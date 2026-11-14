#!/usr/bin/env python3
"""The load review and the session picker, both read from log.md.

    python3 review.py            # every slot: status, last readings, best, swaps
    python3 review.py --next     # the session the page opens next

drain.py writes `review`, `last_done` and `next_session` into state.json after every
drain, and represcribe.py after every re-prescription; the nightly brief gets the review
as text; the page shows it on each slot and in Progress → Lifts. One calculation, three
readers.

THE REVIEW. Per RX slot, the readings of that exact exercise (machine identity is
part of the measurement, so "Lateral Raise (Cable)" is never read against the
dumbbell). A reading is one session's working sets. Progress is a new best:
  - weighted: a best-set e1RM (Epley, as analyse.py) at least 1% over the previous
    best, or more total reps at a top load done before;
  - bodyweight: more added load, or more total reps at the same added load;
  - holds: more total time.
Status: `new` (under 3 readings), `moving` (the latest is a best), `holding` (1–2
since the best), `flat` (3+ since the best). `top` is separate: the latest reading
hit the top of the band on every set at its top load, so a progression rule may fire.
plan.md's rules decide the step; this only reports. Readings inside a re-entry phase
(loads cut on purpose) are shown but never set a best or count towards flat.
None of this calls anything a decline: CLAUDE.md, "A load reset after a form change
is not a decline".

THE PICKER. Which session he trains next: Lower on Sunday if it isn't done that week
(never chased on other days, never displaced). Otherwise, of the upper sessions due
by that day and not done this week, the one gone longest. A missed Monday makes
Thursday Upper A and Saturday Upper B, and Upper C drops for the week, which is the
call he made by hand on 2026-11-11. On a lift day with nothing due, the next session
not done this week is pulled forward. index.html and widget/matchday.js run the same
rule; keep the three in step.
"""
import json
import os
import re
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, "log.md")

# plan.md, Phases: loads deliberately cut, so no reading here is a best or a stall.
REENTRY = [("2026-08-31", "2026-09-13"), ("2026-10-19", "2026-10-25")]

ORDER = ["upper_a", "upper_b", "upper_c", "lower"]
NAMES = {"upper_a": "Upper A", "upper_b": "Upper B", "upper_c": "Upper C", "lower": "Lower"}
SCHEDULE = {1: "upper_a", 2: "football", 3: "rest", 4: "upper_b", 5: "football", 6: "upper_c", 0: "lower"}
LAST_SHOWN = 4

HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2}) · \w+ · (.+?)\s*$")
SET_RE = re.compile(r"^(?:(bodyweight|BW|[+-]?\d+(?:\.\d+)?\s*kg)\s*[×x]\s*)?(\d+:\d{2}|\d+|\?)\s*(\((?:warm-up|w)\))?$", re.I)


# ---------- log.md ----------

def parse_log(text):
    """[{date, name, exs: [{name, sets: [{kg, bw, reps, secs, warm}]}]}], oldest first.
    The same reading of a line as parseExLine() in index.html."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for block in re.split(r"\n(?=## \d{4}-\d{2}-\d{2} )", text):
        lines = block.strip("\n").split("\n")
        m = HEADER.match(lines[0])
        if not m:
            continue
        exs = [e for e in (parse_ex(l) for l in lines[1:] if re.match(r"^- .+ — ", l)) if e]
        out.append({"date": m.group(1), "name": m.group(2), "exs": exs})
    out.sort(key=lambda s: s["date"])
    return out


def parse_ex(line):
    i = line.index(" — ")
    name = line[2:i].strip()
    if not name or name == "?":
        return None
    kg, bw, sets = None, True, []
    for tok in line[i + 3:].split(" | note:")[0].split(","):
        m = SET_RE.match(tok.strip())
        if not m:
            continue
        if m.group(1):
            load = re.sub(r"\s", "", m.group(1))
            if load.lower() in ("bodyweight", "bw"):
                kg, bw = 0.0, True
            else:
                kg, bw = float(load[:-2]), load[0] in "+-"
        if m.group(2) == "?":
            continue
        t = m.group(2).split(":")
        sets.append({"kg": kg or 0.0, "bw": bw, "reps": 0 if len(t) > 1 else int(t[0]),
                     "secs": int(t[0]) * 60 + int(t[1]) if len(t) > 1 else 0, "warm": bool(m.group(3))})
    return {"name": name, "sets": sets} if sets else None


def read_log(path=LOG):
    with open(path, encoding="utf-8") as f:
        return parse_log(f.read())


# ---------- one session's reading of one exercise ----------

def key(name):
    return re.sub(r"\s+", " ", name.lower().replace("-", " ")).strip()


def matches(log_name, rx_name):
    """Same exercise: the name itself, or a variant of it ("Face Pull" → "Face Pull (Cable)")."""
    a, b = key(log_name), key(rx_name)
    return a == b or a.startswith(b + " (")


def working(sets):
    """Sets that count as work: not marked warm-up, and not a lead-in at two-thirds of the
    day's top load or less (the 40kg × 10 before a 65kg incline). workingSets() in index.html."""
    top = max((s["kg"] for s in sets if not s["bw"]), default=0)
    out, lead = [], True
    for s in sets:
        if s["warm"]:
            continue
        if lead and top and not s["bw"] and s["kg"] <= top * 2 / 3:
            continue
        lead = False
        out.append(s)
    return out


def fmt_kg(v):
    return f"{v:g}"


def reading(ex):
    """{kind, top, reps (at the top load), e1rm, secs, text}, or None with no work in it."""
    sets = working(ex["sets"])
    if not sets:
        return None
    if all(s["secs"] for s in sets):
        total = sum(s["secs"] for s in sets)
        return {"kind": "time", "top": 0, "reps": [], "secs": total, "e1rm": 0,
                "text": ", ".join(f"{s['secs'] // 60}:{s['secs'] % 60:02d}" for s in sets)}
    sets = [s for s in sets if s["reps"]]
    if not sets:
        return None
    bw = all(s["bw"] for s in sets)
    top = max(s["kg"] for s in sets)
    reps = [s["reps"] for s in sets if s["kg"] == top]
    if bw:
        load = "BW" if top == 0 else f"{'+' if top > 0 else ''}{fmt_kg(top)}kg"
        return {"kind": "bw", "top": top, "reps": reps, "secs": 0, "e1rm": 0,
                "text": f"{load} × {', '.join(map(str, reps))}"}
    e1rm = max(s["kg"] * (1 + s["reps"] / 30) for s in sets if not s["bw"])
    return {"kind": "kg", "top": top, "reps": reps, "secs": 0, "e1rm": round(e1rm, 1),
            "text": f"{fmt_kg(top)}kg × {', '.join(map(str, reps))}"}


def beats(r, prior):
    """Is reading r a new best against the earlier counted readings?"""
    if not prior:
        return True
    if r["kind"] == "time":
        return r["secs"] > max(p["secs"] for p in prior)
    same = [sum(p["reps"]) for p in prior if p["top"] == r["top"]]
    if same and sum(r["reps"]) > max(same):
        return True
    if r["kind"] == "bw":
        return r["top"] > max(p["top"] for p in prior)
    return r["e1rm"] >= max(p["e1rm"] for p in prior) * 1.01


def band(reps):
    """"8-10" → (8, 10), "5" → (5, 5); AMRAP and holds have none."""
    m = re.match(r"^(\d+)(?:-(\d+))?$", str(reps).strip())
    return (int(m.group(1)), int(m.group(2) or m.group(1))) if m else None


def in_reentry(d):
    return any(a <= d <= b for a, b in REENTRY)


def md(d):
    return d[5:]


# ---------- the review ----------

def shared_names(rx):
    """RX exercise names that appear in more than one session (pull-ups, lateral raise):
    their prescriptions differ by day, so their readings are kept to their own session."""
    seen = {}
    for sid, s in rx["sessions"].items():
        for ex in s["exercises"]:
            seen.setdefault(key(ex["name"]), set()).add(sid)
    return {k for k, v in seen.items() if len(v) > 1}


def entries(log, rx_name, session_name=None):
    """[(date, session name, exercise)] for every logged variant of rx_name, oldest first."""
    out = []
    for s in log:
        if session_name and s["name"] != session_name:
            continue
        for ex in s["exs"]:
            if matches(ex["name"], rx_name):
                out.append((s["date"], s["name"], ex))
    return out


def review_slot(log, rx, sid, idx, shared):
    ex = rx["sessions"][sid]["exercises"][idx]
    sname = rx["sessions"][sid].get("name", NAMES.get(sid, sid))
    own = key(ex["name"]) in shared
    found = entries(log, ex["name"], sname if own else None)
    here = [e for e in found if e[1] == sname] or found
    variant = here[-1][2]["name"] if here else ex["name"]
    rows = []
    for d, _, e in found:
        if e["name"] != variant:
            continue
        r = reading(e)
        if r:
            rows.append(dict(r, date=d, reentry=in_reentry(d)))

    counted, best, since = [], None, 0
    for r in rows:
        if r["reentry"]:
            continue
        if beats(r, counted):
            best, since = r, 0
        else:
            since += 1
        counted.append(r)

    if len(counted) < 3:
        status = "new"
    elif since == 0:
        status = "moving"
    elif since >= 3:
        status = "flat"
    else:
        status = "holding"

    b, need = band(ex.get("reps", "")), min(int(ex.get("sets", 3)), 3)
    streak = 0
    if b:
        for r in reversed(counted):
            if (r["kind"] != "time" and len(r["reps"]) >= need and min(r["reps"]) >= b[1]
                    and (not streak or r["top"] == counted[-1]["top"])):
                streak += 1
            else:
                break

    # The newest session of this slot's day that didn't run it: a dropped slot is not a reading.
    same_day = [s for s in log if s["name"] == sname]
    not_run = None
    if same_day and not any(matches(e["name"], ex["name"]) or any(matches(e["name"], a) for a in ex.get("alts", []))
                            for e in same_day[-1]["exs"]):
        not_run = same_day[-1]["date"]

    alts = []
    for a in ex.get("alts", []):
        hit = entries(log, a)
        r = None
        for d, _, e in reversed(hit):
            r = reading(e)
            if r:
                alts.append({"name": a, "logged_as": e["name"], "date": d, "text": r["text"]})
                break
        if not r:
            alts.append({"name": a, "date": None, "text": "never logged"})

    out = {
        "slot": idx + 1, "name": ex["name"], "logged_as": variant, "type": ex.get("type", "rotate"),
        "status": status, "since_best": since if counted else 0, "top_streak": streak,
        "best": {"date": best["date"], "text": best["text"]} if best else None,
        "last": [f"{md(r['date'])} {r['text']}" + (" (re-entry)" if r["reentry"] else "")
                 for r in reversed(rows[-LAST_SHOWN:])],
        "readings": len(counted),
    }
    if not_run:
        out["not_run"] = not_run
    if alts:
        out["alts"] = alts
    out["line"] = line(out)
    return out


def line(r):
    """One sentence for the page and the brief."""
    best = r["best"]
    if r["readings"] == 0:
        s = "No reading on this exercise in log.md yet."
    elif r["status"] == "new":
        s = f"{r['readings']} reading{'s' if r['readings'] > 1 else ''} so far, too few to call a trend."
    elif r["status"] == "moving":
        s = f"New best last time: {best['text']} ({md(best['date'])})."
    elif r["status"] == "flat":
        s = f"No new best in {r['since_best']} sessions since {md(best['date'])} ({best['text']})."
    else:
        s = f"{r['since_best']} session{'s' if r['since_best'] > 1 else ''} since the best, {best['text']} ({md(best['date'])})."
    if r["top_streak"]:
        s += f" Top of the band on every set, {r['top_streak']} session{'s' if r['top_streak'] > 1 else ''} running."
    if r.get("not_run"):
        s += f" Not run {md(r['not_run'])}."
    return s


def review(log, rx):
    shared = shared_names(rx)
    return {sid: [review_slot(log, rx, sid, i, shared) for i in range(len(s["exercises"]))]
            for sid, s in rx["sessions"].items()}


def review_text(rev, rx):
    """The block the nightly brief gets."""
    out = []
    for sid in ORDER:
        if sid not in rev:
            continue
        out.append(rx["sessions"][sid].get("name", NAMES[sid]))
        for r in rev[sid]:
            tag = r["status"].upper() + (" · TOP" if r["top_streak"] else "")
            name = r["name"] + (f" [logged as {r['logged_as']}]" if r["logged_as"] != r["name"] else "")
            out.append(f"  {r['slot']}. {name} ({r['type']}) — {tag}. {r['line']}")
            if r["last"]:
                out.append(f"     last: {' · '.join(r['last'])}")
            if r.get("alts"):
                out.append("     swaps: " + "; ".join(
                    f"{a['name']} {md(a['date'])} {a['text']}" if a["date"] else f"{a['name']} (never logged)"
                    for a in r["alts"]))
    return "\n".join(out)


# ---------- the picker ----------

def last_done(log):
    """{session id: date of its newest log entry}."""
    ids = {v: k for k, v in NAMES.items()}
    out = {}
    for s in log:
        sid = ids.get(s["name"])
        if sid:
            out[sid] = max(out.get(sid, ""), s["date"])
    return out


def _dow(d):
    return (d.weekday() + 1) % 7          # JS getDay(): Sunday 0


def _offset(dow):
    return (dow + 6) % 7                  # Monday 0 … Sunday 6


def pick(day, done, schedule=SCHEDULE, pull_forward=False):
    """The session for `day`, or None if none is due then. `done` is last_done()."""
    monday = (day - timedelta(days=_offset(_dow(day)))).isoformat()
    when = {sid: dow for dow, sid in schedule.items() if sid in NAMES}
    this_week = lambda sid: done.get(sid, "") >= monday
    if schedule.get(_dow(day)) == "lower" and not this_week("lower"):
        return "lower"
    due = [sid for sid in ORDER if sid != "lower" and sid in when
           and _offset(when[sid]) <= _offset(_dow(day)) and not this_week(sid)]
    if due:
        return min(due, key=lambda sid: (done.get(sid, ""), ORDER.index(sid)))
    if pull_forward:
        rest = [sid for sid in ORDER if sid in when and not this_week(sid)]
        if rest:
            return min(rest, key=lambda sid: (_offset(when[sid]), ORDER.index(sid)))
    return None


def pick_next(today, done, schedule=SCHEDULE, lifted_today=False):
    """(session id, date) the page opens: today if it's a lift day with no lift logged
    yet, else the next lift day that has one due."""
    for i in range(8):
        day = today + timedelta(days=i)
        if schedule.get(_dow(day)) not in NAMES or (i == 0 and lifted_today):
            continue
        sid = pick(day, done, schedule, pull_forward=(i == 0))
        if sid:
            return sid, day.isoformat()
    return ORDER[0], None


def schedule_of(rx):
    return {int(k): v for k, v in (rx or {}).get("schedule", {}).items()} or SCHEDULE


def next_after(log, after_date, rx=None):
    """The session after one logged on after_date (that day's lift is done)."""
    d = date.fromisoformat(after_date)
    return pick_next(d, last_done(log), schedule_of(rx), lifted_today=True)


# ---------- command line ----------

def main():
    sys.path.insert(0, ROOT)
    import drain
    rx, log = drain.load_rx(), read_log()
    if "--next" in sys.argv:
        done = last_done(log)
        today = date.today()
        lifted = any(s["date"] == today.isoformat() and s["name"] in NAMES.values() for s in log)
        sid, when = pick_next(today, done, schedule_of(rx), lifted_today=lifted)
        print(f"Next: {NAMES[sid]} on {when}")
        print("Last done: " + ", ".join(f"{NAMES[k]} {v}" for k, v in sorted(done.items(), key=lambda x: ORDER.index(x[0]))))
        return
    print(review_text(review(log, rx), rx))


if __name__ == "__main__":
    main()
