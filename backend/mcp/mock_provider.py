import json
from typing import Dict, Any, List
from backend.simulator.telemetry import telemetry_simulator

class MockGrafanaMcpProvider:
    """
    High-fidelity simulation of the official 'grafana/mcp-grafana' MCP server.
    Emulates Prometheus PromQL, Loki LogQL, Dashboard Search, and Alert Rules.
    """

    @staticmethod
    def query_prometheus(query: str) -> Dict[str, Any]:
        """Runs a PromQL query against simulated studio metrics."""
        return telemetry_simulator.generate_promql_query_result(query)

    @staticmethod
    def query_loki(query: str) -> Dict[str, Any]:
        """Runs a LogQL query against simulated studio logs."""
        return telemetry_simulator.generate_loki_query_result(query)

    @staticmethod
    def search_dashboards(query: str = "") -> List[Dict[str, Any]]:
        """Searches Grafana dashboards for film & TV studio pipelines."""
        all_dashboards = [
            {
                "id": 101,
                "uid": "vfx-render-farm-prod",
                "title": "VFX Render Farm - Node Health & Queue Depth",
                "uri": "db/vfx-render-farm-prod",
                "url": "/d/vfx-render-farm-prod/vfx-render-farm-node-health-queue-depth",
                "type": "dash-db",
                "tags": ["vfx", "render-farm", "blender", "gpu", "cinema"],
                "isStarred": True
            },
            {
                "id": 102,
                "uid": "premiere-livestream-health",
                "title": "Live Broadcast Premiere - SRT Ingest & CDN Edge",
                "uri": "db/premiere-livestream-health",
                "url": "/d/premiere-livestream-health/live-broadcast-premiere-srt-ingest-cdn-edge",
                "type": "dash-db",
                "tags": ["broadcast", "livestream", "premiere", "cdn"],
                "isStarred": True
            },
            {
                "id": 103,
                "uid": "mastering-transcode-pipeline",
                "title": "Post-Production Encoding & DCP Mastering Queue",
                "uri": "db/mastering-transcode-pipeline",
                "url": "/d/mastering-transcode-pipeline/post-production-encoding-dcp-mastering-queue",
                "type": "dash-db",
                "tags": ["mastering", "transcode", "dcp", "prores"],
                "isStarred": False
            }
        ]
        if not query:
            return all_dashboards
        q = query.lower()
        return [
            d for d in all_dashboards
            if q in d["title"].lower() or any(q in t.lower() for t in d["tags"])
        ]

    @staticmethod
    def get_dashboard_by_uid(uid: str) -> Dict[str, Any]:
        """Returns details and panels for a given dashboard UID."""
        dashboards = {
            "vfx-render-farm-prod": {
                "dashboard": {
                    "uid": "vfx-render-farm-prod",
                    "title": "VFX Render Farm - Node Health & Queue Depth",
                    "panels": [
                        {"id": 1, "title": "Queue Depth Backlog (Frames)", "type": "timeseries"},
                        {"id": 2, "title": "GPU VRAM Allocation (%)", "type": "gauge"},
                        {"id": 3, "title": "Node Status (Active vs Faulted)", "type": "stat"},
                        {"id": 4, "title": "Frame Render Duration (sec)", "type": "heatmap"}
                    ]
                }
            },
            "premiere-livestream-health": {
                "dashboard": {
                    "uid": "premiere-livestream-health",
                    "title": "Live Broadcast Premiere - SRT Ingest & CDN Edge",
                    "panels": [
                        {"id": 1, "title": "SRT Ingest Bitrate (kbps)", "type": "timeseries"},
                        {"id": 2, "title": "Dropped Frames (%)", "type": "timeseries"},
                        {"id": 3, "title": "Concurrent Viewers", "type": "stat"},
                        {"id": 4, "title": "Audio/Video Drift (ms)", "type": "gauge"}
                    ]
                }
            }
        }
        return dashboards.get(uid, {"error": "Dashboard not found", "uid": uid})

    @staticmethod
    def list_alerts() -> List[Dict[str, Any]]:
        """Returns currently firing and evaluated Grafana alert rules."""
        snapshot = telemetry_simulator.get_snapshot()
        return snapshot["alerts"]

