#!/usr/bin/env python3
"""Strong export → data/history.json, the pre-log history the phone page's Progress tab reads.

    python3 history.py                         # latest data/strong_*.csv
    python3 history.py data/<export>.csv

Only sessions dated before the first log.md entry go in: from there on log.md is the
record (it is reconciled against the export), so nothing is counted twice. Run it when a
new export lands, after analyse.py (docs/workflows.md). Like the CSV, the output is for
the page, not for reading.

Format, kept small for a phone:
    {"_from": ..., "_generated": ..., "_until": "YYYY-MM-DD",
     "sessions": [["YYYY-MM-DD", "Workout Name",
                   [["Exercise", bw, [[kg, reps, secs, warm], ...]], ...]], ...]}
bw is 1 for a bodyweight lift, whose kg is then added load (+) or assistance (-).
Sessions are oldest first; exercises and sets keep the performed order.
"""
import glob
import json
import re
import sys
from datetime import datetime

import pandas as pd

OUT = "data/history.json"

# Sets Strong logged as added weight that were assistance. Triceps Dip at 40 → 33 → 26kg,
# Nov 2024 – Jan 2025, falling while reps held, alongside Pull Up (Assisted): read as the
# assisted-dip machine (2026-10-27, pending his confirmation).
ASSISTED_BEFORE = {"Triceps Dip": "2025-02-01"}


def first_log_date():
    with open("log.md") as f:
        text = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
    dates = re.findall(r"^## (\d{4}-\d{2}-\d{2}) ", text, flags=re.M)
    return min(dates)


def num(v):
    v = float(v)
    return int(v) if v == int(v) else round(v, 2)


def main(path):
    until = first_log_date()
    df = pd.read_csv(path)
    df["Exercise Name"] = df["Exercise Name"].str.strip()
    df["Weight"] = df["Weight"].fillna(0)
    df["Reps"] = df["Reps"].fillna(0)
    df["Seconds"] = df["Seconds"].fillna(0)
    df["row"] = range(len(df))
    df = df[df["Date"].str.slice(0, 10) < until]

    # Strong logs a bodyweight lift at 0kg, and added load as a positive weight. A lift is
    # bodyweight when most of its sets are at 0kg, or it is an assisted variant.
    zero = df.groupby("Exercise Name")["Weight"].apply(lambda s: (s == 0).mean())
    bw = {n: z >= 0.5 for n, z in zero.items()}
    assisted = {n: "assisted" in n.lower() for n in zero.index}

    sessions = []
    for date, sess in df.sort_values("row").groupby("Date", sort=False):
        exs = []
        for name, sets in sess.groupby("Exercise Name", sort=False):
            b = bw[name] or assisted[name]
            out = []
            for _, s in sets.iterrows():
                if not s.Reps and not s.Seconds:
                    continue
                helped = assisted[name] or s.Date[:10] < ASSISTED_BEFORE.get(name, "")
                kg = -s.Weight if helped else s.Weight
                out.append([num(kg), int(s.Reps), int(s.Seconds), int(str(s["Set Order"]) == "W")])
            if out:
                exs.append([name, int(b), out])
        if exs:
            sessions.append([date[:10], str(sess["Workout Name"].iloc[0]), exs])
    sessions.sort(key=lambda s: s[0])

    with open(OUT, "w") as f:
        json.dump({"_from": path, "_generated": datetime.now().isoformat(timespec="seconds"),
                   "_until": until, "sessions": sessions}, f, separators=(",", ":"), ensure_ascii=False)
    nsets = sum(len(e[2]) for s in sessions for e in s[2])
    print(f"{OUT}: {len(sessions)} sessions, {nsets} sets, "
          f"{sessions[0][0]} → {sessions[-1][0]} (log.md from {until})")


if __name__ == "__main__":
    exports = sys.argv[1:] or sorted(glob.glob("data/strong_*.csv"))[-1:]
    if not exports:
        sys.exit("no export in data/")
    main(exports[0])
