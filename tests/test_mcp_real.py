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
async def test_mcp_connect_and_tool_discovery():
    """
    Tests MCP connect() and list_tools() dynamic tool discovery.
    """
    client = GrafanaMcpClient()
    
    mock_tool1 = MagicMock()
    mock_tool1.name = "query_prometheus"
    mock_tool2 = MagicMock()
    mock_tool2.name = "list_alert_rules"

    mock_tools_result = MagicMock()
    mock_tools_result.tools = [mock_tool1, mock_tool2]

    mock_session = AsyncMock()
    mock_session.list_tools.return_value = mock_tools_result

    with patch("backend.mcp.client.stdio_client") as mock_stdio:
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        with patch("backend.mcp.client.ClientSession") as mock_cls_session:
            mock_cls_session.return_value.__aenter__.return_value = mock_session
            with patch.object(settings, "GRAFANA_MCP_COMMAND", "docker"):
                with patch.object(settings, "GRAFANA_MCP_ARGS", "run -i --rm grafana/mcp-grafana -t stdio"):
                    await client.connect()
                    assert client._connected is True
                    assert "query_prometheus" in client._available_tools
                    assert "list_alert_rules" in client._available_tools
                    await client.close()
                    assert client._connected is False

@pytest.mark.asyncio
async def test_mcp_tool_execution_live_and_fallback():
    """
    Tests that calling MCP tools dispatches via call_tool when connected,
    and falls back to MockGrafanaMcpProvider when disconnected.
    """
    client = GrafanaMcpClient()

    # 1. Fallback when disconnected
    assert client._connected is False
    res_fallback = await client.query_prometheus("studio_render_queue_depth")
    assert res_fallback["status"] == "success"
    assert "data" in res_fallback

    # 2. Live dispatch via call_tool
    mock_session = AsyncMock()
    mock_block = MagicMock()
    mock_block.text = '{"status": "success", "data": {"resultType": "vector", "result": [{"metric": {"__name__": "studio_render_queue_depth"}, "value": [1788800000, "1428"]}]}}'
    mock_call_result = MagicMock()
    mock_call_result.content = [mock_block]
    mock_session.call_tool.return_value = mock_call_result

    client._session = mock_session
    client._connected = True
    client._available_tools = {"query_prometheus": MagicMock()}

    res_live = await client.query_prometheus("studio_render_queue_depth")
    assert res_live["status"] == "success"
    assert res_live["data"]["result"][0]["value"][1] == "1428"


@pytest.mark.asyncio
async def test_mcp_connect_via_sse():
    """
    Tests MCP connect() via SSE endpoint (Option A).
    """
    client = GrafanaMcpClient()

    mock_tool = MagicMock()
    mock_tool.name = "query_prometheus"
    mock_tools_result = MagicMock()
    mock_tools_result.tools = [mock_tool]

    mock_session = AsyncMock()
    mock_session.list_tools.return_value = mock_tools_result

    with patch("backend.mcp.client.sse_client") as mock_sse:
        mock_sse.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        with patch("backend.mcp.client.ClientSession") as mock_cls_session:
            mock_cls_session.return_value.__aenter__.return_value = mock_session
            with patch.object(settings, "GRAFANA_MCP_SSE_URL", "https://test-instance.grafana.net/mcp"):
                await client.connect()
                assert client._connected is True
                assert "query_prometheus" in client._available_tools
                await client.close()
                assert client._connected is False
