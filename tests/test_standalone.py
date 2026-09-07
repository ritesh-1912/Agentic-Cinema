import unittest
import json
import asyncio
from backend.simulator.telemetry import StudioTelemetrySimulator
from backend.simulator.exporter import generate_prometheus_metrics_text
from backend.mcp.mock_provider import MockGrafanaMcpProvider
from backend.mcp.client import GrafanaMcpClient
from backend.agent.copilot import StudioOpsCopilot
from backend.agent.tools import query_prometheus, list_alerts, get_cinema_pipeline_snapshot

class TestStudioOps(unittest.TestCase):

    def setUp(self):
        self.sim = StudioTelemetrySimulator()

    def test_telemetry_snapshot(self):
        snapshot = self.sim.get_snapshot()
        self.assertIn("render_farm", snapshot)
        self.assertIn("livestream_premiere", snapshot)
        self.assertIn("encoding_pipeline", snapshot)
        self.assertEqual(snapshot["render_farm"]["total_nodes"], 64)

    def test_scenarios(self):
        # Render farm incident
        self.sim.set_scenario("render_farm_incident")
        snap = self.sim.get_snapshot()
        self.assertEqual(snap["scenario"], "render_farm_incident")
        self.assertGreater(snap["render_farm"]["queue_depth"], 1000)
        self.assertGreaterEqual(len(snap["alerts"]), 1)

        # Livestream incident
        self.sim.set_scenario("livestream_incident")
        snap_live = self.sim.get_snapshot()
        self.assertEqual(snap_live["scenario"], "livestream_incident")
        self.assertGreater(snap_live["livestream_premiere"]["dropped_frames_percent"], 1.0)

    def test_prometheus_exposition(self):
        metrics_text = generate_prometheus_metrics_text()
        self.assertIn("studio_render_queue_depth", metrics_text)
        self.assertIn("studio_livestream_bitrate_kbps", metrics_text)

    def test_mock_mcp_provider(self):
        prom_res = MockGrafanaMcpProvider.query_prometheus("studio_render_queue_depth")
        self.assertEqual(prom_res["status"], "success")

        dashboards = MockGrafanaMcpProvider.search_dashboards("render")
        self.assertGreaterEqual(len(dashboards), 1)

    def test_agent_tools(self):
        q_res = query_prometheus("studio_render_queue_depth")
        self.assertIn("studio_render_queue_depth", q_res)

        alerts_json = list_alerts()
        self.assertTrue(isinstance(alerts_json, str))

        snap_json = get_cinema_pipeline_snapshot()
        self.assertIn("render_farm", snap_json)

    def test_copilot_chat(self):
        copilot = StudioOpsCopilot()
        
        # Test Render Farm question
        resp = asyncio.run(copilot.chat("Why is the overnight render queue backed up?"))
        self.assertIn("answer", resp)
        self.assertIn("PRODUCTION IMPACT STATUS", resp["answer"])
        self.assertGreater(len(resp["tools_executed"]), 0)

        # Test Livestream question
        resp2 = asyncio.run(copilot.chat("Is the premiere livestream healthy right now?"))
        self.assertIn("answer", resp2)
        self.assertTrue("livestream" in resp2["answer"].lower() or "stream" in resp2["answer"].lower())

        # Test Alerts question
        resp3 = asyncio.run(copilot.chat("List all active alerts"))
        self.assertIn("answer", resp3)
        self.assertTrue("alert" in resp3["answer"].lower())

if __name__ == "__main__":
    unittest.main()
