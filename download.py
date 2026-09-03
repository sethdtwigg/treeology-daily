#!/usr/bin/env python3
"""Download the catechism card PDFs into Catechism_PDFs/.

Run this once; scraper.py then reads from that folder instead of re-fetching
all 92 cards on every parse.

    pip install -r requirements.txt
    python download.py
"""
import os
import sys
import time

import requests

from scraper import PDF_URLS

FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Catechism_PDFs")


def download(number, url, session):
    # The filename comes from a URL path segment. It is a constant today, but
    # basename() keeps a stray "../" or a backslash from escaping the folder if
    # the list ever becomes configurable or a redirect is followed.
    filename = os.path.basename(url.split("/")[-1].split("\\")[-1])
    if not filename:
        raise ValueError(f"no filename in {url}")
    path = os.path.join(FOLDER, f"{str(number).zfill(2)}_{filename}")

    last = None
    for attempt in range(3):
        try:
            r = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
            return path
        except requests.exceptions.RequestException as e:
            last = e
            time.sleep(2 ** attempt)   # back off rather than hammering the host
    raise last


def main():
    os.makedirs(FOLDER, exist_ok=True)
    session = requests.Session()
    failed = []

    for number, url in PDF_URLS:
        print(f"Downloading #{number}: {url.split('/')[-1]}...")
        try:
            download(number, url, session)
        except (requests.exceptions.RequestException, OSError, ValueError) as e:
            # OSError matters too: a full disk or a locked file used to abort
            # the whole run partway through.
            print(f"  failed: {e}")
            failed.append(number)

    print(f"\n{len(PDF_URLS) - len(failed)}/{len(PDF_URLS)} downloaded into {FOLDER}")
    if failed:
        # A missing card silently becomes a missing catechism later, which is
        # how Thanksgiving.pdf went absent without anyone noticing.
        print(f"FAILED: {failed}")
        return 1
    return 0


if __name__ == "__main__":
    # Without this guard, `import download` fires 92 HTTP requests.
    sys.exit(main())
