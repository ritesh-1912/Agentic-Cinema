import time
import logging
from typing import Optional
from backend.simulator.telemetry import telemetry_simulator

logger = logging.getLogger(__name__)

def generate_prometheus_metrics_text() -> str:
    """
    Generates Prometheus exposition format text for studio pipeline metrics.
    Can be scraped by Prometheus or Grafana Agent/Alloy.
    """
    snapshot = telemetry_simulator.get_snapshot()
    rf = snapshot["render_farm"]
    enc = snapshot["encoding_pipeline"]
    live = snapshot["livestream_premiere"]

    lines = [
        "# HELP studio_render_queue_depth Total number of frames queued for VFX rendering",
        "# TYPE studio_render_queue_depth gauge",
        f'studio_render_queue_depth{{project="Chronos",sequence="SQ_14"}} {rf["queue_depth"]}',
        "",
        "# HELP studio_render_active_nodes Number of operational GPU render farm nodes",
        "# TYPE studio_render_active_nodes gauge",
        f'studio_render_active_nodes{{cluster="render-farm-west"}} {rf["active_nodes"]}',
        "",
        "# HELP studio_render_faulted_nodes Number of faulted/unresponsive GPU render farm nodes",
        "# TYPE studio_render_faulted_nodes gauge",
        f'studio_render_faulted_nodes{{cluster="render-farm-west"}} {rf["faulted_nodes"]}',
        "",
        "# HELP studio_render_gpu_vram_usage_percent Average GPU VRAM usage percentage across worker pool",
        "# TYPE studio_render_gpu_vram_usage_percent gauge",
        f'studio_render_gpu_vram_usage_percent{{node_pool="worker-pool-b"}} {rf["gpu_vram_usage_percent"]:.2f}',
        "",
        "# HELP studio_render_failed_jobs_total Number of failed render jobs in the last hour",
        "# TYPE studio_render_failed_jobs_total gauge",
        f'studio_render_failed_jobs_total{{shot="{rf["active_shot"]}"}} {rf["failed_jobs_last_hour"]}',
        "",
        "# HELP studio_transcode_queue_length Length of active video transcode queue",
        "# TYPE studio_transcode_queue_length gauge",
        f'studio_transcode_queue_length{{format="DCP_4K"}} {enc["transcode_queue_length"]}',
        "",
        "# HELP studio_transcode_error_rate Transcode error rate percentage",
        "# TYPE studio_transcode_error_rate gauge",
        f'studio_transcode_error_rate{{format="DCP_4K"}} {enc["error_rate_percent"]:.2f}',
        "",
        "# HELP studio_livestream_bitrate_kbps Ingest bitrate for live premiere stream in kbps",
        "# TYPE studio_livestream_bitrate_kbps gauge",
        f'studio_livestream_bitrate_kbps{{channel="global_premiere"}} {live["ingest_bitrate_kbps"]}',
        "",
        "# HELP studio_livestream_dropped_frames_rate Percentage of dropped frames in premiere livestream",
        "# TYPE studio_livestream_dropped_frames_rate gauge",
        f'studio_livestream_dropped_frames_rate{{channel="global_premiere"}} {live["dropped_frames_percent"]:.2f}',
        "",
        "# HELP studio_livestream_viewer_concurrency Active concurrent viewers watching live premiere stream",
        "# TYPE studio_livestream_viewer_concurrency gauge",
        f'studio_livestream_viewer_concurrency{{channel="global_premiere"}} {live["viewer_concurrency"]}',
        ""
    ]
    return "\n".join(lines)
