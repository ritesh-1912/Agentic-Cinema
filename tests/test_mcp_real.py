import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp import ClientSession, StdioServerParameters
from backend.mcp.client import GrafanaMcpClient
from backend.config import settings

@pytest.mark.asyncio
async def test_mcp_sdk_imports():
    """Verifies that official Python mcp SDK components are imported and available."""
    assert ClientSession is not None
    assert StdioServerParameters is not None

@pytest.mark.asyncio
async def test_mcp_tool_discovery():
    """
    Tests dynamic MCP tool discovery.
    Simulates a live MCP server response to session.list_tools().
    """
    client = GrafanaMcpClient()
    
    mock_tool1 = MagicMock()
    mock_tool1.name = "query_prometheus"
    mock_tool1.description = "Executes PromQL queries"
    mock_tool2 = MagicMock()
    mock_tool2.name = "list_alerts"
    mock_tool2.description = "Lists firing alert rules"

    mock_tools_result = MagicMock()
    mock_tools_result.tools = [mock_tool1, mock_tool2]

    mock_session = AsyncMock()
    mock_session.list_tools.return_value = mock_tools_result

    with patch.object(client, "_get_mcp_session") as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session
        with patch.object(settings, "GRAFANA_URL", "https://test.grafana.net"):
            with patch.object(settings, "GRAFANA_SERVICE_ACCOUNT_TOKEN", "glsa_test_token"):
                tools = await client.discover_tools()
                assert "query_prometheus" in tools
                assert "list_alerts" in tools
                assert len(tools) == 2

@pytest.mark.asyncio
async def test_mcp_tool_execution_live_and_fallback():
    """
    Tests that calling MCP tools returns parsed data, and gracefully falls back
    to MockGrafanaMcpProvider when the live MCP server is offline.
    """
    client = GrafanaMcpClient()

    # 1. Test fallback when no live server
    res_fallback = await client.query_prometheus("studio_render_queue_depth")
    assert res_fallback["status"] == "success"
    assert "data" in res_fallback

    # 2. Test live MCP tool invocation with mocked session
    mock_session = AsyncMock()
    mock_block = MagicMock()
    mock_block.text = '{"status": "success", "data": {"resultType": "vector", "result": [{"metric": {"__name__": "studio_render_queue_depth"}, "value": [1788800000, "1428"]}]}}'
    mock_call_result = MagicMock()
    mock_call_result.content = [mock_block]
    mock_session.call_tool.return_value = mock_call_result

    with patch.object(client, "_get_mcp_session") as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session
        with patch.object(settings, "GRAFANA_URL", "https://test.grafana.net"):
            with patch.object(settings, "GRAFANA_SERVICE_ACCOUNT_TOKEN", "glsa_test_token"):
                client.discovered_tools = {"query_prometheus": MagicMock()}
                live_res = await client.query_prometheus("studio_render_queue_depth")
                assert live_res["status"] == "success"
                assert live_res["data"]["result"][0]["value"][1] == "1428"
