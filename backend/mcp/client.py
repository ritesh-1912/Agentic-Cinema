import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.mcp.mock_provider import MockGrafanaMcpProvider
from backend.simulator.telemetry import telemetry_simulator

logger = logging.getLogger(__name__)

class GrafanaMcpClient:
    """
    Client for interacting with the Grafana Cloud MCP server (`grafana/mcp-grafana`)
    or native Grafana REST/Datasource endpoints with seamless fallback to high-fidelity
    simulation for testing and evaluation environments.
    """

    def __init__(self):
        self.grafana_url = settings.GRAFANA_URL.rstrip("/") if settings.GRAFANA_URL else None
        self.token = settings.GRAFANA_SERVICE_ACCOUNT_TOKEN
        self.use_live = bool(self.grafana_url and self.token)
        if self.use_live:
            logger.info(f"GrafanaMcpClient initialized with LIVE endpoint: {self.grafana_url}")
        else:
            logger.info("GrafanaMcpClient initialized with HIGH-FIDELITY MCP SIMULATION provider")

    def _http_get_sync(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous authenticated HTTP GET request."""
        query_str = ""
        if params:
            import urllib.parse
            query_str = "?" + urllib.parse.urlencode(params)
        url = f"{self.grafana_url}{path}{query_str}"
        
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)

    def query_prometheus_sync(self, query: str) -> Dict[str, Any]:
        if self.use_live:
            try:
                path = "/api/datasources/proxy/1/api/v1/query"
                return self._http_get_sync(path, params={"query": query})
            except Exception as exc:
                logger.warning(f"Live Prometheus query failed ({exc}), using simulation")
        return MockGrafanaMcpProvider.query_prometheus(query)

    async def query_prometheus(self, query: str) -> Dict[str, Any]:
        return self.query_prometheus_sync(query)

    def query_loki_sync(self, query: str) -> Dict[str, Any]:
        if self.use_live:
            try:
                path = "/api/datasources/proxy/2/loki/api/v1/query"
                return self._http_get_sync(path, params={"query": query})
            except Exception as exc:
                logger.warning(f"Live Loki query failed ({exc}), using simulation")
        return MockGrafanaMcpProvider.query_loki(query)

    async def query_loki(self, query: str) -> Dict[str, Any]:
        return self.query_loki_sync(query)

    def search_dashboards_sync(self, query: str = "") -> List[Dict[str, Any]]:
        if self.use_live:
            try:
                path = "/api/search"
                params = {"query": query, "type": "dash-db"} if query else {"type": "dash-db"}
                return self._http_get_sync(path, params=params)
            except Exception as exc:
                logger.warning(f"Live search failed ({exc}), using simulation")
        return MockGrafanaMcpProvider.search_dashboards(query)

    async def search_dashboards(self, query: str = "") -> List[Dict[str, Any]]:
        return self.search_dashboards_sync(query)

    def get_dashboard_by_uid_sync(self, uid: str) -> Dict[str, Any]:
        if self.use_live:
            try:
                path = f"/api/dashboards/uid/{uid}"
                return self._http_get_sync(path)
            except Exception as exc:
                logger.warning(f"Live get_dashboard failed ({exc}), using simulation")
        return MockGrafanaMcpProvider.get_dashboard_by_uid(uid)

    async def get_dashboard_by_uid(self, uid: str) -> Dict[str, Any]:
        return self.get_dashboard_by_uid_sync(uid)

    def list_alerts_sync(self) -> List[Dict[str, Any]]:
        if self.use_live:
            try:
                path = "/api/v1/provisioning/alert-rules"
                return self._http_get_sync(path)
            except Exception as exc:
                logger.warning(f"Live alerts failed ({exc}), using simulation")
        return MockGrafanaMcpProvider.list_alerts()

    async def list_alerts(self) -> List[Dict[str, Any]]:
        return self.list_alerts_sync()

    def get_snapshot_sync(self) -> Dict[str, Any]:
        return telemetry_simulator.get_snapshot()

    async def get_snapshot(self) -> Dict[str, Any]:
        return self.get_snapshot_sync()

# Global MCP client singleton
grafana_mcp = GrafanaMcpClient()
