import pytest
from backend.simulator.telemetry import StudioTelemetrySimulator

def test_telemetry_snapshot_structure():
    sim = StudioTelemetrySimulator()
    snapshot = sim.get_snapshot()
    
    assert "timestamp" in snapshot
    assert "render_farm" in snapshot
    assert "encoding_pipeline" in snapshot
    assert "livestream_premiere" in snapshot
    assert "alerts" in snapshot

    rf = snapshot["render_farm"]
    assert rf["total_nodes"] == 64
    assert rf["active_nodes"] > 0
    assert rf["queue_depth"] > 0

def test_scenario_switching():
    sim = StudioTelemetrySimulator()
    
    # Test render farm incident
    sim.set_scenario("render_farm_incident")
    snap_rf = sim.get_snapshot()
    assert snap_rf["scenario"] == "render_farm_incident"
    assert snap_rf["render_farm"]["queue_depth"] > 1000
    assert len(snap_rf["alerts"]) >= 1

    # Test livestream incident
    sim.set_scenario("livestream_incident")
    snap_live = sim.get_snapshot()
    assert snap_live["scenario"] == "livestream_incident"
    assert snap_live["livestream_premiere"]["dropped_frames_percent"] > 1.0
    assert snap_live["livestream_premiere"]["ingest_bitrate_kbps"] < 10000

    # Test all nominal
    sim.set_scenario("all_nominal")
    snap_nom = sim.get_snapshot()
    assert snap_nom["render_farm"]["faulted_nodes"] == 2
    assert snap_nom["livestream_premiere"]["stream_status"] == "ONLINE"

def test_promql_simulation():
    sim = StudioTelemetrySimulator()
    sim.set_scenario("render_farm_incident")
    
    res = sim.generate_promql_query_result("studio_render_queue_depth")
    assert res["status"] == "success"
    assert "result" in res["data"]
    assert len(res["data"]["result"]) > 0

def test_loki_simulation():
    sim = StudioTelemetrySimulator()
    sim.set_scenario("render_farm_incident")
    
    res = sim.generate_loki_query_result('{app="studio-pipeline"} |= "CUDA"')
    assert res["status"] == "success"
    assert "streams" in res["data"]["resultType"]
