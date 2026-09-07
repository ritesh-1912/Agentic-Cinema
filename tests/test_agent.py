import pytest
import asyncio
from backend.agent.copilot import StudioOpsCopilot
from backend.agent.tools import query_prometheus, list_alerts, get_cinema_pipeline_snapshot

def test_tool_invocations():
    q_res = query_prometheus("studio_render_queue_depth")
    assert "studio_render_queue_depth" in q_res

    alerts_res = list_alerts()
    assert isinstance(alerts_res, str)

    snap_res = get_cinema_pipeline_snapshot()
    assert "render_farm" in snap_res

@pytest.mark.asyncio
async def test_copilot_chat_render_farm():
    copilot = StudioOpsCopilot()
    resp = await copilot.chat("Why is the overnight render queue backed up?")
    
    assert "answer" in resp
    assert "tools_executed" in resp
    assert "PRODUCTION IMPACT STATUS" in resp["answer"]
    assert len(resp["tools_executed"]) > 0

@pytest.mark.asyncio
async def test_copilot_chat_livestream():
    copilot = StudioOpsCopilot()
    resp = await copilot.chat("Is the premiere livestream healthy right now?")
    
    assert "answer" in resp
    assert "livestream" in resp["answer"].lower() or "stream" in resp["answer"].lower()

@pytest.mark.asyncio
async def test_copilot_chat_alerts():
    copilot = StudioOpsCopilot()
    resp = await copilot.chat("List active firing alerts")
    
    assert "answer" in resp
    assert "alert" in resp["answer"].lower()
