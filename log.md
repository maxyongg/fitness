# Session log

Append-only. Newest at the bottom. One block per session.

Format:

```
## YYYY-MM-DD · Day · Session name
pain(R): n/10 | note: free text
- Exercise — weight × reps, reps, reps
```

`pain(R)` is right-lat pain during the set, 0–10 — the same scale as the green-light
table in `plan.md` (≤3 is a green light). Omit the field entirely on days
where nothing pulled. Use `?` for anything unreadable in a screenshot rather than
guessing — the monthly CSV export corrects it.

Exercises are listed in the order they were performed. That ordering is data in this
project, not formatting — do not sort or regroup it.

---

## 2026-08-31 · Mon · Push
note: first session back after a two-week trip, still carrying fatigue. 17 sets, 1h 2m.
Finisher was 25/8/8 push-ups + pike + diamond + 3×1min plank — front-loaded, switching
to even sets from here. Finisher was not logged in Strong, so it does not appear in
the export or in any analysis.
- Incline Bench Press (Barbell) — 40kg × 8 (warm-up), 60kg × 8, 8, 8, 45kg × 12
- Arnold Press (Dumbbell) — 22kg × 7, 20kg × 7, 8
- Cable Crossover — 11.25kg × 10, 13.75kg × 10, 10
- Lateral Raise (Dumbbell) — 7kg × 15, 15, 15
- Triceps Dip — bodyweight × 10, 10, 10

<!-- Reconciled against data/strong_2026-08-31.csv on 2026-09-01: loads and reps filled
     in, and Cable Crossover moved ahead of Lateral Raise to match the performed order. -->

<!-- Baseline at handover, from the Strong export of 8 May 2024 – 31 Aug 2026:
     382 sessions · 7,323 working sets · 3.16 sessions/week lifetime, 2.67 over the last 12 weeks.
     e1RM: bench 93.3 · incline bench 82.3 · OHP 50.7 (peak 61.7 in Feb) · squat 95.0
     · RDL 95.0 · lat pulldown 92.4 (current quarter; lifetime best 97.5 in Q2) · barbell curl 39.7
     Pull-up: 27 reps total / top set 10 when performed 2nd in session.
     Single-arm iso-lateral row: 80kg mid-2025 → 50kg now. THE number to watch.
     (The Sep 2025 step down from 80kg is a form change, not the injury — his call,
      confirmed 2026-09-01. The right-lat injury is separate, from June 2026.)
     Legs: 6.9% of all working sets ever. Core: planks only, unlogged.
     Corrected 2026-09-01: legs read 7.5% here, analyse.py on this same export gives 6.9%. -->
