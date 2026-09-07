import json
from typing import Dict, Any, List
from backend.mcp.client import grafana_mcp

def query_prometheus(query: str) -> str:
    """
    Executes a PromQL query via the Grafana MCP server to retrieve metrics.
    
    Args:
        query: PromQL query expression (e.g. 'studio_render_queue_depth', 'studio_gpu_vram_usage_percent', 'studio_livestream_bitrate_kbps').
    
    Returns:
        JSON string containing the metric query results from Grafana.
    """
    res = grafana_mcp.query_prometheus_sync(query)
    return json.dumps(res, indent=2)


def query_loki(query: str) -> str:
    """
    Executes a LogQL query via the Grafana MCP server to inspect production logs.
    
    Args:
        query: LogQL query string (e.g. '{app="studio-pipeline"} |= "CUDA"').
    
    Returns:
        JSON string containing the matching log streams and error entries.
    """
    res = grafana_mcp.query_loki_sync(query)
    return json.dumps(res, indent=2)


def search_dashboards(query: str = "") -> str:
    """
    Searches available Grafana monitoring dashboards for studio pipelines.
    
    Args:
        query: Search string to filter dashboards (e.g. 'render', 'livestream', 'transcode').
    
    Returns:
        JSON string listing dashboard titles, UIDs, and tags.
    """
    res = grafana_mcp.search_dashboards_sync(query)
    return json.dumps(res, indent=2)


def list_alerts() -> str:
    """
    Lists active firing and pending alerts configured in Grafana Alertmanager.
    
    Returns:
        JSON string with list of firing alerts, affected pipeline stage, severity, and details.
    """
    res = grafana_mcp.list_alerts_sync()
    return json.dumps(res, indent=2)


def get_cinema_pipeline_snapshot() -> str:
    """
    Retrieves a real-time consolidated health snapshot across all studio pipelines:
    VFX Render Farm, 4K/8K Transcode Pipeline, and Live Premiere Broadcast.
    
    Returns:
        JSON string with high-level metrics, active project/shot, and active alerts.
    """
    res = grafana_mcp.get_snapshot_sync()
    return json.dumps(res, indent=2)


STUDIO_TOOLS = [
    query_prometheus,
    query_loki,
    search_dashboards,
    list_alerts,
    get_cinema_pipeline_snapshot
]
