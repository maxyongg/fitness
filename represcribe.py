#!/usr/bin/env python3
"""
Re-prescribe after a session saved from the phone page, with nobody in the loop.

.github/workflows/represcribe.yml runs after the Drain inbox Action and calls:

  python3 represcribe.py pending   pending=true|false, for $GITHUB_OUTPUT
  python3 represcribe.py run       Claude Code, headless: edits RX, plan.md, log.md
  python3 represcribe.py finish    checks those edits, rebuilds state.json,
                                   prints the commit subject

The workflow only calls these three, so the prompt (docs/represcribe-prompt.md),
model and budget can change here without re-pasting the workflow; Claude can't push
workflow files.

"Pending" means the newest session in log.md is not the one RX.after names. A failed
run leaves RX.after behind, so the next drain, or Run workflow, tries again.
"""

import json
import os
import re
import subprocess
import sys
from datetime import date

import drain

ROOT = drain.ROOT
LOG = drain.LOG
INDEX = drain.INDEX
STATE = drain.STATE
PROMPT = os.path.join(ROOT, "docs", "represcribe-prompt.md")

MODEL = "claude-opus-5"
EFFORT = "high"
BUDGET_USD = "3"          # hard stop per run; a normal run costs well under this
TOOLS = ["Read", "Edit", "Glob", "Grep"]  # no shell: the workflow commits, not Claude
EDITABLE = {"index.html", "plan.md", "log.md"}

HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2}) · \w+ · (.+?)\s*$", re.M)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout


def rx_span(html):
    m = re.search(r"var RX\s*=\s*\{", html)
    if not m:
        return None
    start = m.end() - 1
    return start, drain._object_span(html, start)


def parse_rx(html):
    span = rx_span(html)
    if not span:
        return None
    try:
        return json.loads(drain._js_object_to_json(html[span[0]:span[1]]))
    except json.JSONDecodeError:
        return None


def latest_session():
    found = HEADER.findall(read(LOG))
    return f"{found[-1][0]} {found[-1][1]}" if found else None


def anchors(rx):
    return {sid: [e["name"] for e in s["exercises"] if e.get("type") == "anchor"]
            for sid, s in rx["sessions"].items()}


def cmd_pending():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("::error::Add the ANTHROPIC_API_KEY repo secret — see docs/github-actions-setup.md",
              file=sys.stderr)
        sys.exit(1)
    latest = latest_session()
    after = (parse_rx(read(INDEX)) or {}).get("after")
    pending = bool(latest) and latest != after
    print(f"newest session: {latest} · RX.after: {after}", file=sys.stderr)
    print(f"pending={'true' if pending else 'false'}")


def cmd_run():
    latest = latest_session()
    after = (parse_rx(read(INDEX)) or {}).get("after") or "not set — start from the newest entry"
    sid, when = drain.next_session_id(latest[:10])
    prompt = read(PROMPT)
    for key, value in {
        "after": after,
        "latest": latest,
        "next": f"{drain.SESSION_NAMES.get(sid, sid)} (RX.sessions.{sid}), {when}",
        "today": date.today().isoformat(),
    }.items():
        prompt = prompt.replace("{{" + key + "}}", value)

    cmd = ["claude", "-p", prompt,
           "--model", MODEL, "--effort", EFFORT,
           "--max-budget-usd", BUDGET_USD,
           "--permission-mode", "dontAsk",
           "--allowed-tools", *TOOLS]
    sys.exit(subprocess.run(cmd, cwd=ROOT).returncode)


def cmd_finish():
    errors = []
    latest = latest_session()
    old_html, new_html = git("show", "HEAD:index.html"), read(INDEX)
    old_rx, new_rx = parse_rx(old_html), parse_rx(new_html)

    if not new_rx:
        errors.append("RX in index.html no longer parses")
    else:
        if new_rx.get("after") != latest:
            errors.append(f"RX.after is {new_rx.get('after')!r}, expected {latest!r}")
        if new_rx.get("schedule") != old_rx.get("schedule"):
            errors.append("RX.schedule changed — the template is his")
        if set(new_rx.get("sessions", {})) != set(old_rx["sessions"]):
            errors.append("sessions were added or removed")
        elif anchors(new_rx) != anchors(old_rx):
            errors.append("an anchor's exercise changed")

    stray = [f for f in git("diff", "--name-only", "HEAD").split() if f not in EDITABLE]
    if stray:
        errors.append("changed files it may not touch: " + ", ".join(stray))

    (os_, oe), (ns, ne) = rx_span(old_html), rx_span(new_html) or (0, 0)
    if old_html[:os_] != new_html[:ns] or old_html[oe:] != new_html[ne:]:
        errors.append("index.html changed outside RX")

    numstat = git("diff", "--numstat", "HEAD", "--", "log.md").split()
    if numstat and numstat[1] != "0":
        errors.append(f"{numstat[1]} line(s) removed from log.md")

    if errors:
        for e in errors:
            print(f"::error::{e}", file=sys.stderr)
        sys.exit(1)

    state = json.loads(read(STATE)) if os.path.exists(STATE) else {}
    drain.apply_rx(state, new_rx)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print(f"rx: re-prescribe after {latest}")


if __name__ == "__main__":
    commands = {"pending": cmd_pending, "run": cmd_run, "finish": cmd_finish}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        sys.exit("usage: represcribe.py pending|run|finish")
    commands[sys.argv[1]]()
