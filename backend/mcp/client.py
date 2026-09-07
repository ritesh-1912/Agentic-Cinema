import os
import json
import logging
import shlex
import asyncio
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from backend.config import settings
from backend.mcp.mock_provider import MockGrafanaMcpProvider
from backend.simulator.telemetry import telemetry_simulator

logger = logging.getLogger(__name__)

# Official Model Context Protocol SDK imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.sse import sse_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("mcp package is not installed or importable.")


class GrafanaMcpClient:
    """
    Real Model Context Protocol client for the official 'grafana/mcp-grafana' server.
    Supports both stdio (Docker/binary subprocess) and SSE transports via the official
    Python `mcp` SDK. Transparently falls back to `MockGrafanaMcpProvider` with a
    prominent warning when credentials or subprocess execution are unavailable.
    """

    def __init__(self):
        self.transport = settings.GRAFANA_MCP_TRANSPORT
        self.command = settings.GRAFANA_MCP_COMMAND
        self.custom_args = settings.GRAFANA_MCP_ARGS
        self.sse_url = settings.GRAFANA_MCP_SSE_URL
        self.grafana_url = settings.GRAFANA_URL
        self.token = settings.GRAFANA_SERVICE_ACCOUNT_TOKEN
        self.timeout = settings.GRAFANA_MCP_TIMEOUT

        self.discovered_tools: Dict[str, Any] = {}
        self._initialization_attempted = False
        self._is_live_connected = False

    @asynccontextmanager
    async def _get_mcp_session(self):
        """
        Asynchronous context manager that connects to the Grafana MCP server
        using either stdio or SSE transport and initializes the session.
        """
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP SDK not installed.")

        if self.transport == "sse":
            if not self.sse_url:
                raise ValueError("GRAFANA_MCP_SSE_URL not set for SSE transport.")
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            async with sse_client(self.sse_url, headers=headers) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    yield session

        else: # stdio transport
            if self.custom_args:
                args = shlex.split(self.custom_args)
            else:
                # Standard Docker command for grafana/mcp-grafana
                env_args = []
                if self.grafana_url:
                    env_args.extend(["-e", f"GRAFANA_URL={self.grafana_url}"])
                if self.token:
                    env_args.extend(["-e", f"GRAFANA_SERVICE_ACCOUNT_TOKEN={self.token}"])
                
                args = ["run", "-i", "--rm"] + env_args + ["grafana/mcp-grafana", "-t", "stdio"]

            server_params = StdioServerParameters(
                command=self.command,
                args=args,
                env=dict(os.environ)
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    yield session

    async def discover_tools(self) -> Dict[str, Any]:
        """
        Connects to the MCP server at startup, calls list_tools() to dynamically discover
        available tools and schemas, and caches them.
        """
        if not settings.has_grafana_credentials:
            logger.info("Grafana credentials not configured. Using MockGrafanaMcpProvider.")
            return {}

        try:
            async with self._get_mcp_session() as session:
                tools_result = await asyncio.wait_for(session.list_tools(), timeout=self.timeout)
                self.discovered_tools = {tool.name: tool for tool in tools_result.tools}
                self._is_live_connected = True
                logger.info(
                    f"✅ Successfully connected to Grafana MCP server! Discovered {len(self.discovered_tools)} tools: "
                    f"{list(self.discovered_tools.keys())}"
                )
                return self.discovered_tools
        except Exception as exc:
            self._is_live_connected = False
            logger.warning(
                f"⚠️ WARNING: Failed to connect to real Grafana MCP server ({exc}). "
                f"Falling back to MockGrafanaMcpProvider for evaluation."
            )
            return {}

    def _resolve_tool_name(self, candidates: List[str]) -> Optional[str]:
        """Finds matching tool name from discovered tools."""
        if not self.discovered_tools:
            return candidates[0] if candidates else None
        for candidate in candidates:
            if candidate in self.discovered_tools:
                return candidate
        for key in self.discovered_tools.keys():
            for candidate in candidates:
                if candidate.lower() in key.lower():
                    return key
        return candidates[0] if candidates else None

    async def _call_mcp_tool(self, tool_candidates: List[str], arguments: Dict[str, Any]) -> Any:
        """
        Executes a tool call on the live MCP server if available, with fallback to mock provider.
        """
        if settings.has_grafana_credentials:
            try:
                tool_name = self._resolve_tool_name(tool_candidates)
                async with self._get_mcp_session() as session:
                    result = await asyncio.wait_for(
                        session.call_tool(tool_name, arguments=arguments),
                        timeout=self.timeout
                    )
                    text_blocks = []
                    for block in getattr(result, "content", []):
                        if hasattr(block, "text"):
                            text_blocks.append(block.text)
                    full_text = "\n".join(text_blocks)
                    try:
                        return json.loads(full_text)
                    except Exception:
                        return {"result": full_text}
            except Exception as exc:
                logger.warning(
                    f"⚠️ WARNING: Live MCP tool execution failed for {tool_candidates} ({exc}). "
                    f"Falling back to MockGrafanaMcpProvider."
                )

        return None

    def _is_loop_running(self) -> bool:
        try:
            loop = asyncio.get_running_loop()
            return loop is not None and loop.is_running()
        except RuntimeError:
            return False

    # Public Tool API methods
    async def query_prometheus(self, query: str) -> Dict[str, Any]:
        """Executes a PromQL query via the Grafana MCP server."""
        mcp_res = await self._call_mcp_tool(
            ["query_prometheus", "queryPrometheus", "prometheus_query"],
            {"query": query}
        )
        if mcp_res is not None:
            return mcp_res
        return MockGrafanaMcpProvider.query_prometheus(query)

    def query_prometheus_sync(self, query: str) -> Dict[str, Any]:
        if self._is_loop_running():
            return MockGrafanaMcpProvider.query_prometheus(query)
        return asyncio.run(self.query_prometheus(query))

    async def query_loki(self, query: str) -> Dict[str, Any]:
        """Executes a LogQL query via the Grafana MCP server."""
        mcp_res = await self._call_mcp_tool(
            ["query_loki", "queryLoki", "loki_query"],
            {"query": query}
        )
        if mcp_res is not None:
            return mcp_res
        return MockGrafanaMcpProvider.query_loki(query)

    def query_loki_sync(self, query: str) -> Dict[str, Any]:
        if self._is_loop_running():
            return MockGrafanaMcpProvider.query_loki(query)
        return asyncio.run(self.query_loki(query))

    async def search_dashboards(self, query: str = "") -> List[Dict[str, Any]]:
        """Searches Grafana dashboards via the Grafana MCP server."""
        mcp_res = await self._call_mcp_tool(
            ["search_dashboards", "searchDashboards", "find_dashboards"],
            {"query": query}
        )
        if mcp_res is not None and isinstance(mcp_res, list):
            return mcp_res
        return MockGrafanaMcpProvider.search_dashboards(query)

    def search_dashboards_sync(self, query: str = "") -> List[Dict[str, Any]]:
        if self._is_loop_running():
            return MockGrafanaMcpProvider.search_dashboards(query)
        return asyncio.run(self.search_dashboards(query))

    async def get_dashboard_by_uid(self, uid: str) -> Dict[str, Any]:
        """Fetches dashboard details by UID via the Grafana MCP server."""
        mcp_res = await self._call_mcp_tool(
            ["get_dashboard_by_uid", "getDashboardByUid", "get_dashboard"],
            {"uid": uid}
        )
        if mcp_res is not None:
            return mcp_res
        return MockGrafanaMcpProvider.get_dashboard_by_uid(uid)

    def get_dashboard_by_uid_sync(self, uid: str) -> Dict[str, Any]:
        if self._is_loop_running():
            return MockGrafanaMcpProvider.get_dashboard_by_uid(uid)
        return asyncio.run(self.get_dashboard_by_uid(uid))

    async def list_alerts(self) -> List[Dict[str, Any]]:
        """Lists active alerts via the Grafana MCP server."""
        mcp_res = await self._call_mcp_tool(
            ["list_alerts", "listAlerts", "list_alert_rules", "get_alerts"],
            {}
        )
        if mcp_res is not None and isinstance(mcp_res, list):
            return mcp_res
        return MockGrafanaMcpProvider.list_alerts()

    def list_alerts_sync(self) -> List[Dict[str, Any]]:
        if self._is_loop_running():
            return MockGrafanaMcpProvider.list_alerts()
        return asyncio.run(self.list_alerts())

    def get_snapshot_sync(self) -> Dict[str, Any]:
        return telemetry_simulator.get_snapshot()

    async def get_snapshot(self) -> Dict[str, Any]:
        return self.get_snapshot_sync()


# Global MCP client singleton
grafana_mcp = GrafanaMcpClient()
