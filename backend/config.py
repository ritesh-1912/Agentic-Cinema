import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Settings:
    # Google AI Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Grafana Cloud & MCP Configuration
    GRAFANA_URL: Optional[str] = os.getenv("GRAFANA_URL")
    GRAFANA_SERVICE_ACCOUNT_TOKEN: Optional[str] = os.getenv("GRAFANA_SERVICE_ACCOUNT_TOKEN")
    
    # MCP Transport Configuration: 'stdio' (Docker/binary subprocess) or 'sse' (Hosted endpoint)
    GRAFANA_MCP_TRANSPORT: str = os.getenv("GRAFANA_MCP_TRANSPORT", "stdio").lower()
    GRAFANA_MCP_COMMAND: str = os.getenv("GRAFANA_MCP_COMMAND", "docker")
    GRAFANA_MCP_ARGS: Optional[str] = os.getenv("GRAFANA_MCP_ARGS")
    GRAFANA_MCP_SSE_URL: Optional[str] = os.getenv("GRAFANA_MCP_SSE_URL")
    GRAFANA_MCP_TIMEOUT: float = float(os.getenv("GRAFANA_MCP_TIMEOUT", "15.0"))

    # Grafana Cloud Prometheus Push Configuration
    GRAFANA_PROMETHEUS_URL: Optional[str] = os.getenv("GRAFANA_PROMETHEUS_URL")
    GRAFANA_PROMETHEUS_USER: Optional[str] = os.getenv("GRAFANA_PROMETHEUS_USER")
    GRAFANA_PROMETHEUS_TOKEN: Optional[str] = os.getenv("GRAFANA_PROMETHEUS_TOKEN")

    # Server Settings
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    SIMULATOR_TICK_SECONDS: float = float(os.getenv("SIMULATOR_TICK_SECONDS", "2.0"))

    @property
    def has_grafana_credentials(self) -> bool:
        return bool((self.GRAFANA_URL and self.GRAFANA_SERVICE_ACCOUNT_TOKEN) or self.GRAFANA_MCP_SSE_URL)

    @property
    def has_gemini_credentials(self) -> bool:
        return bool(self.GEMINI_API_KEY)

settings = Settings()
