#!/usr/bin/env python3
"""Shortcut uploads from the watch (inbox/watch-*.txt) → workout summaries in data/health.json.

    python3 watch.py            # every inbox/watch-*.txt; the Watch upload Action runs this
    python3 watch.py FILE ...   # just these, left in place (for testing)
    python3 watch.py --from-git # curves for data/health.json's workouts, rebuilt from the
                                # uploads in git history; health.json itself is untouched

The iPhone shortcut ("Matchday watch", set up in docs/workflows.md) runs when a watch
workout ends, or by hand. Shortcuts can't read a workout record out of Health, only
samples, so it sends the watch's heart-rate readings, each with
its time, and optionally the active-energy readings, for the last day (Shortcuts' date
filters can't go shorter). The file looks like:

    matchday-watch 1
    sent: <date>
    hr:
    <one bpm per line>
    times:
    <one date per line, same order>
    kcal:            (optional)
    <one kcal per line>
    kcal times:
    <one date per line>

A variable may sit on its label's line ("hr: <first bpm>", then one per line), which is
how his Text action is laid out (2026-11-05). The dates are however Shortcuts prints
them on his phone (ISO, "30 Oct 2026 at 8:03 PM",
"Today at 20:03", with or without seconds), so parse_when() takes any of those.

A workout shows up as a block of dense readings: about one every 5s while a workout is
recording, against one every few minutes otherwise. A minute with 3+ readings is
dense; dense minutes with gaps of up to 10 minutes are one block, and a block of 10+
dense minutes is a workout. Its summary has the same shape as the Health-export import
(index.html, Import tab), plus "via": "shortcut". `min` here is elapsed time, start to
end; the export's is workout time, which leaves out pauses.

Merging: an export record (no "via") for the same stretch of time always wins. A newer
shortcut record replaces an older one for the same stretch, since a later upload has had
longer for the watch to sync. A file that can't be read stays in inbox/ and the exit
code is 1.

The curve: each workout's heart rate as 15-second means, for the page's graph, kept in
data/hr/YYYY-MM.json under the workout's "date start" (as data/health.json has it). Only
the workout's own minutes; the rest of the upload (the night, the day) is dropped with
the inbox file. An export record without a curve takes the shortcut's for the same
stretch. A curve whose workout is no longer in health.json is pruned.
"""
import datetime as dt
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HEALTH = os.path.join(ROOT, "data", "health.json")
CURVES = os.path.join(ROOT, "data", "hr")
STEP = 15                                   # seconds per curve point
CURVE_NOTE = ("Heart rate per workout as 15-second means (bpm; null where the watch has no reading), "
              "from t0. Keyed by the workout's date and start in data/health.json. Workout minutes "
              "only. Shortcut uploads time readings to the minute, so within a minute their place is "
              "spread evenly. Written by watch.py and the page's Health import; read via health.py --curve.")
SGT = dt.timezone(dt.timedelta(hours=8))
MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
HEALTH_BY = "index.html (Apple Health import) + watch.py (shortcut uploads)"
HEALTH_NOTE = ("Workout summaries only. hr.bins: minutes per 10-bpm band, keyed by its lower bound. "
               "via: shortcut = from a Shortcut upload, where min is elapsed time. Read via health.py. "
               "Each workout's heart-rate curve is in data/hr/YYYY-MM.json.")
DENSE_PER_MIN, MAX_GAP_MIN, MIN_DENSE_MIN, MIN_FOOTBALL_OVERLAP = 3, 10, 10, 45

TIME_RE = re.compile(r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([ap])?\.?\s*m?\.?(?![a-z])", re.I)
LABEL_RE = re.compile(r"^(kcal\s+times|times|kcal|hr|sent)\s*:\s*(.*)$", re.I)
ISO_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?(?:\.\d+)?\s*(Z|[+-]\d{2}:?\d{2})?")


def parse_when(text, ref):
    """A date as Shortcuts printed it → aware datetime (SGT unless it says otherwise).
    ref is roughly when it was sent: it settles "Today"/"Yesterday", a missing year, and
    whether 03/11 is 3 Nov or 11 Mar (whichever lands nearer ref)."""
    s = text.replace(" ", " ").replace(" ", " ").strip()
    m = ISO_RE.search(s)
    if m:
        y, mo, d, h, mi, sec, tz = m.groups()
        if tz in (None, ""):
            tzinfo = SGT
        elif tz == "Z":
            tzinfo = dt.timezone.utc
        else:
            tz = tz.replace(":", "")
            tzinfo = dt.timezone((1 if tz[0] == "+" else -1) * dt.timedelta(hours=int(tz[1:3]), minutes=int(tz[3:5])))
        return dt.datetime(int(y), int(mo), int(d), int(h), int(mi), int(sec or 0), tzinfo=tzinfo).astimezone(SGT)

    t = TIME_RE.search(s)
    if not t:
        return None
    h, mi, sec, ap = int(t.group(1)), int(t.group(2)), int(t.group(3) or 0), (t.group(4) or "").lower()
    if ap == "p" and h < 12:
        h += 12
    elif ap == "a" and h == 12:
        h = 0
    rest = (s[:t.start()] + " " + s[t.end():]).lower()

    if "today" in rest or "yesterday" in rest:
        day = ref.date() - dt.timedelta(days=1 if "yesterday" in rest else 0)
        return dt.datetime(day.year, day.month, day.day, h, mi, sec, tzinfo=SGT)

    candidates = []
    word = re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", rest)
    if word:
        nums = [int(n) for n in re.findall(r"\d+", rest)]
        day = next((n for n in nums if 1 <= n <= 31), None)
        year = next((n for n in nums if n >= 1000), None)
        if day is not None:
            years = [year] if year else [ref.year, ref.year - 1]
            candidates = [(yy, MONTHS[word.group(1)], day) for yy in years]
    else:
        nums = [int(n) for n in re.findall(r"\d+", rest)]
        if len(nums) >= 2:
            a, b = nums[0], nums[1]
            year = nums[2] if len(nums) > 2 else ref.year
            year = year + 2000 if year < 100 else year
            candidates = [(year, b, a), (year, a, b)]      # day-first first: en_SG
    best = None
    for y, mo, d in candidates:
        try:
            when = dt.datetime(y, mo, d, h, mi, sec, tzinfo=SGT)
        except ValueError:
            continue
        if best is None or abs((when - ref).total_seconds()) < abs((best - ref).total_seconds()) - 86400:
            best = when
    return best


def read_upload(path, ref):
    """inbox file → (heart-rate [(datetime, bpm)], energy [(datetime, kcal)])."""
    sections, cur = {}, None
    for raw in open(path, encoding="utf-8-sig"):
        line = raw.strip()
        label = LABEL_RE.match(line)
        if label:
            key, rest = re.sub(r"\s+", " ", label.group(1).lower()), label.group(2).strip()
            if key == "sent":
                ref = parse_when(rest, ref) or ref
                cur = None
                continue
            cur = sections.setdefault(key, [])
            if rest:                     # "hr: 152": the list's first item shares the label's line
                cur.append(rest)
        elif line and cur is not None:
            cur.append(line)

    def pairs(values, times):
        if len(values) != len(times):
            raise ValueError(f"{len(values)} values but {len(times)} times")
        out = []
        for v, t in zip(values, times):
            num = re.search(r"\d+(?:[.,]\d+)?", v)
            when = parse_when(t, ref)
            if not num or not when:
                raise ValueError(f"can't read {v!r} at {t!r}")
            out.append((when, float(num.group(0).replace(",", "."))))
        # By time only: the sort is stable, so readings that share a minute (his phone
        # prints no seconds) keep the order the watch recorded them in. make_curve needs it.
        return sorted(out, key=lambda p: p[0])

    if "hr" not in sections or "times" not in sections:
        raise ValueError("no hr:/times: sections, so not a shortcut upload")
    hr = pairs(sections["hr"], sections["times"])
    kcal = pairs(sections.get("kcal", []), sections.get("kcal times", [])) if "kcal" in sections else []
    return hr, kcal


def blocks(hr):
    """Runs of dense minutes → [(start, end)] of each workout."""
    per_min = {}
    for when, _ in hr:
        per_min.setdefault(when.replace(second=0, microsecond=0), []).append(when)
    dense = sorted(m for m, ws in per_min.items() if len(ws) >= DENSE_PER_MIN)
    runs, cur = [], []
    for m in dense:
        if cur and (m - cur[-1]).total_seconds() / 60 > MAX_GAP_MIN:
            runs.append(cur)
            cur = []
        cur.append(m)
    if cur:
        runs.append(cur)
    return [(min(per_min[r[0]]), max(per_min[r[-1]])) for r in runs if len(r) >= MIN_DENSE_MIN]


def summarise(start, end, hr, kcal, rx):
    inside = [(w, v) for w, v in hr if start <= w <= end]
    seconds = any(w.second for w, _ in inside)
    per_min = {}
    for w, _ in inside:
        k = w.replace(second=0)
        per_min[k] = per_min.get(k, 0) + 1
    weights = []
    for i, (w, v) in enumerate(inside):
        if seconds:
            nxt = inside[i + 1][0] if i + 1 < len(inside) else end
            weights.append(min((nxt - w).total_seconds(), 60))
        else:          # minute-resolution times: share the minute among its readings
            weights.append(60 / per_min[w.replace(second=0)])
    total = sum(weights) or 1
    bins = {}
    for (w, v), wt in zip(inside, weights):
        b = int(v // 10 * 10)
        bins[b] = bins.get(b, 0) + wt
    vals = [v for _, v in inside]
    rec = {
        "date": start.date().isoformat(), "start": start.strftime("%H:%M"), "end": end.strftime("%H:%M"),
        "kind": kind(start, end, rx), "type": "Workout", "source": "Apple Watch", "via": "shortcut",
        "min": round((end - start).total_seconds() / 60),
    }
    energy = sum(v for w, v in kcal if start <= w <= end)
    if energy > 0:
        rec["kcal"] = round(energy)
    rec["hr"] = {
        "avg": round(sum(v * wt for (_, v), wt in zip(inside, weights)) / total),
        "min": round(min(vals)), "max": round(max(vals)), "n": len(inside),
        "bins": {str(k): round(bins[k] / 60, 1) for k in sorted(bins) if bins[k] / 60 >= 0.1},
    }
    return rec


def make_curve(start, end, hr):
    """15-second means of the readings from start to end: {"t0": "HH:MM:SS", "bpm": [...]}.
    When the times carry no seconds (how his phone prints them), each minute's readings are
    spread evenly across that minute, in the order the watch took them: the values are the
    watch's, only their place inside the minute is estimated."""
    inside = [(w, v) for w, v in hr if start <= w <= end]
    if inside and not any(w.second for w, _ in inside):
        per_min = {}
        for w, v in inside:
            per_min.setdefault(w, []).append(v)
        inside = [(m + dt.timedelta(seconds=(i + 0.5) * 60 / len(vs)), v)
                  for m, vs in per_min.items() for i, v in enumerate(vs)]
    n = int((end - start).total_seconds() // STEP) + 4
    sums, counts = [0.0] * n, [0] * n
    for when, v in inside:
        i = int((when - start).total_seconds() // STEP)
        if 0 <= i < n:
            sums[i] += v
            counts[i] += 1
    bpm = [round(t / c) if c else None for t, c in zip(sums, counts)]
    while bpm and bpm[-1] is None:
        bpm.pop()
    return {"t0": start.strftime("%H:%M:%S"), "bpm": bpm}


def curve_key(w):
    return f"{w['date']} {w['start']}"


def load_curves(month):
    try:
        return json.load(open(os.path.join(CURVES, month + ".json"), encoding="utf-8")).get("curves", {})
    except (OSError, ValueError):
        return {}


def save_curves(month, curves):
    os.makedirs(CURVES, exist_ok=True)
    head = [f'  "_note": {json.dumps(CURVE_NOTE)},', f'  "step": {STEP},']
    body = ",\n".join(f"    {json.dumps(k)}: {json.dumps(curves[k], separators=(',', ':'))}"
                      for k in sorted(curves))
    with open(os.path.join(CURVES, month + ".json"), "w", encoding="utf-8") as f:
        f.write("{\n" + "\n".join(head) + '\n  "curves": {\n' + body + "\n  }\n}\n")


def store_curves(new, workouts):
    """new: {key: curve}. Writes each touched month, pruning curves with no workout."""
    keep = {curve_key(w) for w in workouts}
    for month in sorted({k[:7] for k in new}):
        curves = load_curves(month)
        curves.update({k: v for k, v in new.items() if k[:7] == month})
        save_curves(month, {k: v for k, v in curves.items() if k in keep})


def kind(start, end, rx):
    """Football fills 45+ minutes of an RX.football slot; otherwise a lift day's workout is lifting."""
    js_dow = str((start.weekday() + 1) % 7)
    fb = (rx or {}).get("football", {}).get(js_dow)
    if fb:
        lo = start.replace(hour=int(fb["start"][:2]), minute=int(fb["start"][3:]), second=0)
        hi = start.replace(hour=int(fb["end"][:2]), minute=int(fb["end"][3:]), second=0)
        if (min(end, hi) - max(start, lo)).total_seconds() / 60 >= MIN_FOOTBALL_OVERLAP:
            return "football"
    session = (rx or {}).get("schedule", {}).get(js_dow, "")
    return "lifting" if session.startswith(("upper", "lower")) else "other"


def span(w):
    s = dt.datetime.fromisoformat(w["date"] + "T" + w["start"])
    e = dt.datetime.fromisoformat(w["date"] + "T" + w["end"])
    return s, e + dt.timedelta(days=1) if e < s else e


def merge(workouts, new):
    """Add one shortcut record. Returns what happened, for the summary line, and the
    record that now stands for that stretch of time (its curve goes under its key)."""
    ns, ne = span(new)
    for i, w in enumerate(workouts):
        ws, we = span(w)
        if ws < ne and ns < we:
            if not w.get("via"):
                return "already in the Health import", w
            workouts[i] = new
            return "updated", new
    workouts.append(new)
    return "added", new


def load_health():
    try:
        return json.load(open(HEALTH, encoding="utf-8"))
    except (OSError, ValueError):
        return {"workouts": []}


def save_health(data):
    data["workouts"].sort(key=lambda w: w["date"] + w["start"])
    head = {
        "_generated": dt.datetime.now(SGT).strftime("%Y-%m-%dT%H:%M:%S"),
        "_by": HEALTH_BY,
        "_note": HEALTH_NOTE,
        "exported": data.get("exported", ""),
    }
    lines = [f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}," for k, v in head.items()]
    body = ",\n".join("    " + json.dumps(w, separators=(",", ":"), ensure_ascii=False) for w in data["workouts"])
    os.makedirs(os.path.dirname(HEALTH), exist_ok=True)
    with open(HEALTH, "w", encoding="utf-8") as f:
        f.write("{\n" + "\n".join(lines) + '\n  "workouts": [\n' + body + "\n  ]\n}\n")


def from_git():
    """Every upload the Action ever processed is still in git history (committed to inbox/,
    then deleted). Rebuild the curve of each Apple Watch workout in health.json from the
    newest upload that covers it. For curves the Action didn't keep, or a format fix."""
    import subprocess
    import tempfile
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    uploads, sha = [], None
    for line in git("log", "--diff-filter=A", "--format=%H %cI", "--name-only", "--", "inbox/watch-*.txt").splitlines():
        if line.startswith("inbox/"):
            uploads.append((sha[1], sha[0], line))
        elif line.strip():
            sha = line.split()
    data, found = load_health(), {}
    watch_ws = [w for w in data["workouts"] if w.get("source") == "Apple Watch"]
    with tempfile.TemporaryDirectory() as tmp:
        for when, commit, path in sorted(uploads):
            f = os.path.join(tmp, "upload.txt")
            with open(f, "w", encoding="utf-8") as out:
                out.write(git("show", f"{commit}:{path}"))
            try:
                hr, _ = read_upload(f, dt.datetime.fromisoformat(when).astimezone(SGT))
            except ValueError as e:
                print(f"{path}: can't read it ({e})")
                continue
            for start, end in blocks(hr):
                ns, ne = span({"date": start.date().isoformat(), "start": start.strftime("%H:%M"),
                               "end": end.strftime("%H:%M")})
                match = [w for w in watch_ws if span(w)[0] < ne and ns < span(w)[1]]
                if match:
                    found[curve_key(match[0])] = make_curve(start, end, hr)
    if found:
        store_curves(found, data["workouts"])
    print(f"Curves from git history: {len(found)} ({', '.join(sorted(found)) or 'none'})")
    return 0


def main():
    args = sys.argv[1:]
    if args == ["--from-git"]:
        return from_git()
    files = args or sorted(glob.glob(os.path.join(ROOT, "inbox", "watch-*.txt")))
    if not files:
        print("No watch uploads in inbox/.")
        return 0
    try:
        sys.path.insert(0, ROOT)
        from drain import load_rx
        rx = load_rx()
    except Exception as e:                       # football falls back to "other" if RX won't parse
        print(f"RX unreadable ({e}); kinds are guesses.")
        rx = None

    data, bad, subjects, curves = load_health(), 0, [], {}
    for path in files:
        name = os.path.basename(path)
        ref = dt.datetime.fromtimestamp(os.path.getmtime(path), SGT)
        try:
            hr, kcal = read_upload(path, ref)
        except (OSError, ValueError) as e:
            print(f"{name}: can't read it ({e}). Left in inbox/.")
            bad += 1
            continue
        found = blocks(hr)
        if not hr:
            print(f"{name}: no heart-rate readings in it (phone locked when it ran?).")
        elif not found:
            print(f"{name}: {len(hr)} readings, {hr[0][0]:%d %b %H:%M}–{hr[-1][0]:%H:%M}, but no workout among them.")
        for start, end in found:
            rec = summarise(start, end, hr, kcal, rx)
            what, kept = merge(data["workouts"], rec)
            print(f"{name}: {rec['date']} {rec['start']}–{rec['end']} {rec['kind']}, {rec['min']} min, "
                  f"HR {rec['hr']['avg']} avg / {rec['hr']['max']} max ({rec['hr']['n']} readings): {what}")
            if kept is rec or curve_key(kept) not in load_curves(kept["date"][:7]):
                curves[curve_key(kept)] = make_curve(start, end, hr)
            if what != "already in the Health import":
                subjects.append(f"{rec['date']} {rec['kind']}")
        if not args:
            os.remove(path)
    if subjects:
        save_health(data)
    if curves:
        store_curves(curves, data["workouts"])
    subject = "health: watch " + (", ".join(dict.fromkeys(subjects)) if subjects else "upload, nothing new")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"subject={subject}\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
