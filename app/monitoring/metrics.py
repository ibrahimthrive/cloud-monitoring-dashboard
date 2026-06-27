"""psutil-backed system metrics collection."""
import platform
import shutil
import subprocess
import time
from datetime import datetime

import psutil

_BOOT_TIME = psutil.boot_time()
_last_net_sample = {"timestamp": None, "bytes_sent": None, "bytes_recv": None}


def get_cpu_metrics():
    return {
        "percent": psutil.cpu_percent(interval=0.3),
        "per_core": psutil.cpu_percent(interval=0.0, percpu=True),
        "core_count": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "load_avg": _get_load_avg(),
    }


def _get_load_avg():
    try:
        return [round(x, 2) for x in psutil.getloadavg()]
    except (AttributeError, OSError):
        return None


def get_ram_metrics():
    vm = psutil.virtual_memory()
    return {
        "percent": vm.percent,
        "used_mb": round(vm.used / (1024 ** 2), 2),
        "total_mb": round(vm.total / (1024 ** 2), 2),
        "available_mb": round(vm.available / (1024 ** 2), 2),
    }


def get_disk_metrics():
    usage = shutil.disk_usage("/")
    percent = round((usage.used / usage.total) * 100, 2) if usage.total else 0.0
    return {
        "percent": percent,
        "used_gb": round(usage.used / (1024 ** 3), 2),
        "total_gb": round(usage.total / (1024 ** 3), 2),
        "free_gb": round(usage.free / (1024 ** 3), 2),
    }


def get_network_metrics():
    """Computes instantaneous upload/download throughput in KB/s."""
    global _last_net_sample

    counters = psutil.net_io_counters()
    now = time.time()

    sent_kbps = recv_kbps = 0.0
    if _last_net_sample["timestamp"] is not None:
        elapsed = now - _last_net_sample["timestamp"]
        if elapsed > 0:
            sent_kbps = round((counters.bytes_sent - _last_net_sample["bytes_sent"]) / 1024 / elapsed, 2)
            recv_kbps = round((counters.bytes_recv - _last_net_sample["bytes_recv"]) / 1024 / elapsed, 2)

    _last_net_sample = {"timestamp": now, "bytes_sent": counters.bytes_sent, "bytes_recv": counters.bytes_recv}

    return {
        "upload_kbps": max(sent_kbps, 0.0),
        "download_kbps": max(recv_kbps, 0.0),
        "total_sent_mb": round(counters.bytes_sent / (1024 ** 2), 2),
        "total_recv_mb": round(counters.bytes_recv / (1024 ** 2), 2),
    }


def get_uptime_seconds():
    return int(time.time() - _BOOT_TIME)


def get_uptime_human():
    seconds = get_uptime_seconds()
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def get_current_metrics():
    """Aggregate snapshot of all live metrics, used by the AJAX live-refresh endpoint."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": get_cpu_metrics(),
        "ram": get_ram_metrics(),
        "disk": get_disk_metrics(),
        "network": get_network_metrics(),
        "uptime_seconds": get_uptime_seconds(),
        "uptime_human": get_uptime_human(),
        "hostname": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
    }


def get_processes(limit=50, sort_by="cpu_percent"):
    processes = []
    for proc in psutil.process_iter(["pid", "name", "username", "status", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append(
                {
                    "pid": info["pid"],
                    "name": info["name"],
                    "username": info["username"],
                    "status": info["status"],
                    "cpu_percent": round(info["cpu_percent"] or 0.0, 2),
                    "memory_percent": round(info["memory_percent"] or 0.0, 2),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda p: p.get(sort_by, 0), reverse=True)
    return processes[:limit]


def get_services():
    """Best-effort cross-platform service listing.

    Windows: psutil.win_service_iter(). Linux: systemctl (if present), else empty list.
    """
    system = platform.system()

    if system == "Windows":
        services = []
        for svc in psutil.win_service_iter():
            try:
                info = svc.as_dict()
                services.append(
                    {
                        "name": info["name"],
                        "display_name": info["display_name"],
                        "status": info["status"],
                        "start_type": info.get("start_type"),
                    }
                )
            except psutil.Error:
                continue
        return services

    if system == "Linux" and shutil.which("systemctl"):
        try:
            output = subprocess.check_output(
                ["systemctl", "list-units", "--type=service", "--no-pager", "--no-legend"],
                text=True,
                timeout=5,
            )
        except (subprocess.SubprocessError, OSError):
            return []

        services = []
        for line in output.strip().splitlines():
            fields = line.split(None, 4)
            if len(fields) >= 4:
                services.append(
                    {
                        "name": fields[0],
                        "display_name": fields[0],
                        "status": fields[3],
                        "start_type": fields[2],
                    }
                )
        return services

    return []
