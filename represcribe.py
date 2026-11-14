#!/usr/bin/env python3
"""
Re-prescribe after a session saved from the phone page, with nobody in the loop.

  python3 represcribe.py pending   pending=true|false
  python3 represcribe.py prompt    the brief (docs/represcribe-prompt.md), filled in
  python3 represcribe.py finish    checks the edits, rebuilds state.json,
                                   prints the commit subject
  python3 represcribe.py run       Claude Code headless on the brief (API key needed)

In use: a Claude Code routine on his Claude plan, 22:00 SGT on Mon/Thu/Sat/Sun. It runs
`pending`, and if a session is waiting, works through `prompt` itself, then runs
`finish`, then commits and pushes. The routine's own instructions are in
docs/workflows.md.

Not in use: the Re-prescribe Action in docs/github-actions-setup.md. It runs
`pending`, `run`, `finish` after every drain and bills API credits (~$1 a session).

"Pending" means the newest session in log.md is not the one RX.after names. A failed
run leaves RX.after behind, so the next run tries again.
"""

import json
import os
import re
import subprocess
import sys
from datetime import date, timedelta

import drain
import health
import review

ROOT = drain.ROOT
LOG = drain.LOG
INDEX = drain.INDEX
STATE = drain.STATE
PROMPT = os.path.join(ROOT, "docs", "represcribe-prompt.md")

MODEL = "claude-opus-5"
EFFORT = "high"
BUDGET_USD = "3"          # hard stop per run; a normal run costs well under this
TOOLS = ["Read", "Edit", "Glob", "Grep"]  # `run` only: no shell, the workflow commits
EDITABLE = {"index.html", "plan.md", "log.md"}
REBUILT = {"state.json"}  # finish writes it, so a second finish must not reject it

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
    """The newest lifting session. Football is logged too, but RX.after names a lift:
    a match is context for the session after it, not one to re-prescribe from."""
    found = [h for h in HEADER.findall(read(LOG)) if h[1] != "Football"]
    return f"{found[-1][0]} {found[-1][1]}" if found else None


def anchors(rx):
    return {sid: [e["name"] for e in s["exercises"] if e.get("type") == "anchor"]
            for sid, s in rx["sessions"].items()}


def check_calls(rx):
    """Every slot the load review calls flat carries a `call`: the stall rule in plan.md
    ("propose something, don't note it"), made checkable. And each session's `short`
    (the flat-day slots) points at real slots."""
    errors = []
    rev = review.review(review.read_log(LOG), rx)
    for sid, rows in rev.items():
        exs = rx["sessions"][sid]["exercises"]
        for r in rows:
            if r["status"] == "flat" and not str(exs[r["slot"] - 1].get("call", "")).strip():
                errors.append(f"{rx['sessions'][sid]['name']} slot {r['slot']} ({r['name']}) is flat "
                              f"and has no `call`: {r['line']}")
        short = rx["sessions"][sid].get("short", [])
        if not isinstance(short, list) or any(not isinstance(i, int) or not 0 <= i < len(exs) for i in short):
            errors.append(f"{rx['sessions'][sid]['name']} `short` must list slot indexes 0-{len(exs) - 1}")
    return errors


def cmd_pending():
    latest = latest_session()
    after = (parse_rx(read(INDEX)) or {}).get("after")
    pending = bool(latest) and latest != after
    print(f"newest session: {latest} · RX.after: {after}", file=sys.stderr)
    print(f"pending={'true' if pending else 'false'}")


def filled_prompt():
    latest = latest_session()
    after = (parse_rx(read(INDEX)) or {}).get("after") or "not set — start from the newest entry"
    log, rx = review.read_log(LOG), parse_rx(read(INDEX))
    sid, when = review.next_after(log, latest[:10], rx)
    prompt = read(PROMPT)
    for key, value in {
        "after": after,
        "latest": latest,
        "next": f"{drain.SESSION_NAMES.get(sid, sid)} (RX.sessions.{sid}), {when}",
        "today": date.today().isoformat(),
        "review": review.review_text(review.review(log, rx), rx),
        "sleep": "\n".join(health.sleep_lines(health.load_nights(),
                                              (date.fromisoformat(latest[:10]) - timedelta(days=6)).isoformat()))
                 or "No nights recorded yet.",
    }.items():
        prompt = prompt.replace("{{" + key + "}}", value)
    return prompt


def cmd_prompt():
    print(filled_prompt())


def cmd_run():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("::error::Add the ANTHROPIC_API_KEY repo secret — see docs/github-actions-setup.md",
              file=sys.stderr)
        sys.exit(1)
    cmd = ["claude", "-p", filled_prompt(),
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
        else:
            errors += check_calls(new_rx)

    stray = [f for f in git("diff", "--name-only", "HEAD").split()
             if f not in EDITABLE | REBUILT]
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
    drain.refresh_review(state, new_rx)
    drain.write_state(state)
    print(f"rx: re-prescribe after {latest}")


if __name__ == "__main__":
    commands = {"pending": cmd_pending, "prompt": cmd_prompt, "finish": cmd_finish, "run": cmd_run}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        sys.exit("usage: represcribe.py pending|prompt|finish|run")
    commands[sys.argv[1]]()
