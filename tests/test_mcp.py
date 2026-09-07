import pytest
import asyncio
from backend.mcp.mock_provider import MockGrafanaMcpProvider
from backend.mcp.client import GrafanaMcpClient

def test_mock_provider_promql():
    res = MockGrafanaMcpProvider.query_prometheus("studio_render_queue_depth")
    assert res["status"] == "success"
    assert "data" in res

def test_mock_provider_dashboards():
    dashboards = MockGrafanaMcpProvider.search_dashboards("render")
    assert len(dashboards) >= 1
    assert "vfx" in dashboards[0]["tags"]

def test_mock_provider_alerts():
    alerts = MockGrafanaMcpProvider.list_alerts()
    assert isinstance(alerts, list)

@pytest.mark.asyncio
async def test_mcp_client_methods():
    client = GrafanaMcpClient()
    res = await client.query_prometheus("studio_render_queue_depth")
    assert res["status"] == "success"

    alerts = await client.list_alerts()
    assert isinstance(alerts, list)

    dashboards = await client.search_dashboards()
    assert len(dashboards) >= 1
