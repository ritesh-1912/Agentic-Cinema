import json
from typing import Dict, Any, List
from backend.mcp.client import grafana_mcp
from backend.simulator.telemetry import telemetry_simulator

async def query_prometheus(query: str = "", *args, **kwargs) -> str:
    """
    Executes a PromQL query via the Grafana MCP server to retrieve metrics.
    
    Args:
        query: PromQL query expression (e.g. 'studio_render_queue_depth', 'studio_gpu_vram_usage_percent', 'studio_livestream_bitrate_kbps').
    
    Returns:
        JSON string containing the metric query results from Grafana.
    """
    if not query and args:
        query = str(args[0])
    return json.dumps(await grafana_mcp.query_prometheus(query))

async def query_loki(query: str = "", *args, **kwargs) -> str:
    """
    Executes a LogQL query via the Grafana MCP server to inspect production logs.
    
    Args:
        query: LogQL query string (e.g. '{app="studio-pipeline"} |= "CUDA"').
    
    Returns:
        JSON string containing the matching log streams and error entries.
    """
    if not query and args:
        query = str(args[0])
    return json.dumps(await grafana_mcp.query_loki(query))

async def list_alerts(*args, **kwargs) -> str:
    """
    Lists active firing and pending alerts configured in Grafana Alertmanager.
    
    Returns:
        JSON string with list of firing alerts, affected pipeline stage, severity, and details.
    """
    return json.dumps(await grafana_mcp.list_alerts())

async def search_dashboards(query: str = "", *args, **kwargs) -> str:
    """
    Searches available Grafana monitoring dashboards for studio pipelines.
    
    Args:
        query: Search string to filter dashboards (e.g. 'render', 'livestream', 'transcode').
    
    Returns:
        JSON string listing dashboard titles, UIDs, and tags.
    """
    if not query and args:
        query = str(args[0])
    return json.dumps(await grafana_mcp.search_dashboards(query))

async def get_cinema_pipeline_snapshot(*args, **kwargs) -> str:
    """
    Retrieves a real-time consolidated health snapshot across all studio pipelines:
    VFX Render Farm, 4K/8K Transcode Pipeline, and Live Premiere Broadcast.
    
    Returns:
        JSON string with high-level metrics, active project/shot, and active alerts.
    """
    result = telemetry_simulator.get_snapshot()
    return json.dumps(result, indent=2)

STUDIO_TOOLS = [
    query_prometheus,
    query_loki,
    list_alerts,
    search_dashboards,
    get_cinema_pipeline_snapshot
]

TOOL_NAME_TO_FUNCTION = {
    "query_prometheus": query_prometheus,
    "query_loki": query_loki,
    "list_alerts": list_alerts,
    "search_dashboards": search_dashboards,
    "get_cinema_pipeline_snapshot": get_cinema_pipeline_snapshot,
}
