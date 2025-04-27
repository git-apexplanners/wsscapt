"""Command-line interface for the Slot Game Analyzer."""

import sys
import signal
import click
from typing import Optional

from slot_analyzer.config import settings
from slot_analyzer.log_utils import get_logger
from slot_analyzer.services import ServiceRegistry, health_service
from slot_analyzer.message_broker import message_queue

logger = get_logger(__name__)

def handle_shutdown(signal_num: int, frame: Optional[object]) -> None:
    """Handle application shutdown gracefully."""
    logger.info("Shutting down application...")
    
    try:
        # Cleanup services
        ServiceRegistry.cleanup()
        
        # Close message queue connection
        message_queue.close()
        
        logger.info("Shutdown complete")
        sys.exit(0)
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))
        sys.exit(1)

# Register shutdown handlers
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

@click.group()
@click.version_option(version=settings.APP_VERSION)
def cli() -> None:
    """Slot Game Analyzer CLI."""
    pass

@cli.command()
def health() -> None:
    """Check system health."""
    try:
        result = health_service.check_health()
        if result["status"] == "healthy":
            click.echo(click.style("System is healthy", fg="green"))
            for component, status in result["components"].items():
                click.echo(f"  {component}: {status}")
        else:
            click.echo(click.style("System is unhealthy", fg="red"))
            click.echo(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Error checking health: {str(e)}", fg="red"))
        sys.exit(1)

@cli.command()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode"
)
def start(debug: bool) -> None:
    """Start the Slot Game Analyzer."""
    try:
        if debug:
            settings.DEBUG = True
            click.echo("Debug mode enabled")
        
        click.echo(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        click.echo("Press Ctrl+C to stop")
        
        # Verify system health before starting
        health_result = health_service.check_health()
        if health_result["status"] != "healthy":
            raise click.ClickException("System health check failed")
            
        # Main application loop
        while True:
            signal.pause()
            
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        sys.exit(1)

def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        click.echo(click.style(f"Fatal error: {str(e)}", fg="red"))
        sys.exit(1)

if __name__ == "__main__":
    main()
