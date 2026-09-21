#!/usr/bin/env python3
"""
Drain inbox JSON files into log.md and update state.json.

Handles the mechanical transcription so a Claude session can skip
re-reading plan.md, index.html and the full log. Run it, read
state.json and the stdout summary, then decide what to programme.

Does NOT modify index.html or plan.md — prescriptions are still
a Claude decision, not automation.
"""

import json
import glob
import os
import re
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
INBOX = os.path.join(ROOT, "inbox")
LOG = os.path.join(ROOT, "log.md")
STATE = os.path.join(ROOT, "state.json")
INDEX = os.path.join(ROOT, "index.html")

SCHEDULE = {
    0: "lower",    # Sunday
    1: "upper_a",  # Monday
    2: "football",
    3: "rest",
    4: "upper_b",  # Thursday
    5: "football",
    6: "upper_c",  # Saturday
}

SESSION_NAMES = {
    "upper_a": "Upper A",
    "upper_b": "Upper B",
    "upper_c": "Upper C",
    "lower": "Lower",
}


def find_inbox_files():
    pattern = os.path.join(INBOX, "*.json")
    files = sorted(glob.glob(pattern))
    return files


def parse_inbox(path):
    with open(path) as f:
        return json.load(f)


def format_weight(w):
    if w == int(w):
        return str(int(w))
    return str(w)


def format_duration(secs):
    m, s = divmod(int(secs), 60)
    if m > 0:
        return f"{m}:{s:02d}"
    return f"0:{s:02d}"


def to_log_entry(data):
    date = data["date"]
    session = data.get("session", "")
    day_name = ""
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        day_name = dt.strftime("%a")
    except ValueError:
        pass

    lines = []
    header = f"## {date} · {day_name} · {session}"
    lines.append(header)

    pain = data.get("pain", {}).get("right_lat")
    notes_parts = []
    if pain is not None:
        notes_parts.append(f"pain(R): {pain}/10")
    extra_notes = data.get("notes", "")
    if extra_notes and extra_notes != "Imported from Strong":
        notes_parts.append(f"note: {extra_notes}")
    if notes_parts:
        lines.append(" | ".join(notes_parts))

    for ex in data.get("exercises", []):
        line = format_exercise(ex)
        lines.append(f"- {line}")

    extra = data.get("extra", "").strip()
    if extra:
        lines.append(f"- Extra: {extra}")

    return "\n".join(lines)


def format_exercise(ex):
    name = ex["name"]
    sets = ex.get("sets", [])
    is_bw = ex.get("bodyweight", False)
    bilateral = "weightL" in ex or "weightR" in ex
    ex_weight = ex.get("weight", 0)

    if bilateral:
        return format_bilateral(name, ex, sets)

    has_duration = any(s.get("duration", 0) > 0 for s in sets)

    if has_duration:
        parts = []
        for s in sets:
            dur = s.get("duration", 0)
            if dur > 0:
                parts.append(format_duration(dur))
            elif s.get("reps", 0) > 0:
                parts.append(str(s["reps"]))
        return f"{name} — {', '.join(parts)}"

    if is_bw:
        reps = group_reps_bw(sets)
        return f"{name} — bodyweight × {reps}"

    has_per_set_weight = any(s.get("weight", 0) > 0 for s in sets)

    if has_per_set_weight:
        return format_weighted(name, sets)

    if ex_weight and ex_weight > 0:
        reps = [str(s.get("reps", 0)) for s in sets if s.get("reps", 0) > 0]
        return f"{name} — {format_weight(ex_weight)}kg × {', '.join(reps)}"

    reps = group_reps_bw(sets)
    return f"{name} — bodyweight × {reps}"


def format_bilateral(name, ex, sets):
    wl = ex.get("weightL", 0)
    wr = ex.get("weightR", 0)
    reps_strs = [str(s.get("reps", 0)) for s in sets if s.get("reps", 0) > 0]
    reps = ", ".join(reps_strs)
    return (
        f"{name} — L {format_weight(wl)}kg × {reps}, "
        f"R {format_weight(wr)}kg × {reps}"
    )


def group_reps_bw(sets):
    reps = [s.get("reps", 0) for s in sets if s.get("reps", 0) > 0]
    return ", ".join(str(r) for r in reps)


def format_weighted(name, sets):
    groups = []
    i = 0
    while i < len(sets):
        s = sets[i]
        w = s.get("weight", 0)
        reps_at_weight = []
        while i < len(sets) and sets[i].get("weight", 0) == w:
            r = sets[i].get("reps", 0)
            if r > 0:
                reps_at_weight.append(str(r))
            i += 1
        if reps_at_weight:
            groups.append(f"{format_weight(w)}kg × {', '.join(reps_at_weight)}")

    return f"{name} — {', '.join(groups)}"


def append_to_log(entry_text):
    with open(LOG, "r") as f:
        content = f.read()

    baseline_marker = "<!-- Baseline at handover"
    if baseline_marker in content:
        pos = content.index(baseline_marker)
        before = content[:pos].rstrip()
        after = content[pos:]
        new_content = before + "\n\n" + entry_text + "\n\n" + after
    else:
        new_content = content.rstrip() + "\n\n" + entry_text + "\n"

    with open(LOG, "w") as f:
        f.write(new_content)


def load_rx():
    with open(INDEX, "r") as f:
        html = f.read()

    match = re.search(r"var RX\s*=\s*\{", html)
    if not match:
        return None

    start = match.start() + len("var RX = ")
    depth = 0
    end = start
    for i in range(start, len(html)):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    js_obj = html[start:end]
    json_str = js_obj
    json_str = re.sub(r'(?<=[{,\n])\s*(\w+)\s*:', r' "\1":', json_str)
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)
    json_str = json_str.replace("—", "—")
    json_str = re.sub(r':\s*"([^"]*)—([^"]*)"', r': "\1—\2"', json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def next_session_id(from_date_str):
    dt = datetime.strptime(from_date_str, "%Y-%m-%d")
    for offset in range(1, 8):
        candidate = dt + timedelta(days=offset)
        dow = candidate.weekday()
        py_to_js = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
        js_dow = py_to_js[dow]
        sid = SCHEDULE.get(js_dow)
        if sid and sid not in ("football", "rest"):
            return sid, candidate.strftime("%Y-%m-%d")
    return None, None


def build_state(data, rx):
    state = {}
    state["_generated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    state["_by"] = "drain.py"

    state["last_session"] = {
        "date": data["date"],
        "type": data.get("session_id", ""),
        "name": data.get("session", ""),
        "exercise_count": len(data.get("exercises", [])),
        "pain_right_lat": data.get("pain", {}).get("right_lat"),
    }

    top_sets = []
    for ex in data.get("exercises", []):
        sets = ex.get("sets", [])
        best_rep = max((s.get("reps", 0) for s in sets), default=0)
        w = ex.get("weight", 0)
        if ex.get("bodyweight"):
            w = "BW"
        elif "weightL" in ex:
            w = f"L{ex['weightL']}/R{ex['weightR']}"
        top_sets.append({
            "name": ex["name"],
            "weight": w,
            "best_reps": best_rep,
            "set_count": len(sets),
        })
    state["last_session"]["top_sets"] = top_sets

    nid, ndate = next_session_id(data["date"])
    state["next_session"] = {
        "type": nid,
        "name": SESSION_NAMES.get(nid, nid or "?"),
        "expected_date": ndate,
    }

    if rx and "sessions" in rx:
        slots = {}
        for sid, sdata in rx["sessions"].items():
            slot_list = []
            for ex in sdata.get("exercises", []):
                entry = {
                    "name": ex["name"],
                    "type": ex.get("type", "rotate"),
                    "sets": ex.get("sets", 3),
                    "reps": ex.get("reps", ""),
                    "load": ex.get("load", 0),
                    "unit": ex.get("unit", "kg"),
                }
                if ex.get("bilateral"):
                    entry["loadL"] = ex.get("loadL", 0)
                    entry["loadR"] = ex.get("loadR", 0)
                if ex.get("alts"):
                    entry["alts"] = ex["alts"]
                slot_list.append(entry)
            slots[sid] = slot_list
        state["slots"] = slots
        state["rx_asof"] = rx.get("asof", "")

    state["row_protocol"] = {
        "load_right": 50,
        "load_left": 60,
        "green_count": 0,
        "status": "zero greens since 09-17 reset",
    }

    state["flags"] = build_flags(data)

    return state


def build_flags(data):
    flags = []
    pain = data.get("pain", {}).get("right_lat")
    if pain is not None and pain > 3:
        flags.append(f"pain(R) {pain}/10 — amber, row protocol resets")
    elif pain is not None and pain <= 3 and pain > 0:
        flags.append(f"pain(R) {pain}/10 — green light")

    for ex in data.get("exercises", []):
        name = ex["name"]
        sets = ex.get("sets", [])
        if "Pull Up" in name:
            total = sum(s.get("reps", 0) for s in sets)
            top = max((s.get("reps", 0) for s in sets), default=0)
            flags.append(f"Pull-up: top set {top}, total {total}")

    return flags


def build_editorial(data, state):
    lines = []
    lines.append(f"Session: {data['date']} {data.get('session', '')}")
    lines.append(f"Exercises: {len(data.get('exercises', []))}")

    pain = data.get("pain", {}).get("right_lat")
    if pain is not None:
        if pain <= 3:
            lines.append(f"Pain(R): {pain}/10 — green")
        else:
            lines.append(f"Pain(R): {pain}/10 — AMBER")
    else:
        lines.append("Pain(R): not recorded")

    nxt = state.get("next_session", {})
    lines.append(f"Next: {nxt.get('name', '?')} ({nxt.get('expected_date', '?')})")

    if state.get("flags"):
        lines.append("Flags:")
        for f in state["flags"]:
            lines.append(f"  - {f}")

    return "\n".join(lines)


def main():
    files = find_inbox_files()
    if not files:
        print("Inbox empty — nothing to drain.")
        return

    rx = load_rx()

    for path in files:
        fname = os.path.basename(path)
        print(f"Draining {fname}...")

        data = parse_inbox(path)
        entry = to_log_entry(data)
        append_to_log(entry)
        print(f"  → appended to log.md")

        state = build_state(data, rx)
        with open(STATE, "w") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"  → state.json updated")

        editorial = build_editorial(data, state)
        print()
        print("--- editorial summary ---")
        print(editorial)
        print("---")
        print()
        print(f"Files to commit: log.md, state.json")
        print(f"Files to delete: {fname}")
        print(f"Commit subject: log: {data['date']} {data.get('session', '')}")


if __name__ == "__main__":
    main()
