#!/usr/bin/env python3
"""Local server for the grammar practice page.

Serves index.html and saves what you type into ./sentences/ (one .txt per
grammar point) plus a combined all_sentences.md.

    python3 server.py              # then open http://localhost:8765
    python3 server.py 9000         # different port
    python3 server.py --no-open    # don't launch a browser tab

Furigana comes from SudachiPy, kept in ./vendor (see furigana.py).
"""
import json
import os
import re
import sys
import threading
import webbrowser
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import furigana

ROOT = Path(__file__).resolve().parent
SENTENCES = ROOT / "sentences"
COMBINED = ROOT / "all_sentences.md"
HOST, PORT = "127.0.0.1", 8765
PROGRESS = SENTENCES / ".progress.json"  # {"days": {"2026-10-08": 12, ...}}: sentences added per day
MAX_BYTES = 1_000_000
LOCK = threading.Lock()
_grammar = (None, None)  # (mtime of grammar.json, parsed items)


def load_grammar():
    """grammar.json, re-read only when the file changes (it's ~700 KB, and every autosave asks for it)."""
    global _grammar
    path = ROOT / "grammar.json"
    mtime = path.stat().st_mtime_ns
    if _grammar[0] != mtime:
        items = json.loads(path.read_text(encoding="utf-8"))
        for g in items:
            safe = re.sub(r'[\\/:*?"<>|\s]+', "_", g["title"]).strip("_")
            g["file"] = f'{g["id"]:03d}_{safe}.txt'
        _grammar = (mtime, items)
    return _grammar[1]


def sentence_count(text):
    """A sentence is a line with at least 3 characters. Keep in sync with count() in index.html."""
    return sum(1 for ln in text.splitlines() if len(ln.strip()) >= 3)


def load_progress():
    try:
        days = json.loads(PROGRESS.read_text(encoding="utf-8")).get("days", {})
        return days if isinstance(days, dict) else {}
    except (OSError, ValueError, AttributeError):
        return {}


def add_to_today(delta):
    """Net sentences written today (deleting one you wrote today takes it back off). Caller holds LOCK."""
    days = load_progress()
    today = date.today().isoformat()
    days[today] = max(0, int(days.get(today, 0)) + delta)
    write_atomic(PROGRESS, json.dumps({"days": days}, indent=0, sort_keys=True))
    return today, days[today]


def write_atomic(path, text):
    path.parent.mkdir(exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")  # callers hold LOCK, so one writer at a time
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def rebuild_combined(items):
    parts = [
        "# N2 Grammar: practice sentences\n",
        f"_Updated {datetime.now():%Y-%m-%d %H:%M}_\n",
    ]
    for g in items:
        path = SENTENCES / g["file"]
        if not path.exists():
            continue
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            continue
        head = f'## {g["id"]:03d} · {g["title"]}'
        if g.get("reading"):
            head += f' ({g["reading"]})'
        parts.append(head + "\n")
        parts.append("_" + "; ".join(g["meanings"]) + "_\n")
        parts.append("\n".join(f"- {ln}" for ln in lines) + "\n")
    write_atomic(COMBINED, "\n".join(parts))


class Handler(BaseHTTPRequestHandler):
    server_version = "GrammarPractice"

    def log_message(self, fmt, *args):
        pass  # we print our own save lines

    def _send(self, status, body=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _host_ok(self):
        # Refuse requests whose Host isn't loopback (DNS-rebinding guard), and
        # cross-site requests (an Origin header naming some other site).
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        origin = self.headers.get("Origin")
        origin_host = urlparse(origin).hostname if origin else None
        return host in ("localhost", "127.0.0.1") and origin_host in (None, "localhost", "127.0.0.1")

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, b"forbidden")
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            return self._send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/api/grammar":
            return self._json(load_grammar())
        if path == "/api/sentences":
            out = {}
            for g in load_grammar():
                p = SENTENCES / g["file"]
                if p.exists():
                    out[str(g["id"])] = p.read_text(encoding="utf-8")
            return self._json(out)
        if path == "/api/stats":
            return self._json({"day": date.today().isoformat(), "days": load_progress()})
        self._send(404, b"not found")

    def do_POST(self):
        if not self._host_ok():
            return self._send(403, b"forbidden")
        if self.path.split("?", 1)[0] != "/api/furigana":
            return self._send(404, b"not found")
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > 200_000:
                return self._send(413, b"too large")
            texts = json.loads(self.rfile.read(length).decode("utf-8"))["texts"]
            if not (isinstance(texts, list) and len(texts) <= 300 and all(isinstance(t, str) and len(t) <= 600 for t in texts)):
                raise ValueError
        except (ValueError, KeyError, UnicodeDecodeError):
            return self._send(400, b"expected {\"texts\": [up to 300 strings]}")
        try:
            results = [furigana.segments(t) for t in texts]
        except Exception as e:  # SudachiPy / dictionary missing
            return self._json({"error": f"furigana unavailable: {e}"}, 503)
        self._json({"results": results})

    def do_PUT(self):
        if not self._host_ok():
            return self._send(403, b"forbidden")
        m = re.fullmatch(r"/api/sentences/(\d+)", self.path.split("?", 1)[0])
        if not m:
            return self._send(404, b"not found")
        items = load_grammar()
        g = next((x for x in items if x["id"] == int(m.group(1))), None)
        if g is None:
            return self._send(404, b"unknown grammar id")
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._send(400, b"bad length")
        if length > MAX_BYTES:
            return self._send(413, b"too large")
        try:
            text = self.rfile.read(length).decode("utf-8").replace("\r\n", "\n")
        except UnicodeDecodeError:
            return self._send(400, b"not utf-8")

        with LOCK:
            path = SENTENCES / g["file"]
            before = sentence_count(path.read_text(encoding="utf-8")) if path.exists() else 0
            if text or path.exists():  # don't create empty files
                write_atomic(path, text)
                rebuild_combined(items)
            n = sentence_count(text)
            if n != before:
                day, today = add_to_today(n - before)
            else:
                day = date.today().isoformat()
                today = load_progress().get(day, 0)
        print(f'{datetime.now():%H:%M:%S}  saved  sentences/{g["file"]}  ({n} sentences, {today} today)', flush=True)
        self._json({"ok": True, "file": g["file"], "day": day, "today": today})


def main():
    args = sys.argv[1:]
    port = next((int(a) for a in args if a.isdigit()), PORT)
    SENTENCES.mkdir(exist_ok=True)
    try:
        httpd = ThreadingHTTPServer((HOST, port), Handler)
    except OSError as e:
        sys.exit(f"Could not start on port {port}: {e}\nAlready running? Otherwise try: python3 server.py {port + 1}")
    url = f"http://localhost:{port}/"
    print(f"Grammar practice running at {url}")
    print(f"Saving to {SENTENCES}")
    print("Furigana: " + ("ready (SudachiPy)" if furigana.available() else "NOT available. Is ./vendor intact?"))
    print("Ctrl+C to stop.", flush=True)
    if "--no-open" not in args:
        threading.Timer(0.5, webbrowser.open, [url]).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
