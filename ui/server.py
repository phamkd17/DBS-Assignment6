#!/usr/bin/env python3
"""LifeHarness UI server. Read-only: serves the page and the current plan.

Run:  python3 ui/server.py      then open http://localhost:4321
"""
import json
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLANS = ROOT / "plans"
UI = ROOT / "ui"
PORT = 4321
DATED = re.compile(r"^\d{4}-\d{2}-\d{2}\.json$")


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def state():
    saved_files = sorted(p for p in PLANS.glob("*.json") if DATED.match(p.name))
    saved = load(saved_files[-1]) if saved_files else None
    proposed = load(PLANS / "proposed.json") if (PLANS / "proposed.json").exists() else None
    return {"proposed": proposed, "saved": saved}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/state"):
            body = json.dumps(state()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *args):  # keep the terminal quiet
        pass


if __name__ == "__main__":
    print(f"LifeHarness UI: http://localhost:{PORT}")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
