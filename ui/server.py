#!/usr/bin/env python3
"""LifeHarness UI server. Read-only: serves the page and the current plan.

Run:  python3 ui/server.py      then open http://localhost:4321
"""
import json
import re
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
        super().do_GET()

    def log_message(self, *args):  # keep the terminal quiet
        pass


if __name__ == "__main__":
    print(f"LifeHarness UI: http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
