#!/usr/bin/env python3
"""Download Framer site .mjs chunks (and recursive ./ imports) to vendor/framer-site/."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
OUT = ROOT / "vendor" / "framer-site" / "3bR6R2YrHoycodLqL6z8ep"
BASE = "https://framerusercontent.com/sites/3bR6R2YrHoycodLqL6z8ep"

IMPORT_RE = re.compile(r'(?:from|import)\s*"\./([^"]+\.mjs)"')


def curl_download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["curl", "-fsSL", "-o", str(dest), url],
        check=True,
    )


def main() -> None:
    text = HTML.read_text(encoding="utf-8")
    # Only bundles linked for hydration (skip search index JSON endpoints named .js)
    seed = set(
        m.group(1)
        for m in re.finditer(
            r'href="https://framerusercontent\.com/sites/3bR6R2YrHoycodLqL6z8ep/([^"?]+\.mjs)"',
            text,
        )
    )
    seed |= set(
        m.group(1)
        for m in re.finditer(
            r'src="https://framerusercontent\.com/sites/3bR6R2YrHoycodLqL6z8ep/([^"?]+\.mjs)"',
            text,
        )
    )
    seen: set[str] = set()
    queue = list(seed)

    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        dest = OUT / name
        if not dest.exists():
            print("fetch", name)
            curl_download(f"{BASE}/{name}", dest)
        body = dest.read_text(encoding="utf-8", errors="replace")
        for m in IMPORT_RE.finditer(body):
            dep = m.group(1)
            if dep not in seen:
                queue.append(dep)

    print(f"Downloaded {len(seen)} files to {OUT.relative_to(ROOT)}")

    events_js = ROOT / "vendor" / "events-framer-com-script.js"
    if not events_js.exists():
        print("fetch events-framer-com-script.js")
        subprocess.run(
            [
                "curl",
                "-fsSL",
                "-o",
                str(events_js),
                "https://events.framer.com/script?v=2",
            ],
            check=True,
        )


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print("curl failed:", e, file=sys.stderr)
        sys.exit(1)
