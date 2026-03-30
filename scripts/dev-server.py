#!/usr/bin/env python3
"""
Serve the wedding site over http:// — required for Framer ES modules (.mjs).
Opening index.html via file:// often causes CORS / module load errors in the browser.

Usage (from repo root):
  python3 scripts/dev-server.py
Then open http://127.0.0.1:8080/index.html
"""
from __future__ import annotations

import mimetypes
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("PORT", "8080"))

mimetypes.add_type("text/javascript", ".mjs")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        # Harmless for same-origin; helps some webviews / proxies that expect CORS on assets.
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def main() -> None:
    os.chdir(ROOT)
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving {ROOT}")
    print(f"Open http://127.0.0.1:{PORT}/index.html")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
