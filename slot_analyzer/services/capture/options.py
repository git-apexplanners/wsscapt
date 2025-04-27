from dataclasses import dataclass

@dataclass
class Options:
    enabled: bool = True
    interval: int = 60
    tolerance: int = 5
    listen_host: str = "localhost"
    listen_port: int = 8080