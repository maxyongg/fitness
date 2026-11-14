#!/usr/bin/env python3
"""Apple Health workouts (data/health.json) joined to log.md, for programming mode.

    python3 health.py                     # watch workouts, last 12 weeks
    python3 health.py --since 2026-09-01
    python3 health.py --all               # every app's workouts (Strong, the phone), all dates
    python3 health.py --curve             # plus each workout's heart rate, 5-minute means

Nights (sleep, HRV, resting heart rate, from the morning shortcut upload) print last.

Two things write data/health.json. After each watch workout, an iPhone shortcut uploads
the watch's heart rate and watch.py turns it into a summary (marked [shortcut]; its
minutes are elapsed time). Now and then, the phone page's Import tab reads the Health
app's full export on the phone, and that record replaces the shortcut's. Only workout
summaries reach the repo: no routes, no daily data. This script is how a session reads
the file: don't read the JSON by hand.

Per workout: minutes, active kcal, km, and heart rate from the watch: Apple's
average/min/max, plus minutes in 10-bpm bands (hr.bins, keyed by the band's lower bound).
The bands are raw on purpose: no max HR or zone model is assumed. Don't invent one; ask
him if zones ever matter.

With --curve, each workout that has one also prints its heart-rate curve
(data/hr/YYYY-MM.json, 15-second means) as 5-minute means from the start, so a session
can see a late fade or the football rotation without reading the file.

Football rows carry effort and load from log.md, so the watch reading sits next to his
own. Lifting rows carry the log's session name for that date. What the watch says is
context for the programme, not a target: see CLAUDE.md, "No target, no date".
"""
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2}) · (\w+) · (.+)$", re.M)
EFFORT = re.compile(r"^effort: (\d+)/10 \| (\d+) min \| load: (\d+)(?: \| ([^|\n]+))?", re.M)


def log_by_date(path):
    """{date: [{"name", "effort", "load", "where"}]} from log.md's headers."""
    text = re.sub(r"<!--.*?-->", "", open(path, encoding="utf-8").read(), flags=re.S)
    out = {}
    for m in HEADER.finditer(text):
        e = {"name": m.group(3).strip(), "effort": None, "load": None, "where": ""}
        nxt = text[m.end() + 1:].split("\n", 1)[0]
        f = EFFORT.match(nxt)
        if f:
            e.update(effort=int(f.group(1)), load=int(f.group(3)), where=(f.group(4) or "").strip())
        elif nxt.startswith("did not play"):
            e["effort"] = 0
        out.setdefault(m.group(1), []).append(e)
    return out


def bands(hr):
    b = (hr or {}).get("bins") or {}
    return " ".join(f"{k}:{b[k]:g}" for k in sorted(b, key=int))


def hr_txt(hr):
    if not hr:
        return "—"
    return f"{hr['avg']}/{hr['max']}" if hr.get("max") else str(hr["avg"])


def curve_line(w):
    """5-minute means of the workout's 15-second curve, or None."""
    try:
        c = json.load(open(os.path.join(HERE, "data", "hr", w["date"][:7] + ".json"),
                           encoding="utf-8"))["curves"].get(f"{w['date']} {w['start']}")
    except (OSError, ValueError, KeyError):
        return None
    if not c:
        return None
    out, bpm = [], c["bpm"]
    for i in range(0, len(bpm), 20):
        part = [v for v in bpm[i:i + 20] if v is not None]
        out.append(str(round(sum(part) / len(part))) if part else "·")
    return f"from {c['t0'][:5]}, per 5 min: " + " ".join(out)


def main():
    args = sys.argv[1:]
    show_all = "--all" in args
    since = (dt.date.today() - dt.timedelta(weeks=12)).isoformat()
    if "--since" in args:
        since = args[args.index("--since") + 1]
    if show_all and "--since" not in args:
        since = "0000"

    path = os.path.join(HERE, "data", "health.json")
    if not os.path.exists(path):
        print("No data/health.json yet. He imports it from the phone page: Import tab → Apple Health.")
        return
    data = json.load(open(path, encoding="utf-8"))
    log = log_by_date(os.path.join(HERE, "log.md"))

    ws = [w for w in data.get("workouts", []) if w["date"] >= since
          and (show_all or w.get("source") == "Apple Watch" or w.get("kind") == "football")]
    src = f"Health import of {data['exported']}" if data.get("exported") else "Shortcut uploads only, no Health import yet"
    print(f"{src} · {len(ws)} workouts since {since}"
          + ("" if show_all else " (watch only; --all for every app)"))

    for kind, title in (("football", "FOOTBALL"), ("lifting", "LIFTING"), ("other", "OTHER")):
        rows = [w for w in ws if w.get("kind") == kind]
        if not rows:
            continue
        print(f"\n{title}")
        for w in rows:
            day = dt.date.fromisoformat(w["date"]).strftime("%a")
            sessions = log.get(w["date"], [])
            if kind == "football":
                fb = next((s for s in sessions if s["name"] == "Football"), None)
                logged = ("not logged" if not fb else "did not play" if fb["effort"] == 0
                          else f"effort {fb['effort']}/10 load {fb['load']}")
                what = logged
            elif kind == "lifting":
                lift = next((s for s in sessions if s["name"] != "Football"), None)
                what = lift["name"] if lift else "no log entry"
            else:
                what = w.get("type", "")
            extra = []
            if w.get("km"):
                extra.append(f"{w['km']} km")
            if w.get("kcal"):
                extra.append(f"{w['kcal']} kcal")
            print(f"  {w['date']} {day} {w['start']}-{w['end']}  {what:<24} {w['min']:>3} min  "
                  f"HR {hr_txt(w.get('hr')):<8} {' · '.join(extra)}"
                  + ("" if w.get("source") == "Apple Watch" else f"  [{w.get('source')}]")
                  + ("  [shortcut: elapsed min]" if w.get("via") == "shortcut" else ""))
            if bands(w.get("hr")):
                print(f"      bands {bands(w.get('hr'))}")
            if "--curve" in args and curve_line(w):
                print(f"      curve {curve_line(w)}")

    lines = sleep_lines(data.get("nights", []), since)
    if lines:
        print("\nSLEEP (the night ending that morning)")
        print("\n".join(lines))


def sleep_lines(nights, since):
    """One line per night from `since`, then the average. represcribe.py puts these in the
    nightly brief."""
    ns = sorted((n for n in nights if n["date"] >= since), key=lambda n: n["date"])
    out = []
    for n in ns:
        day = dt.date.fromisoformat(n["date"]).strftime("%a")
        hr = n.get("hr") or {}
        out.append(f"  {n['date']} {day} {n['start']}-{n['end']}  {n['asleep'] // 60}h{n['asleep'] % 60:02d} asleep, "
                   f"{n.get('awake', 0)} min awake  HRV {n.get('hrv', '—')}  resting HR {n.get('rhr', '—')}"
                   + (f"  sleeping HR {hr['avg']} avg, {hr['low']} low" if hr else ""))
    if len(ns) > 1:
        avg = sum(n["asleep"] for n in ns) / len(ns)
        hrv = [n["hrv"] for n in ns if n.get("hrv")]
        avg = int(avg + 0.5)
        out.append(f"  average of {len(ns)}: {avg // 60}h{avg % 60:02d} asleep"
                   + (f", HRV {round(sum(hrv) / len(hrv))}" if hrv else ""))
    return out


def load_nights():
    try:
        return json.load(open(os.path.join(HERE, "data", "health.json"), encoding="utf-8")).get("nights", [])
    except (OSError, ValueError):
        return []


if __name__ == "__main__":
    main()
