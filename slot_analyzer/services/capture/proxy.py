"""
Proxy management module for intercepting network traffic.
"""
from pathlib import Path
import asyncio
from typing import Callable, Dict, Optional
import ssl
from datetime import datetime

from mitmproxy import ctx, options
from mitmproxy.tools import dump
from mitmproxy import proxy
from OpenSSL import crypto
from loguru import logger

from slot_analyzer.errors import ProxyError
from slot_analyzer.config import settings

class CertificateManager:
    """Handles SSL certificate generation and management"""
    
    def __init__(self, cert_dir: Path):
        self.cert_dir = cert_dir
        self.cert_dir.mkdir(parents=True, exist_ok=True)
        self.ca_cert_path = self.cert_dir / "mitmproxy-ca.pem"
        self.ca_key_path = self.cert_dir / "mitmproxy-ca.key"

    def generate_ca_cert(self) -> None:
        """Generate a new CA certificate if it doesn't exist"""
        if self.ca_cert_path.exists() and self.ca_key_path.exists():
            return

        # Generate key
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        # Generate certificate
        cert = crypto.X509()
        cert.get_subject().CN = "Slot Analyzer Root CA"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(315360000)  # Valid for 10 years
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')

        # Save certificate and private key
        with open(self.ca_cert_path, "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(self.ca_key_path, "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

        logger.info(f"Generated new CA certificate at {self.ca_cert_path}")

class MitmproxyController(dump.DumpMaster):
    """Custom mitmproxy controller for handling traffic"""

    def __init__(self, opts: options.Options):
        super().__init__(opts)
        self._request_handler: Optional[Callable] = None
        self._response_handler: Optional[Callable] = None
        self._websocket_handler: Optional[Callable] = None

    def set_handlers(self,
                    request_handler: Callable,
                    response_handler: Callable,
                    websocket_handler: Callable):
        """Set callback handlers for different types of traffic"""
        self._request_handler = request_handler
        self._response_handler = response_handler
        self._websocket_handler = websocket_handler

    def request(self, flow):
        """Process intercepted requests"""
        if self._request_handler:
            request_data = {
                "method": flow.request.method,
                "url": flow.request.pretty_url,
                "headers": dict(flow.request.headers),
                "content": flow.request.content.decode('utf-8', 'ignore'),
                "timestamp": datetime.now().isoformat()
            }
            asyncio.create_task(self._request_handler(request_data))

    def response(self, flow):
        """Process intercepted responses"""
        if self._response_handler:
            response_data = {
                "status_code": flow.response.status_code,
                "headers": dict(flow.response.headers),
                "content": flow.response.content.decode('utf-8', 'ignore'),
                "timestamp": datetime.now().isoformat()
            }
            asyncio.create_task(self._response_handler(response_data))

    def websocket_message(self, flow):
        """Process WebSocket messages"""
        if self._websocket_handler and flow.websocket:
            for message in flow.websocket.messages:
                websocket_data = {
                    "type": "send" if message.from_client else "receive",
                    "content": message.content.decode('utf-8', 'ignore'),
                    "timestamp": datetime.now().isoformat()
                }
                asyncio.create_task(self._websocket_handler(websocket_data))

class ProxyManager:
    """Manages the mitmproxy instance for traffic interception"""

    def __init__(self):
        self.cert_manager = CertificateManager(settings.CERT_DIR)
        self.proxy_port = settings.PROXY_PORT
        self.proxy_host = settings.PROXY_HOST
        self._controller: Optional[MitmproxyController] = None
        self._request_handler: Optional[Callable] = None
        self._response_handler: Optional[Callable] = None
        self._websocket_handler: Optional[Callable] = None

    def on_request(self, handler: Callable[[Dict], None]):
        """Register request handler"""
        self._request_handler = handler

    def on_response(self, handler: Callable[[Dict], None]):
        """Register response handler"""
        self._response_handler = handler

    def on_websocket(self, handler: Callable[[Dict], None]):
        """Register WebSocket handler"""
        self._websocket_handler = handler

    async def start(self):
        """Start the proxy server"""
        try:
            # Ensure CA certificate exists
            self.cert_manager.generate_ca_cert()

            # Configure mitmproxy options
            opts = Options(
                listen_host=self.proxy_host,
                listen_port=self.proxy_port,
                ssl_insecure=True,  # Accept invalid certificates
                cadir=str(self.cert_manager.cert_dir)
            )

            # Initialize proxy server
            opts.mode = ["regular"]  # Regular proxy mode
            self._controller = MitmproxyController(opts)
            self._controller.server = proxy.server.ProxyServer(opts)

            # Set up handlers
            self._controller.set_handlers(
                self._request_handler,
                self._response_handler,
                self._websocket_handler
            )

            logger.info(f"Started proxy server on {self.proxy_host}:{self.proxy_port}")

        except Exception as e:
            logger.error(f"Failed to start proxy: {str(e)}")
            raise ProxyError(f"Failed to start proxy: {str(e)}")

    async def stop(self):
        """Stop the proxy server"""
        if self._controller:
            try:
                await self._controller.shutdown()
                self._controller = None
                logger.info("Proxy server stopped")
            except Exception as e:
                logger.error(f"Error stopping proxy: {str(e)}")
                raise ProxyError(f"Failed to stop proxy: {str(e)}")