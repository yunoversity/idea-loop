#!/usr/bin/env python3
"""Static server plus a small Deepgram TTS proxy so the API key stays server-side.

    DEEPGRAM_API_KEY=... python3 serve.py        # http://127.0.0.1:8770  (PORT=9000 to change)

Without the env var the page still works: catalog samples play, and users can paste a key in the browser.
"""
import json, os, re, urllib.error, urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
KEY = os.environ.get("DEEPGRAM_API_KEY", "")
MODEL_RE = re.compile(r"^aura-2-[a-z]+-en$")  # English Aura-2 voices only
MAX_CHARS = 2000


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/config":
            return self._json(200, {"proxy": bool(KEY)})
        super().do_GET()

    def do_POST(self):
        if self.path != "/api/speak":
            return self._json(404, {"err_msg": "not found"})
        if not KEY:
            return self._json(503, {"err_msg": "DEEPGRAM_API_KEY is not set on the server"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(min(n, 10_000)))
            text, model = str(req.get("text", "")).strip(), str(req.get("model", ""))
        except (ValueError, TypeError):
            return self._json(400, {"err_msg": "bad request"})
        if not text or len(text) > MAX_CHARS:
            return self._json(400, {"err_msg": f"text must be 1 to {MAX_CHARS} characters"})
        if not MODEL_RE.match(model):
            return self._json(400, {"err_msg": "unsupported model"})
        r = urllib.request.Request(
            f"https://api.deepgram.com/v1/speak?model={model}&encoding=mp3",
            data=json.dumps({"text": text}).encode(),
            headers={"Authorization": f"Token {KEY}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                audio = resp.read()
        except urllib.error.HTTPError as e:
            return self._json(e.code, {"err_msg": "Deepgram error"})
        except (urllib.error.URLError, TimeoutError):
            return self._json(502, {"err_msg": "could not reach Deepgram"})
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", str(len(audio)))
        self.end_headers()
        self.wfile.write(audio)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8770"))
    print(f"http://127.0.0.1:{port}  (key {'loaded' if KEY else 'not set: browser-key mode'})")
    ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=ROOT)).serve_forever()
