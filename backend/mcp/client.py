import asyncio
import json
import logging
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from backend.config import settings
from backend.mcp.mock_provider import MockGrafanaMcpProvider

logger = logging.getLogger(__name__)


class GrafanaMcpClient:
    """
    Real MCP client for the official `grafana/mcp-grafana` server.
    Opens one persistent stdio session for the process lifetime (connect() at
    app startup, close() at shutdown) and dispatches tool calls through the
    Model Context Protocol — not raw REST.

    Falls back to MockGrafanaMcpProvider ONLY if the MCP session cannot be
    established or a call errors out, and always logs a visible warning when
    that happens so fallback use is never silent.
    """

    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None
        self._available_tools: Dict[str, Any] = {}
        self._connected = False
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        if self._connected:
            return

        command = settings.GRAFANA_MCP_COMMAND
        args = settings.GRAFANA_MCP_ARGS.split() if settings.GRAFANA_MCP_ARGS else []
        env = {
            "GRAFANA_URL": settings.GRAFANA_URL or "",
            "GRAFANA_SERVICE_ACCOUNT_TOKEN": settings.GRAFANA_SERVICE_ACCOUNT_TOKEN or "",
        }

        if not command:
            logger.warning(
                "GRAFANA_MCP_COMMAND not set — running in SIMULATION-ONLY mode. "
                "Set it to enable the real MCP connection."
            )
            return

        try:
            server_params = StdioServerParameters(command=command, args=args, env=env)
            self._exit_stack = AsyncExitStack()
            read_stream, write_stream = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self._session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await self._session.initialize()

            tools_result = await self._session.list_tools()
            self._available_tools = {t.name: t for t in tools_result.tools}
            self._connected = True

            logger.info(
                f"GrafanaMcpClient connected via real MCP session. "
                f"Discovered {len(self._available_tools)} tools: "
                f"{list(self._available_tools.keys())}"
            )
        except Exception as exc:
            logger.warning(
                f"Failed to establish a live MCP session ({exc}). "
                f"Falling back to SIMULATION mode for this process lifetime."
            )
            self._connected = False

    async def close(self) -> None:
        if self._exit_stack is not None:
            await self._exit_stack.aclose()
        self._connected = False

    def _resolve_tool_name(self, *candidates: str) -> Optional[str]:
        for candidate in candidates:
            if candidate in self._available_tools:
                return candidate
        for name in self._available_tools:
            if any(c.lower() in name.lower() for c in candidates):
                return name
        return None

    async def _call_tool(self, candidates: List[str], arguments: Dict[str, Any]) -> Any:
        if not self._connected or self._session is None:
            raise RuntimeError("MCP session not connected")

        tool_name = self._resolve_tool_name(*candidates)
        if tool_name is None:
            raise RuntimeError(
                f"No matching tool found among candidates {candidates}. "
                f"Available: {list(self._available_tools.keys())}"
            )

        result = await self._session.call_tool(tool_name, arguments=arguments)
        text_parts = [block.text for block in result.content if hasattr(block, "text")]
        raw = "\n".join(text_parts)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw}

    async def query_prometheus(self, query: str) -> Dict[str, Any]:
        async with self._lock:
            try:
                return await self._call_tool(
                    ["query_prometheus", "query_datasource", "prometheus_query"],
                    {"query": query},
                )
            except Exception as exc:
                logger.warning(f"Live Prometheus MCP call failed ({exc}), using simulation")
                return MockGrafanaMcpProvider.query_prometheus(query)

    async def query_loki(self, query: str) -> Dict[str, Any]:
        async with self._lock:
            try:
                return await self._call_tool(
                    ["query_loki", "query_loki_logs", "loki_query"],
                    {"query": query},
                )
            except Exception as exc:
                logger.warning(f"Live Loki MCP call failed ({exc}), using simulation")
                return MockGrafanaMcpProvider.query_loki(query)

    async def search_dashboards(self, query: str = "") -> List[Dict[str, Any]]:
        async with self._lock:
            try:
                result = await self._call_tool(
                    ["search_dashboards", "find_dashboards"],
                    {"query": query} if query else {},
                )
                return result if isinstance(result, list) else result.get("dashboards", [])
            except Exception as exc:
                logger.warning(f"Live dashboard search MCP call failed ({exc}), using simulation")
                return MockGrafanaMcpProvider.search_dashboards(query)

    async def get_dashboard_by_uid(self, uid: str) -> Dict[str, Any]:
        async with self._lock:
            try:
                return await self._call_tool(
                    ["get_dashboard_by_uid", "get_dashboard"],
                    {"uid": uid},
                )
            except Exception as exc:
                logger.warning(f"Live get_dashboard MCP call failed ({exc}), using simulation")
                return MockGrafanaMcpProvider.get_dashboard_by_uid(uid)

    async def list_alerts(self) -> List[Dict[str, Any]]:
        async with self._lock:
            try:
                result = await self._call_tool(
                    ["list_alert_rules", "list_alerts", "get_alerts"],
                    {},
                )
                return result if isinstance(result, list) else result.get("alerts", [])
            except Exception as exc:
                logger.warning(f"Live alerts MCP call failed ({exc}), using simulation")
                return MockGrafanaMcpProvider.list_alerts()


grafana_mcp = GrafanaMcpClient()
