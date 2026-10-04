# What the data supports — and what it doesn't

Everything here came out of `analyse.py` on the Strong export. The headline is in
`CLAUDE.md`; this is the working. **`docs/incidents.md` is the companion file** — where
this one records what the data supports, that one records what was claimed anyway, and
the rule each error produced. Read it before adding a finding here.

## Read this before trusting any number below

**The export is not everything he does.** Confirmed by Max on 2026-09-02: he finishes
push days with three sets of push-ups, pull days with three sets of pull-ups, and trains
core ad hoc — and most of it never reaches Strong. Push-ups appear **8 times in the whole
export**, last April 2025.

Three consequences, and they touch most of this file:

- **Volume is understated**, by an unknown amount, unevenly across muscle groups.
- **Session shape is wrong.** Push days look like exactly five exercises; they are five
  plus a finisher. Anything reasoning from "sessions run 5–6 exercises" — the
  session-length question below included — is reasoning about the logged part only.
- **"Absent" claims are unsafe.** Core reading as zero since 9 March is a fact about the
  log. It was written up here and in `docs/goals.md` as a training gap; that was wrong.

He is now logging the ad hoc work: each session has an extra/finisher field on the
phone page, and the free-text row captures anything done outside the prescribed slots. Numbers from exports
after September 2026 should be progressively more complete — which also means **do not
compare set counts across that boundary** and read a rise as improvement.

## Holds: the pull-up position effect

Pull-ups at position 2 in the session for five months ran 24–32 reps. Moved to position
5 for three months: 13–23. Moved back to position 2 and immediately 27.

This one survives where the session-length claim didn't, because position was a standing
programme decision rather than a day-by-day choice — it isn't confounded with how good
he felt that morning. The reversal still rests on a single session, so treat it as
strong but not proven.

Practical consequence: **pull-ups go first on pull day**, and session order generally is
programming, not formatting. `log.md` records exercises in performed order for this
reason. Never sort or regroup it.

## Holds: left and right lat are separate lifts

Left progresses normally; holding it back to match the right detrains a healthy lat for
nothing, and cross-education means training the good side produces measurable strength
gains in the injured one.

The **70kg** figure often quoted for the left predates the September 2025 form change
and is not established by any 2026 data — the only 2026 row session (20 Aug) put both
sides in at 50kg. Treat the size of the gap as unmeasured until the two sides are
logged separately.

Right starts at the heaviest genuinely pain-free load and moves on the green-light rules
in `plan.md` — reps before weight, always.

## Does not hold: session length

Tested twice, opposite answers both times.

Scored against each lift's lifetime history, 7+ exercise sessions look worse. But
6-exercise days are 49% of 2024 and 6% of 2026, so that comparison is mostly measuring
two years of getting stronger. Remove the time trend and 7+ sessions score *best* —
which is reverse causation: on good days he does more exercises and pushes further into
the session.

Observational data cannot separate these. Sessions run 5–6 exercises because that fits
his hour, **not** because it is proven optimal. An earlier version of `CLAUDE.md`
asserted 5–6 was his tested optimum; that was wrong and was removed.

To actually answer it: alternate a 5-exercise and a 7-exercise version of the same
session for eight weeks, choosing which one **before** training rather than by feel on
the day. Nothing short of that means anything.

## Does not hold: time of day

He believes he is stronger at certain times. The log cannot show it, and the apparent
effect is the calendar again.

| Session start | raw z | de-trended | n |
|---|---|---|---|
| morning ≤11 | +0.172 | +0.127 | 745 |
| midday 12–14 | +0.037 | +0.033 | 109 |
| afternoon 15–17 | +0.084 | +0.051 | 386 |
| evening 18+ | **−0.220** | **+0.124** | 751 |

Raw, mornings beat evenings by 0.39 SD. De-trended, evening goes from −0.220 to +0.124
and the gap all but vanishes — because **he moved from evening training in 2024 to
morning training in 2026**, across the same two years he got stronger. 2024 was 53
evening sessions against 19 morning; 2026 is 60 morning against 22 evening. Mornings are
also mostly weekends: 80 of 143 morning sessions are a Saturday or Sunday.

Three checks, all pointing the same way:

- **Year by year the sign flips.** Evening led in 2024 (−0.63 vs −0.78), morning in 2025
  (+0.25 vs −0.04), level in 2026 (+0.378 vs +0.397).
- **Within 2026 alone** — the clean window, both times well represented — the four
  buckets sit between +0.378 and +0.463. A 0.09 SD spread is nothing.
- **Per lift within 2026**, only 6 of 18 favour mornings; mean gap **−0.11 SD**, median
  −0.10. If anything it leans PM, which is to say it leans nowhere.

Unlike the session-length question this one is **answerable, and the answer is no
effect** — the specifications agree once the confounded variance is removed, rather than
contradicting each other.

The one that looks like something: overhead press, AM +0.59 (n=16) against PM +0.03
(n=5). Ignore it. It is the lift that regressed across 2026, the PM sample is five
sessions, and it is the same trend confound in miniature.

**What this does and does not mean.** It means his log cannot detect a time-of-day
effect, not that none exists — physiology says one usually does, and n here is
observational. It also means there is no strength argument for scheduling around a time
of day, so **train when it suits the week.** If he feels stronger in the morning, that
is worth more than a 0.02 SD difference: readiness and adherence are real and the
measurement is not sensitive enough to argue with him.

To answer it properly: alternate a morning and an evening version of the *same session
type*, deciding which **before** the day starts, for eight weeks. Same design as the
session-length test, and the only version that would mean anything.

## Holds: his rep zones, and the programme's bands were above them

Checked 2026-10-02, when he asked whether "+2.5kg at 10–12" was his rule. It wasn't, and
it isn't his data either. The bands came in with the 09-01 plan and the redesign of
09-21; "top of the band on all sets for two consecutive sessions → smallest increment"
was written by a Claude session on 09-21. Neither was derived from the export.

`analyse.py` now prints REP ZONES: per exercise, the reps at the session's top weight,
and what the session right before a load increase looked like. From the 31 Aug export:

- **Heavy barbell lifts live at 5s.** Squat sets of 5, and every 12-month increase came
  after 5s. Flat bench the same.
- **Incline bench, RDL, OHP, rows and pulldowns live at 8.** He moves up after 8s.
- **Most accessories live at 8–10**, not 10–12: chest fly (8s on 65kg for months), DB
  bench, cable crossover, triceps pull, leg extension, curls.
- **High-rep work is a short list:** lateral raise (15–18), face pull (10–12), triceps
  extension (10–12), calves (15), core.
- **He moves up after one session at the top of his zone**, not two (median held at a
  load: 1 session for most lifts, 2 for squat, flat bench and rows).
- **Lower-body barbell jumps are 5kg** (squat, RDL); upper barbell 2.5–5; dumbbells and
  pins the next step.

**What it means:** a band set two reps above where he works reads as a stall that isn't
one. Several debrief "stalls" in September (fly, triceps pull, leg extension, leg curl)
were bands, not plateaus. Set bands from REP ZONES, not from a template.

## Proposed: rep ranges from the research (2026-10-04, awaiting his decision)

He asked for bands set by the evidence, not only by his history. Nothing in `plan.md` or
the page has changed until he says go.

**What the research supports**
- Muscle grows across a wide range, roughly 6–30 reps, when sets end close to failure;
  very light loads (~20% 1RM) fall short. Schoenfeld et al. 2021 (Sports 9:32);
  Currier et al. 2023 (BJSM, 178 studies); Lasevicius et al. 2018.
- Maximal strength favours heavy loads (>80% 1RM, about 8 reps or fewer). Currier 2023.
- Proximity to failure drives growth, load drives strength. Robinson et al. 2024
  (Sports Med). Training to failure adds 24–48h to recovery: Morán-Navarro et al. 2017.
  That matters for legs within 48h of football.
- Adding reps works as well as adding weight. Plotkin et al. 2022 (PeerJ). So a band can
  be wide where the weight steps are coarse.
- In footballers, heavy low-rep squats improve sprint and jump: Helgerud et al. 2011
  (4×4 half squat), Rønnestad et al. 2008, Wisløff et al. 2004.
- **No trial sets the best reps for a given exercise.** Per-lift bands come from what the
  lift is for, the size of one weight step (each rep ≈ 3% of 1RM, the Epley estimate
  `analyse.py` uses), and joint-load practice, which is coaching consensus, not RCT.

**Band width:** one weight step costs about (step % ÷ 3) reps, so the band must be at least
that wide, or the next weight starts under it. That is what 10–12 bands did: DB press
26kg × 12 went to 28kg × 8; lateral raise +1kg on 8kg is 12%, about 4 reps.

**Proposed bands** (RIR = reps in reserve at the end of each set)

| Lift | Now | Proposed | Effort | Why |
|---|---|---|---|---|
| Squat | 3×8–10 | **3×5** | RIR 2 | Strength for football; his history too. Knees permitting. |
| Deadlift | 3×5 | 3×5 | RIR 2 | Unchanged |
| RDL | 3×6–8 | 3×6–8 | RIR 2 | Unchanged; hamstrings 48h before football |
| Incline bench | 4×5–8 | 4×5–8 | RIR 1–2 | Unchanged |
| Pull-ups | AMRAP +5 / AMRAP−2 | unchanged | | |
| Iso row | 8–10 | 8–10 | | Row protocol and physio govern it |
| DB bench | 10–12 | **8–12** | RIR 1–2 | 2kg step ≈ 2–3 reps |
| Chest-supported row | 10–12 | **8–12** | RIR 1–2 | Compound accessory |
| Triceps dip | 8–12 BW | 8–12, then weighted | RIR 1–2 | Unchanged |
| Chest fly, cable crossover | 10–12 | **10–15** | RIR 0–2 | Shoulder at stretch; stack steps ~10% |
| Straight-arm pulldown | 10–12 | **10–15** | RIR 2 | Single-joint, on the injured lat |
| Reverse fly | 8–12 | **10–15** | RIR 0–2 | Small muscle |
| Triceps pull | 10–12 | **10–15** | RIR 0–2 | Elbow load |
| Curls (cable, barbell, hammer) | 8–10 / 10–12 | **8–12** | RIR 0–2 | One band for the slot |
| Leg curl | 8–10 | **8–12** | RIR 1–2 | |
| Lateral raise | 15–20 | 15–20 | RIR 0–1 | Unchanged; 1kg step ≈ 4 reps |
| Face pull | 12–15 | **12–20** | RIR 0–1 | 2.5kg step ≈ 14% |
| Leg extension | 10–12 | **12–20** | RIR 0–2 | Light, for the knees |
| Calves | 15–20 | **12–20** | RIR 0–1 | |
| Hanging leg raise | 10–12 | **8–15**, then toes to bar | | Calisthenics progression |

**Rule:** the top of the band on every set, at the target effort, once → the next step.
Not two sessions. Right iso row excepted.

**Where his history and this disagree:** chest fly (he works at 8), triceps pull and leg
extension. The reason to go lighter is joint load, not growth, so it is his call.

## The general lesson

Three confident findings in this project turned out to be scheduling artefacts read as
physiology — the session-length claim, and twice over the Sep 2025 row drop, which is a
form change he made deliberately (see `CLAUDE.md`).

The log records what he lifted. It never records why he stopped. Ask him before
inferring from it; he is right about his own body more often than the log is.

**Two habits that would have caught most of it:**

1. **De-trend before believing any cross-sectional comparison.** Session length, the row
   drop and time of day all produced confident wrong answers because something changed
   over the same two years he got stronger. If the groups being compared are not evenly
   spread across the calendar, the comparison is measuring the calendar.
2. **State exactly what you computed.** "22 of 22 pull days end on a curl" was written
   from a calculation that actually asked whether a curl appeared *anywhere* in the
   session. It was 9 of 22. The number was right; the sentence was not, and it reached
   two documents before anyone checked.

## Open questions

- **Is the 50kg right-side ceiling pain-limited or caution-limited?** First real data
  point, 2026-09-03 — the first `pain(R)` ever recorded. **3/10, which is a green light**
  under the `plan.md` protocol, with the left working up to 60kg × 8 while the right held
  50kg × 8, 8, 8.

  Two things follow. The gap is **10kg, not the 20kg** that older notes assumed — so
  treat 70/50 as retired, and 60/50 as the first measurement. And his note said the right
  side was *"half weakness half pain — I've certainly lost a lot of strength there"*,
  which the 0–10 scale cannot carry: a green light on pain says nothing about strength
  deficit. If that reading repeats, the limiter is detraining rather than tissue, and
  the answer is loading the right side more, not less.

  **Still open, and a worked example of how not to close it.** On 2026-09-13 he rowed
  57kg for two sets of 8, both sides equal, and this file briefly recorded that as the
  50kg ceiling being broken. It was the **Uni Lateral Seated Row**, a different exercise
  from the Iso Lateral Row — his correction, 09-14. Different machine, different
  leverage, loads not on the same scale. The comparison was never valid and the
  conclusion is withdrawn.

  This is the fourth time in this project a number has been read against a number it
  does not belong with, and the first three are the whole reason the "Read this before
  trusting any number below" section exists. **Machine identity is part of the
  measurement.**

  **Updated 2026-09-20.** On 09-17 he performed the right-side iso-lateral row at 50kg
  and reported **4/10** with "extreme tightness" — an amber under the protocol. The two
  greens from 09-03 and 09-10 are struck and the count resets to zero. On 09-20 a
  calisthenics session also read 4/10 with no iso-lateral row in it, so the gate count is
  untouched but the pattern is now three consecutive 4/10 readings across three different
  sessions. Readings run: 3/10 (09-03), 2/10 (09-10), 4/10 (09-13 seated row), 4/10
  (09-17 iso-lateral row), 4/10 (09-20 calisthenics). That is a physio question, not one
  for this file. The row holds at 50kg; nothing is added.

  **Updated 2026-10-02.** The right side read **6/10 on the Seated Row (Cable), 57kg ×
  10, 10, 10**, on 2026-10-01. His answer places it on that row, not the deadlift or the
  +8kg pull-ups in the same session. It is the highest reading in the log. The
  chest-supported row read 0/10 on 09-26, and the iso-lateral row 3/10 at 55kg on 09-24.
  Tempting to call seated cable rowing the provoker, since the 09-13 4/10 was also a
  seated row at 57kg. But that was the Uni Lateral Seated Row, a different machine, and he
  called it tightness. One reading per machine is not a pattern. Name it to the physio,
  and watch whether the chest-supported row stays clean.
- **Did the overhead press decline because its slot rotates?** Asserted in `plan.md`
  for a fortnight as though settled; it is not. OHP e1RM ran 49.6 → 60.2 → **61.7**
  (2026Q1) → 57.0 → 50.7. The rotation story says it fell because push slot 2 picks it
  about one day in four. Two rival explanations cover the same window and neither has
  been excluded: the **right lat injury from June 2026**, and the **two-week August
  trip** the whole re-entry phase exists for. There is also a prior question nobody has
  asked — was slot 2 already rotating in 2026Q1, when the lift *peaked*? If it was, the
  rotation story is dead on arrival.

  **Resolvable from the next export**, and `analyse.py` should do it: count OHP sessions
  per quarter against e1RM per quarter, and check whether the drop lands at June or
  tracks exposure. Until then the slot stays rotating — anchoring it was proposed,
  implemented on 2026-09-12 and undone the same day, because the cost is concrete (it
  would make a movement that has provoked right-lat pain on both recent push days
  compulsory rather than occasional) and the benefit rests on an untested because.
- **Is overhead pressing what the right lat is reacting to on push day?** Two sessions,
  both 2/10: barbell OHP on 2026-09-07 (his note names it), Arnold press on 2026-09-11.
  Two is a pattern worth naming to the physio, not a conclusion, and the confound is
  obvious — those are simply the two push days since the restart. Watch whether a push
  day *without* an overhead press comes in clean. If the pattern holds, the question is
  whether the movement belongs on push day at all, which is his physio's call and not
  the log's.
- **Why was Feb–Apr 2026 his best block in two years?** Nine straight Saturday leg days.
  Never established. CPAP started May/June, which is where the decline begins, but he
  considers this closed — note it, don't reopen it.
