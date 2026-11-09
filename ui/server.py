#!/usr/bin/env python3
"""LifeHarness UI server: serves the page and the current plan, and lets the page
update to-dos (notes/todos.json). It never touches plans/ or data/.

Run:  python3 ui/server.py      then open http://localhost:4321
"""
import json
import os
import re
import secrets
from datetime import datetime
import threading
import time
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PLANS = ROOT / "plans"
UI = ROOT / "ui"
PORT = 4321
DATED = re.compile(r"^\d{4}-\d{2}-\d{2}\.json$")

# Background: Windows Spotlight lock-screen photos.
# Unofficial, undocumented endpoint (the one Windows itself calls); it may change.
# Photos are licensed to Microsoft: shown on this local page only, never saved.
SPOTLIGHT = ("https://fd.api.iris.microsoft.com/v4/api/selection"
             "?placement=88000820&bcnt=4&country=US&locale=en-US&fmt=json")
BATCHES_PER_DAY = 1   # ~4 photos: the page shows the first, the rest are backups if it fails to load
CACHE = UI / ".spotlight-cache.json"   # today's photo links, so a server restart keeps the same photo
_lock = threading.Lock()
try:
    _c = json.loads(CACHE.read_text())
    _pool, _fetched_on = _c["photos"], _c["date"]
except (OSError, KeyError, json.JSONDecodeError):
    _pool, _fetched_on = [], None


def _fetch_batch():
    req = urllib.request.Request(SPOTLIGHT, headers={"User-Agent": "LifeHarness/1.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        data = json.load(r)
    photos = []
    for it in data.get("batchrsp", {}).get("items", []):
        try:
            ad = json.loads(it["item"])["ad"]
            url = ad["landscapeImage"]["asset"]
        except (KeyError, TypeError, json.JSONDecodeError):
            continue
        u = urlparse(url)
        if u.scheme != "https" or not u.hostname.endswith(".microsoft"):
            continue  # only Microsoft's image CDN
        place = (ad.get("iconHoverText") or "").split("\r\n")[0]
        photos.append({"url": url, "place": place or ad.get("title", ""),
                       "credit": ad.get("copyright", "")})
    return photos


def spotlight_photos():
    """Fetch a fresh set once per day (on the first request of a new date)."""
    global _pool, _fetched_on
    today = time.strftime("%Y-%m-%d")
    with _lock:
        if _pool and _fetched_on == today:
            return list(_pool)
        fresh, seen = [], set()
        for _ in range(BATCHES_PER_DAY):
            try:
                for p in _fetch_batch():
                    if p["url"] not in seen:
                        seen.add(p["url"])
                        fresh.append(p)
            except Exception:
                break   # offline or endpoint changed
        if fresh:
            _pool, _fetched_on = fresh, today
            try:
                CACHE.write_text(json.dumps({"date": today, "photos": fresh}))
            except OSError:
                pass
        return list(_pool)   # if the fetch failed, keep yesterday's photos (retry next request)


def local_settings():
    """KEY=VALUE pairs from the git-ignored .env file (e.g. GOOGLE_ACCOUNT)."""
    settings = {}
    try:
        for line in (ROOT / ".env").read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                settings[k.strip()] = v.strip()
    except OSError:
        pass
    return settings


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


# To-dos: shared between the page (via the endpoints below) and Claude (check-ins).
TODOS = ROOT / "notes" / "todos.json"
_todo_lock = threading.Lock()
ALLOWED_ORIGINS = {f"http://localhost:{PORT}", f"http://127.0.0.1:{PORT}"}
MAX_TODO, MAX_NOTE = 300, 1000


class TodoFileError(Exception):
    pass


def load_todos():
    if not TODOS.exists():
        return {"todos": []}
    try:
        data = json.loads(TODOS.read_text())
        assert isinstance(data.get("todos"), list)
        return data
    except (OSError, json.JSONDecodeError, AssertionError, AttributeError):
        raise TodoFileError("notes/todos.json is unreadable; not overwriting it")


def save_todos(data):
    tmp = TODOS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, TODOS)   # atomic: never leaves a half-written file


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def clean(text, limit):
    text = " ".join(str(text or "").split())
    return text[:limit] if text else None


def state():
    saved_files = sorted(p for p in PLANS.glob("*.json") if DATED.match(p.name))
    saved = load(saved_files[-1]) if saved_files else None
    proposed = load(PLANS / "proposed.json") if (PLANS / "proposed.json").exists() else None
    try:
        todos = load_todos()["todos"]
    except TodoFileError:
        todos = None   # the page shows a warning instead of the list
    return {"proposed": proposed, "saved": saved, "todos": todos}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI), **kwargs)

    def send_json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/state"):
            return self.send_json(state())
        if self.path.startswith("/api/photos"):
            return self.send_json(spotlight_photos())
        if self.path.startswith("/api/config"):
            return self.send_json({"google_account": local_settings().get("GOOGLE_ACCOUNT", "")})
        super().do_GET()

    def do_POST(self):
        if not self.path.startswith("/api/todos/"):
            return self.send_error(404)
        # Only the page itself may make changes: other websites can also send requests to
        # localhost, but they can't fake the Origin header or send JSON without a preflight.
        if self.headers.get("Origin") not in ALLOWED_ORIGINS:
            return self.send_error(403)
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            return self.send_error(415)
        length = int(self.headers.get("Content-Length") or 0)
        if length > 4096:
            return self.send_error(413)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self.send_error(400)
        action = self.path[len("/api/todos/"):]

        with _todo_lock:
            try:
                data = load_todos()
            except TodoFileError as e:
                return self.send_error(409, str(e))
            todos = data["todos"]
            find = lambda: next((t for t in todos if t.get("id") == body.get("id")), None)

            if action == "add":
                text = clean(body.get("text"), MAX_TODO)
                if not text:
                    return self.send_error(400)
                todos.append({"id": "t" + secrets.token_hex(4), "text": text, "done": False,
                              "created": now(), "done_at": None, "notes": []})
            elif action == "toggle":
                t = find()
                if not t:
                    return self.send_error(404)
                t["done"] = not t.get("done")
                t["done_at"] = now() if t["done"] else None
            elif action == "note":
                t, text = find(), clean(body.get("text"), MAX_NOTE)
                if not t or not text:
                    return self.send_error(400)
                t.setdefault("notes", []).append({"at": now(), "by": "Khang", "text": text})
            else:
                return self.send_error(404)
            save_todos(data)
        return self.send_json(todos)

    def log_message(self, *args):  # keep the terminal quiet
        pass


if __name__ == "__main__":
    print(f"LifeHarness UI: http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
