import time
import math
import random
from typing import Dict, Any, List

class StudioTelemetrySimulator:
    """
    Simulates authentic film & TV studio infrastructure telemetry:
    - VFX Render Farm (Blender / Houdini / Maya GPU clusters)
    - 4K/8K Post-Production Encoding & Transcode Pipeline (ProRes, AV1, DCP)
    - Global Premiere Livestream Broadcast Pipeline (SRT/RTMP ingest, CDN, viewer metrics)
    """

    def __init__(self):
        self.start_time = time.time()
        self.scenario = "render_farm_incident"  # Default active incident scenario for demo
        self._step_counter = 0

    def set_scenario(self, scenario_name: str):
        valid = ["render_farm_incident", "livestream_incident", "encoding_incident", "all_nominal"]
        if scenario_name in valid:
            self.scenario = scenario_name

    def get_snapshot(self) -> Dict[str, Any]:
        """Returns a consolidated dictionary of current metrics and system state."""
        self._step_counter += 1
        now = time.time()
        elapsed = now - self.start_time
        jitter = math.sin(elapsed / 10.0) * 0.05 + (random.random() - 0.5) * 0.03

        # Base nominal states
        state = {
            "timestamp": now,
            "scenario": self.scenario,
            "render_farm": {
                "total_nodes": 64,
                "active_nodes": 62,
                "faulted_nodes": 2,
                "queue_depth": int(180 + 20 * math.sin(elapsed / 15.0)),
                "average_frame_render_time_sec": 125.0,
                "failed_jobs_last_hour": 3,
                "gpu_vram_usage_percent": 74.2 + (jitter * 10),
                "gpu_temperature_celsius": 68.5,
                "current_project": "Project 'Chronos' - Sequence 14 (VFX Final Comp)",
                "active_shot": "SH_042_EXT_NEBULA_BATTLE",
            },
            "encoding_pipeline": {
                "active_workers": 16,
                "transcode_queue_length": 14,
                "transcode_fps": 184.0,
                "error_rate_percent": 0.02,
                "cpu_utilization_percent": 68.0,
                "target_format": "ProRes 4444 XQ -> AV1 10-bit HDR / SMPTE DCP",
            },
            "livestream_premiere": {
                "stream_status": "ONLINE",
                "ingest_bitrate_kbps": 15200,
                "target_bitrate_kbps": 15000,
                "dropped_frames_percent": 0.04,
                "audio_sync_drift_ms": 2.1,
                "viewer_concurrency": int(52000 + 1500 * math.sin(elapsed / 30.0)),
                "cdn_cache_hit_ratio_percent": 98.6,
                "primary_ingest_region": "us-west-2 (Oregon Studio Ingest)",
            },
            "alerts": []
        }

        # Apply Scenarios
        if self.scenario == "render_farm_incident":
            # Overnight render queue backed up
            state["render_farm"]["active_nodes"] = 46
            state["render_farm"]["faulted_nodes"] = 18
            state["render_farm"]["queue_depth"] = 1428  # Severely backed up
            state["render_farm"]["average_frame_render_time_sec"] = 692.0  # Heavy degradation
            state["render_farm"]["failed_jobs_last_hour"] = 87
            state["render_farm"]["gpu_vram_usage_percent"] = 99.4  # VRAM thrashing
            state["render_farm"]["gpu_temperature_celsius"] = 84.2
            state["alerts"].append({
                "name": "RenderQueueBackpressureCritical",
                "severity": "CRITICAL",
                "stage": "vfx_render_farm",
                "message": "Render queue depth (1,428 frames) exceeds SLA threshold (>500 frames). 18 nodes reporting CUDA OOM on SH_042 8K volumetric layer.",
                "firing_since": "1 hour 42 minutes ago",
                "suggested_action": "Purge cached uncompressed 8K EXR textures or reroute Node Pool B to 48GB VRAM nodes."
            })
            state["alerts"].append({
                "name": "NodePoolMemoryThrashing",
                "severity": "WARNING",
                "stage": "vfx_render_farm",
                "message": "GPU VRAM usage at 99.4% on 18 worker nodes. Swap thrashing detected on /mnt/scratch/render_cache.",
                "firing_since": "54 minutes ago",
                "suggested_action": "Restart hung Blender worker daemons on worker-pool-b-[01-18]."
            })

        elif self.scenario == "livestream_incident":
            # Live premiere broadcast degradation
            state["livestream_premiere"]["stream_status"] = "DEGRADED"
            state["livestream_premiere"]["ingest_bitrate_kbps"] = 6450  # Below 15,000 target
            state["livestream_premiere"]["dropped_frames_percent"] = 4.85  # Critical (> 1%)
            state["livestream_premiere"]["audio_sync_drift_ms"] = 48.6  # Noticeable lip sync desync
            state["livestream_premiere"]["cdn_cache_hit_ratio_percent"] = 81.2
            state["alerts"].append({
                "name": "LivestreamIngestBitrateSevereDrop",
                "severity": "CRITICAL",
                "stage": "live_broadcast",
                "message": "Primary SRT ingest bitrate collapsed to 6,450 kbps (expected 15,000 kbps). Dropped frames at 4.85%.",
                "firing_since": "14 minutes ago",
                "suggested_action": "Failover to Secondary Backup Ingest Path (SRT-B on us-east-1) immediately."
            })

        elif self.scenario == "encoding_incident":
            state["encoding_pipeline"]["active_workers"] = 5
            state["encoding_pipeline"]["transcode_queue_length"] = 89
            state["encoding_pipeline"]["error_rate_percent"] = 12.4
            state["encoding_pipeline"]["cpu_utilization_percent"] = 99.8
            state["alerts"].append({
                "name": "TranscodeQueueBottleneck",
                "severity": "WARNING",
                "stage": "post_encoding",
                "message": "Transcode error rate spiked to 12.4% on chunk multiplexing. 11 encoding workers unresponsive.",
                "firing_since": "28 minutes ago",
                "suggested_action": "Check FFmpeg/AV1 worker disk space on /storage/dcp_tmp and restart worker cluster."
            })

        return state

    def generate_promql_query_result(self, query: str) -> Dict[str, Any]:
        """Simulates Prometheus instant/range query results based on the query string."""
        snapshot = self.get_snapshot()
        query_lower = query.lower()

        timestamp = snapshot["timestamp"]

        if "render_queue" in query_lower or "queue_depth" in query_lower:
            return {
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [
                        {
                            "metric": {
                                "__name__": "studio_render_queue_depth",
                                "project": "Chronos",
                                "pipeline": "vfx_render_farm",
                                "sequence": "SQ_14",
                                "job_type": "blender_cycles_gpu"
                            },
                            "value": [timestamp, str(snapshot["render_farm"]["queue_depth"])]
                        }
                    ]
                }
            }

        elif "gpu_vram" in query_lower or "gpu" in query_lower:
            return {
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [
                        {
                            "metric": {
                                "__name__": "studio_gpu_vram_usage_percent",
                                "node_pool": "worker-pool-b",
                                "gpu_model": "NVIDIA_RTX_A6000",
                                "cluster": "render-farm-west"
                            },
                            "value": [timestamp, f"{snapshot['render_farm']['gpu_vram_usage_percent']:.2f}"]
                        }
                    ]
                }
            }

        elif "failed_jobs" in query_lower or "failure" in query_lower or "error" in query_lower:
            return {
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [
                        {
                            "metric": {
                                "__name__": "studio_render_failed_jobs_total",
                                "reason": "CUDA_OUT_OF_MEMORY",
                                "shot": snapshot["render_farm"]["active_shot"]
                            },
                            "value": [timestamp, str(snapshot["render_farm"]["failed_jobs_last_hour"])]
                        }
                    ]
                }
            }

        elif "livestream" in query_lower or "bitrate" in query_lower or "stream" in query_lower:
            return {
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [
                        {
                            "metric": {
                                "__name__": "studio_livestream_bitrate_kbps",
                                "channel": "global_premiere",
                                "codec": "HEVC_10bit"
                            },
                            "value": [timestamp, str(snapshot["livestream_premiere"]["ingest_bitrate_kbps"])]
                        },
                        {
                            "metric": {
                                "__name__": "studio_livestream_dropped_frames_rate",
                                "channel": "global_premiere"
                            },
                            "value": [timestamp, f"{snapshot['livestream_premiere']['dropped_frames_percent']:.2f}"]
                        }
                    ]
                }
            }

        elif "transcode" in query_lower or "encoding" in query_lower:
            return {
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [
                        {
                            "metric": {
                                "__name__": "studio_transcode_queue_length",
                                "target": "DCP_4K_HDR"
                            },
                            "value": [timestamp, str(snapshot["encoding_pipeline"]["transcode_queue_length"])]
                        },
                        {
                            "metric": {
                                "__name__": "studio_transcode_error_rate",
                                "target": "DCP_4K_HDR"
                            },
                            "value": [timestamp, f"{snapshot['encoding_pipeline']['error_rate_percent']:.2f}"]
                        }
                    ]
                }
            }

        # Default multi-metric vector
        return {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "studio_render_queue_depth", "stage": "vfx"},
                        "value": [timestamp, str(snapshot["render_farm"]["queue_depth"])]
                    },
                    {
                        "metric": {"__name__": "studio_render_faulted_nodes", "stage": "vfx"},
                        "value": [timestamp, str(snapshot["render_farm"]["faulted_nodes"])]
                    },
                    {
                        "metric": {"__name__": "studio_livestream_dropped_frames_rate", "stage": "broadcast"},
                        "value": [timestamp, f"{snapshot['livestream_premiere']['dropped_frames_percent']:.2f}"]
                    }
                ]
            }
        }

    def generate_loki_query_result(self, query: str) -> Dict[str, Any]:
        """Simulates Loki log queries for studio logs."""
        snapshot = self.get_snapshot()
        now_ns = str(int(time.time() * 1e9))

        logs = []
        if snapshot["scenario"] == "render_farm_incident":
            logs = [
                [now_ns, '{"level":"ERROR","host":"worker-b-14","proc":"blender_cycles","msg":"CUDA error: Out of memory in cuMemAlloc(&device_pointer, size) on frame 042_0182.exr"}'],
                [now_ns, '{"level":"WARN","host":"worker-b-08","proc":"render_daemon","msg":"Node memory threshold exceeded: 63.8GB / 64GB allocated. Swap thrashing observed."}'],
                [now_ns, '{"level":"ERROR","host":"worker-b-02","proc":"render_daemon","msg":"Job failed: Shot SH_042 layer \'VolumetricNebula\' exceeded VRAM cap. Node marked FAULTED."}'],
                [now_ns, '{"level":"INFO","host":"render-scheduler","proc":"dispatcher","msg":"Backpressure alert: 1,428 pending frames in queue for Sequence 14."}']
            ]
        elif snapshot["scenario"] == "livestream_incident":
            logs = [
                [now_ns, '{"level":"WARN","host":"ingest-primary-oregon","proc":"srt_receiver","msg":"Packet retransmission rate exceeded 6.2%. Ingest bandwidth throttled."}'],
                [now_ns, '{"level":"ERROR","host":"transcoder-edge-01","proc":"live_packager","msg":"Dropped 144 frames in chunk #9240. Video-audio drift detected (48.6ms)."}'],
                [now_ns, '{"level":"WARN","host":"cdn-gateway","proc":"health_monitor","msg":"Livestream ingest bitrate dropped below 7000 kbps."}']
            ]
        else:
            logs = [
                [now_ns, '{"level":"INFO","host":"render-scheduler","proc":"dispatcher","msg":"Queue operating normally. 180 frames pending. 62 nodes healthy."}'],
                [now_ns, '{"level":"INFO","host":"ingest-primary-oregon","proc":"srt_receiver","msg":"SRT stream healthy. 15,200 kbps, 0 dropped frames."}']
            ]

        return {
            "status": "success",
            "data": {
                "resultType": "streams",
                "result": [
                    {
                        "stream": {"app": "studio-pipeline", "environment": "production"},
                        "values": logs
                    }
                ]
            }
        }

# Global singleton simulator instance
telemetry_simulator = StudioTelemetrySimulator()
