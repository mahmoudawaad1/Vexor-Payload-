"""Command execution — shell, Python, and file ops."""

import os
import subprocess
import sys


def run_shell(cmd: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        return output[:50000] if output else "[no output]"
    except subprocess.TimeoutExpired:
        return f"[timeout after {timeout}s]"
    except Exception as e:
        return f"[error: {e}]"


def run_python(code: str) -> str:
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=30
        )
        return (result.stdout + result.stderr)[:50000] or "[no output]"
    except Exception as e:
        return f"[error: {e}]"


def read_file(path: str) -> str:
    try:
        with open(path, "r", errors="replace") as f:
            return f.read()[:100000]
    except Exception as e:
        return f"[error: {e}]"


def write_file(path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w") as f:
            f.write(content)
        return f"[wrote {len(content)} bytes to {path}]"
    except Exception as e:
        return f"[error: {e}]"


def download(url: str, dest: str) -> str:
    try:
        import requests
        r = requests.get(url, timeout=30)
        with open(dest, "wb") as f:
            f.write(r.content)
        return f"[downloaded {len(r.content)} bytes to {dest}]"
    except Exception as e:
        return f"[error: {e}]"


def list_dir(path: str = ".") -> str:
    try:
        entries = os.listdir(path)
        return "\n".join(entries) or "[empty]"
    except Exception as e:
        return f"[error: {e}]"
