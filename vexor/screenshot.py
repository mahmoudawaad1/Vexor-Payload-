"""Screenshot capture — cross-platform."""

import io
import os
import base64


def capture() -> str:
    """Take screenshot, return base64-encoded PNG."""
    try:
        import pyautogui
        img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        return _fallback_capture()


def save(path: str = None) -> str:
    """Save screenshot to file, return path."""
    path = path or os.path.join(os.path.expanduser("~"), ".vx_screen.png")
    try:
        import pyautogui
        img = pyautogui.screenshot()
        img.save(path)
        return path
    except ImportError:
        return _fallback_capture()


def _fallback_capture() -> str:
    """Fallback using platform-specific tools."""
    import subprocess
    import platform
    import tempfile

    system = platform.system()
    tmp = os.path.join(tempfile.gettempdir(), "vx_screen.png")

    try:
        if system == "Windows":
            # Use built-in PowerShell
            ps_cmd = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "[System.Windows.Forms.Screen]::PrimaryScreen | ForEach-Object {"
                "  $bmp = New-Object System.Drawing.Bitmap($_.Bounds.Width, $_.Bounds.Height);"
                "  $gfx = [System.Drawing.Graphics]::FromImage($bmp);"
                "  $gfx.CopyFromScreen($_.Bounds.Location, [System.Drawing.Point]::Empty, $_.Bounds.Size);"
                f"  $bmp.Save('{tmp}')"
                "}"
            )
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=10)
        elif system == "Darwin":
            subprocess.run(["screencapture", "-x", tmp], capture_output=True, timeout=10)
        elif system == "Linux":
            subprocess.run(["scrot", tmp], capture_output=True, timeout=10)

        if os.path.exists(tmp):
            with open(tmp, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return "[screenshot unavailable]"
