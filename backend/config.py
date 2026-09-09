import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Settings:
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    raw_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    GEMINI_MODEL: str = "gemini-flash-latest" if ("2.5" in raw_model or "3.5" in raw_model) else raw_model

    # Grafana Cloud & MCP Configuration
    GRAFANA_URL: Optional[str] = os.getenv("GRAFANA_URL")
    GRAFANA_SERVICE_ACCOUNT_TOKEN: Optional[str] = os.getenv("GRAFANA_SERVICE_ACCOUNT_TOKEN")
    
    # Grafana MCP server settings
    GRAFANA_MCP_SSE_URL: Optional[str] = os.getenv("GRAFANA_MCP_SSE_URL")
    GRAFANA_MCP_COMMAND: str = os.getenv(
        "GRAFANA_MCP_COMMAND",
        "/usr/local/bin/mcp-grafana" if os.path.exists("/usr/local/bin/mcp-grafana") else ""
    )
    GRAFANA_MCP_ARGS: str = os.getenv("GRAFANA_MCP_ARGS", "")

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
        return bool(self.GRAFANA_URL and self.GRAFANA_SERVICE_ACCOUNT_TOKEN)

    @property
    def has_gemini_credentials(self) -> bool:
        return bool(self.GEMINI_API_KEY)

settings = Settings()
