#!/usr/bin/env python3
"""
Bump RX.asof in index.html to today's date.

Run after drain.py in the GitHub Action so the page shows
prescriptions are current. Does not change exercises, loads,
or rep targets — that is still a Claude decision.
"""

import re
import sys
from datetime import date

ROOT = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
INDEX = __import__("os").path.join(ROOT, "index.html")


def main():
    today = date.today().isoformat()

    with open(INDEX, "r") as f:
        html = f.read()

    new_html, count = re.subn(
        r'(asof:\s*")[^"]*(")',
        rf"\g<1>{today}\2",
        html,
        count=1,
    )

    if count == 0:
        print("Could not find RX.asof in index.html", file=sys.stderr)
        sys.exit(1)

    with open(INDEX, "w") as f:
        f.write(new_html)

    print(f"RX.asof → {today}")


if __name__ == "__main__":
    main()
