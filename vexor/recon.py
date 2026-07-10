"""System reconnaissance — gather host intelligence."""

import os
import platform
import socket
import subprocess
import json


def gather() -> dict:
    data = {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_release": platform.release(),
        "arch": platform.machine(),
        "user": _get_user(),
        "internal_ip": _get_ip(),
        "external_ip": _get_external_ip(),
        "interfaces": _get_interfaces(),
        "processes": _get_processes(),
        "drives": _get_drives(),
    }
    return data


def _get_user() -> str:
    return os.getenv("USERNAME") or os.getenv("USER") or "unknown"


def _get_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _get_external_ip() -> str:
    try:
        import requests
        r = requests.get("https://api.ipify.org?format=json", timeout=5)
        return r.json().get("ip", "unknown")
    except Exception:
        return "unknown"


def _get_interfaces() -> list:
    try:
        result = subprocess.run(
            ["ipconfig" if platform.system() == "Windows" else "ip", "addr"],
            capture_output=True, text=True, timeout=5
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()][:20]
    except Exception:
        return []


def _get_processes() -> list:
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(["ps", "aux", "--no-headers"], capture_output=True, text=True, timeout=5)
        return [line.strip() for line in result.stdout.splitlines()[:30]]
    except Exception:
        return []


def _get_drives() -> list:
    if platform.system() == "Windows":
        try:
            import string
            drives = []
            for letter in string.ascii_uppercase:
                path = f"{letter}:\\"
                if os.path.exists(path):
                    drives.append(path)
            return drives
        except Exception:
            return []
    else:
        return ["/"]
