# The programme

The brief is in `docs/goals.md`: holistic fitness at his own pace, shifting towards
calisthenics, with no target to hit. This file is how that gets delivered week to week —
read the goals before proposing a change to it.

A **two-week rotation**. Week A is the heavy half — five lifting sessions and the legs
day. Week B is lighter — three lifting sessions, and a second football on the Friday
where Week A puts a Push.

This is Max's own template, given 2026-09-02. It is the spine of the programme and it
is authoritative. What the export shows about how faithfully it gets run is a separate
question, kept honest at the bottom of this file — do not confuse the two, and do not
delete a session from this plan because the log is quiet about it.

## The fortnight

| | **Week A** | **Week B** |
|---|---|---|
| **Mon** | Push | Push |
| **Tue** | Football — 2h, 7-a-side | Football — 2h, 7-a-side |
| **Wed** | Rest, protected | Rest, protected |
| **Thu** | Pull | Pull |
| **Fri** | Push | Football — 2h, 7-a-side |
| **Sat** | Legs, then yoga | Yoga only |
| **Sun** | Pull | Calisthenics |

Week A is 2 × Push, 2 × Pull, 1 × Legs. Week B is 1 × Push, 1 × Pull, 1 × Calisthenics.
Eight lifting sessions a fortnight, two or three football sessions, yoga twice.

**Anchor:** Week A begins **Monday 7 September 2026**, and the weeks alternate from
there — so 14 Sep is Week B, 21 Sep Week A, and so on. He corrected this on 2026-09-07;
an earlier version guessed 14 Sep, which was a week out.

**Time of day is free.** He suspected he is stronger at certain times; the log says
otherwise. Within 2026 — the only window where mornings and evenings are both well
represented — the gap across all four time buckets is 0.09 SD, and only 6 of 18 lifts
favour mornings. The apparent morning advantage in the raw numbers is the calendar: he
shifted from evening training in 2024 to morning training in 2026 while getting
stronger throughout. Working out in `docs/findings.md`.

So schedule sessions by what the week allows, not by a time. In practice that has meant
mornings at the weekend and evenings on weekdays, which is fine and needs no change. If
he *feels* stronger at a given hour, train then — the measurement is not sensitive
enough to argue with him, and readiness is worth more than 0.02 SD.

**Wednesday is protected in both weeks.** Late food after Tuesday football. Nothing
goes there, yoga included.

## Phases

| Dates | Phase | What |
|---|---|---|
| → 13 Sep 2026 | Re-entry | 10% off top sets if needed. No legs day. The rotation runs normally — this week is Week A. |
| 14 Sep → | Full block | Full load, everything on, progressing normally. |

## Anchors and rotations

Every session has two kinds of slot, and the difference matters more than the exercise
names.

- **Anchor slots** stay the same session after session and carry the load progression.
  You cannot progressively overload something you do not repeat. Incline bench is at an
  all-time high because slot 1 never changes. The overhead press, in a rotating slot,
  fell from 61.7 to 50.7 e1RM over the same period — but read that as the cost a
  rotating slot *can* carry, not as a measured cause. See the Push section: the
  rotation is one candidate explanation and it has never been tested against the other
  two.
- **Rotate slots** change whenever he likes, from the menus below. Variety costs nothing
  here because these slots are not chasing a number — they are accumulating volume and
  covering angles. Adherence matters more than optimality, and he trains more when he is
  enjoying it.

So: **rotate the accessories freely, leave the anchors alone.** Anchoring a rotating
lift is the lever available if one needs to progress — but it costs variety, and it is
not free when the lift in question is one the right lat reacts to. Push slot 2 was
considered for it on 2026-09-12 and deliberately left rotating; see the Push section.

Exercises marked ★ are ones he has never logged. See "Trying new exercises" below.

## Push (~50 min)

| # | Slot | Exercise | Sets | Now |
|---|---|---|---|---|
| 1 | **Anchor** | Incline Bench Press (Barbell) | 4 × 5–8 | 60kg |
| 2 | Rotate — vertical press | Shoulder Press · Arnold Press · **Overhead Press** · Landmine Press | 3 × 8–10 | 30kg / 22kg / 40kg |
| 3 | Rotate — chest | Chest Fly · Cable Crossover · Incline Chest Press · Dumbbell Pullover | 3 × 10–12 | 65kg / 13.75kg / 14kg |
| 4 | **Anchor** | Lateral Raise — dumbbell or cable | 3 × 15–20 | 8kg |
| 5 | Rotate — triceps | Triceps Extension · Triceps Dip · One-Handed Triceps Pull · ★ Skullcrusher | 3 × 10–12 | 17.5kg / bw |
| F | Rotate — finisher | Push-Ups · ★ Diamond Push-Ups · ★ Pike Push-Ups · ★ Deficit Push-Ups | 3 × 15 | bodyweight |

### Slot 2 stays a rotate slot — decided 2026-09-12

An earlier version of this file carried a standing proposal to anchor the overhead
press here for a block. It was briefly implemented on 2026-09-12 and **undone the same
day.** Do not re-propose it without new evidence; the reasoning is below, so that the
next session inherits it instead of re-deriving it.

**The argument for it was never tested.** It ran: OHP fell from 61.7 to 50.7 e1RM
because its slot rotates, so anchor the slot and it comes back. But nothing establishes
the *because*. Two other explanations cover the same window and neither was ruled out —
the right lat injury dating from June 2026, and the two-week trip in August that the
whole re-entry phase exists for. This project has already mistaken three scheduling
artefacts for physiology; this would be the fourth.

**The argument against it is concrete.** Both push days since the restart logged
right-lat pain at 2/10, and both had an overhead press in slot 2 — the barbell OHP on
09-07, the Arnold on 09-11. Anchoring would make the provoking movement compulsory every
push day rather than roughly one in four, while that structure is under physiotherapy
care. That is the wrong direction on the one signal actually being measured.

**And nothing depends on it.** There is no target and no date. The overhead press hole
is real, but a lift regressing is not a goal to chase unless he says it is — the brief
is rounding, not peaking, and push already carries two anchors out of six slots.

**What answers it instead:** the next Strong export. `analyse.py` can ask directly
whether OHP sessions cluster where the slot happened to pick it, and whether the decline
tracks slot frequency or tracks June. That question is now logged in `docs/findings.md`.
Until then the slot rotates, and if the right lat keeps reacting to overhead pressing,
the live question is whether the movement belongs on push day at all — not whether to
do more of it.

The finisher has been happening for years and going unlogged — push-ups appear 8 times
in the whole export, last April 2025. Log it. Even sets of 15, not 25/8/8.

**Dumbbell Pullover is on trial in slot 3**, first run 2026-09-11 at 14kg — session 1 of
4 under the four-session rule below. Decide to keep or drop it after the fourth, not by
feel. It displaces nothing permanently; it is one of the chest rotate options.

Flat bench was dropped deliberately in June to prioritise incline. It stays dropped.

## Pull (~50 min)

**Exactly one horizontal row and one to two vertical pulls.** This is not a guess: across
the 22 pull days from May to August he did **exactly one horizontal row on every single
one**, and one to three vertical pulls, median two. An earlier version of this file
prescribed two of each. That was wrong — the wide-grip row was the surplus, and it has
moved to the substitutes line.

| # | Slot | Exercise | Sets | Now |
|---|---|---|---|---|
| 1 | **Anchor** | **Pull Up** — first, always | 3 × AMRAP | bodyweight |
| 2 | **Anchor** — the one horizontal row | Single-Arm Iso-Lateral Row, left then right | 3 × 8–10 each | see protocol |
| 3 | Rotate — second vertical | Lat Pulldown · Alternate Single-Arm Lat Pulldown · Underhand Pulldown · ★ Straight-Arm Pulldown | 3 × 10 | 67kg |
| 4 | Rotate — rear delt | Face Pull · ★ Reverse Flye · ★ Bent-Over Rear-Delt Raise | 3 × 12–15 | 17.5kg |
| 5 | Rotate — biceps | Bicep Curl · Preacher Curl · Hammer Curl · Incline Curl · Rings Curl | 3 × 8–10 | 30kg |
| F | Rotate — finisher | Hanging Leg Raise · Plank · ★ Dead Hang · ★ Ab Wheel | 3 × 10–12 | bodyweight |

**Slot 2 substitutes**, only if the machine is taken: Seated Wide-Grip Row (57kg, hold
and chase reps) or ★ Chest-Supported Row. It is an anchor because it is the injured
side's lift — the green-light protocol needs the same movement week to week to mean
anything.

**Slot 4 is new as a fixed slot.** Rear delts fell from 3.0 sets a week to 0.8 because
the face pull was optional. Making it a real slot is the fix.

**Pull-ups go first.** Position 2 for five months gave 21–26 reps; position 5 for three
months gave 13–23; back to position 2 on 27 Aug gave 27, the best in the record. His own
data, and the strongest thing in it.

**On doing two exercises for one muscle group:** normal and fine — the second one is
volume, not a strength test, and it is expected to be weaker. But his instinct is worth
respecting, and the position effect shows fatigue costs him real reps on the compound.
Hence one horizontal, one or two vertical, pull-ups first and fresh.

## Legs (~45 min) — Week A only

He dislikes leg training. It sits once a fortnight by design, not once a week.

| # | Exercise | Sets | Now |
|---|---|---|---|
| 1 | Squat (Barbell) | 3 × 6–8 | 75kg |
| 2 | Romanian Deadlift (Barbell) | 3 × 6–8 | 70kg |
| 3 | Leg Press *or* Bulgarian Split Squat | 3 × 10 | 130kg |
| 4 | Lying or Kneeling Leg Curl | 3 × 10–12 | 35kg |
| 5 | Seated Calf Raise | 3 × 15 | 40kg |

**The RDL lives here and nowhere else.** It appears on 10 of his 11 leg days and on
none of his 22 pull days. An earlier version of this file moved it to Thursday to cover
the hamstring gap on Week B. That was the wrong fix: it put a heavy hip hinge on a day
he has never hinged. Week B has no direct leg work, by design — two hours of 7-a-side
on the Tuesday and again on the Friday is the trade.

## Calisthenics (~55 min) — Week B Sunday

**In Week B this is the second upper-body session, not an extra.** Week B carries one
Push and one Pull, so this day has to cover what they miss — and the five-slot version
this replaced covered a vertical pull and a dip and nothing else. Rebuilt 2026-09-05 at
his request to be a complete upper body: every pull and push pattern, plus core, grip
and the Phase 1 skills.

Run as **antagonist supersets** — the two movements in a block alternate, and the rest
comes after the pair, not between them. Nothing in a pair competes for the same muscle,
so this costs nothing in performance and takes about fifteen minutes off the session.

| Block | | Exercise | Sets | Rest |
|---|---|---|---|---|
| **A** skill | A1 | ★ Chest-to-Wall Handstand | 3 × 20–30s | pair, then 60s |
| | A2 | Hollow Body Hold | 3 × 20–30s | |
| **B** | B1 | **Pull Up** — vertical pull | 3 × AMRAP−1 | pair, then 90s |
| | B2 | Triceps Dip — horizontal/vertical push | 3 × 8–10 | |
| **C** | C1 | ★ Ring Row *or* Inverted Row — horizontal pull | 3 × 10–12 | pair, then 90s |
| | C2 | ★ Pike Push-Up — vertical push | 3 × 6–8 | |
| **D** finisher | D1 | Hanging Leg Raise — core | 3 × 10–12 | pair, then 60s |
| | D2 | ★ Dead Hang — grip | 3 × 20–30s | |

Eight movements, four blocks, about 55 minutes. Coverage: vertical pull (B1),
horizontal pull (C1), vertical push (C2), horizontal push (B2), core (A2, D1), grip
(D2), plus the handstand skill.

**Skill block is practice, not conditioning.** Ten minutes, stop while the shape is
still clean, never to failure. It goes first because skill work is worthless tired.

### The right lat governs this session

Three days after a pull day, and the 3 Sep note said the right side was *"half weakness
half pain"*. There is more pulling here than in a normal pull day.

- **C1 is the release valve.** A ring or inverted row is instantly regressable — walk
  the feet in or raise the bar and the load drops. If the right side talks, regress it,
  then cut it. Do not push through.
- **D2 decompresses.** The dead hang at the end is deliberate, and the physio should
  sign it off before the first one.
- Keep the pull-ups honest: **AMRAP−1**, one rep in reserve. Re-entry runs to 13 Sep.

### Three new movements at once — deliberately

`plan.md`'s own rule says introduce one new exercise at a time and give it four
sessions. This breaks that rule and it is worth saying why: **that rule protects
progression on established lifts, and this session has no established anything** — it
has never once been logged. There is no baseline to disturb, so the first job is to
create one. The two anchors, pull-up and dip, are unchanged, so continuity is intact.

Pike push-ups were on the invented list an older version of this file carried as though
he already did them. They are reintroduced here **as new**, under the standing rule, to
fill the vertical-push gap that his regressed overhead press leaves. If he would rather
not, a second dip variation covers the block and the gap stays open.

Progressions and how to know when to move on: `docs/calisthenics.md`.

**Log all of it.** This session has never appeared in Strong, so it currently reads as
though it does not exist.

## Yoga (15–20 min) — Saturday, both weeks

Week A it follows the legs day. Week B it is the whole of Saturday. It happens either
way — that is the point of giving it a fixed slot rather than leaving it floating.

90/90 hip switch · half-pigeon · supine hamstring with a strap · thoracic open-book ·
couch stretch · ankle dorsiflexion.

Not tracked in Strong and not worth tracking. It is the one thing here measured by
whether it happened, not by what it weighed.

## The row protocol

Left and right are separate exercises that share a machine. Log them separately.

**Left** — progress normally. Note the "70kg" figure carried in older notes predates
the September 2025 form change; the only 2026 row session (20 Aug) put *both* sides in
at 50kg. Re-establish where the left actually is before assuming a 20kg gap.

**Right** — start at the heaviest genuinely pain-free load. Three green lights held for
two consecutive weeks → +2.5kg. Any red → back to the last green load and stay there.

| Green light | Means |
|---|---|
| Pain ≤ 3/10 during the set | Present, not sharp, doesn't change how you move |
| Baseline within 24h | Next morning feels like any other |
| Not creeping week to week | Compare to a fortnight ago, not yesterday |

This framework comes from Achilles tendinopathy research, not muscle strain. It is an
adaptation and the physio should sign off on it.

## Progression

- **Incline bench** — +2.5kg once all four sets hit 8
- **Overhead press**, if it goes into slot 2 — +2.5kg at the top of the range
- **Lateral raises** — stay 15–20; +1kg once 20 holds across all three sets.
  Earned and taken on 2026-09-11: 7kg × 20, 20, 20 on 09-07 → 8kg × 15, 15, 15. Next
  step is 9kg, on the same condition.
- **Seated wide-grip row** — hold 57kg deliberately, chase reps
- **Pull-ups** — back to 27 reps fresh, then re-add 5kg once that holds three sessions
- **Anything the right lat touches** — reps before weight, always
- **Legs** — leave loads where they are; once a fortnight is too infrequent to programme
- **Calisthenics** — reps only, never load

## When life interferes

- Miss a day, take the next one in the template. Do not shuffle sessions between days
  to catch up, and do not restart the fortnight.
- After 10+ days off, take 10% off top sets for the first session back.
- Travelling: Sunday's session needs a bar and a floor. Push needs almost nothing.

## What the log says about adherence

Kept separate from the plan above on purpose. The template is the intent; this is what
the Strong export of 31 Aug 2026 actually contains.

- The fortnight asks for **eight lifting sessions**, about four a week. Logged rate is
  **3.16/week lifetime and 2.67 over the last twelve weeks.** The gap is mostly the
  Friday Push and the Sunday session.
- **Push and Pull are run faithfully.** Both are rock-solid five-exercise templates and
  the loads move. This is the working half of the programme.
- **Legs run about monthly** rather than once a fortnight — 11 sessions across 2026.
- **Calisthenics has never appeared in the log at all.** Either it is not happening or
  it is happening unlogged. Worth knowing which, because the answer changes what the
  Sunday slot is for.

None of this is a verdict on the plan. It is what to check against the next export.

## What we don't know

Both open questions and the full working live in `docs/findings.md`. The short version:
session length is unanswerable from observational data, and whether the right lat's
50kg ceiling is pain-limited or caution-limited will not be known until `pain(R)`
actually gets logged.

## How this plan changes

This file is not a record of what he does. It is the programme, and it is meant to move.

**Claude proposes, Max decides.** Bring a change with the evidence behind it, the
trade-off it costs, and a recommendation — not a list of options to pick from. Then
write down what was decided and why, so the next session inherits the reasoning instead
of re-deriving it.

**Review points:**

- **Every new export** into `data/` — reconcile the log, re-run `analyse.py`, and come
  back with what moved, what stalled, and one proposal. See `docs/workflows.md`.
- **Phase boundaries** — the next one is 14 Sep, when re-entry ends and Week A starts.
- **Any lift stalled three sessions or more** — that is a prompt to propose something,
  not a fact to note in passing.
- **Any green-light streak on the right row** — three held over two weeks earns +2.5kg.
  Say so; don't wait to be asked.
- **A session repeatedly skipped** — ask why before assuming it should be cut. The log
  tells you about adherence, never about intent.

**Everything goes to `main`** — his instruction, 2026-09-10. That includes this file,
`CLAUDE.md` and `analyse.py`, which an earlier version of this rule sent to a branch for
review. It did not work: branches sat unmerged, and on 09-10 a logged session and a UI
fix were stranded on one for days because nobody noticed. Branch only if he asks for one
in that message. Pushing straight to `main` is not licence to change the programme
unasked — the propose-don't-impose rule above is unchanged, and a change he has not
agreed to is still wrong; it just means the writing-down happens where he can see it.

## Trying new exercises

He is open to movements he has never done. The constraint is that a new exercise has to
earn a slot, not get added on top — the sessions are five exercises because that is what
fits his hour, and that is not up for renegotiation without a reason.

**The rule for introducing one:**

1. Name the slot it goes into and the exercise it displaces.
2. Say what it is for — a gap in the plan, a stall to break, a rehab constraint.
3. Run it for **four sessions**, then keep it or drop it. Decide before starting, not
   by feel afterwards. This is the same discipline `docs/findings.md` asks for on the
   session-length question, and for the same reason.
4. Log it under its real Strong name from the first set, so it is visible to
   `analyse.py` rather than invisible like the calisthenics day currently is.

**Standing candidates**, with what each is for:

| Exercise | Slot | What it is for |
|---|---|---|
| Chest-Supported Row | Pull 3 or 4 | Removes torso English from the row — the most promising way to load the right lat without the pain that free rowing brings. He did one on 27 Aug. |
| Dead Hang | Calisthenics, or after Pull | Lat decompression, 3 × 30s. Cheap, and the sort of thing a physio tends to like. Clear it with them. |
| Hip Thrust | Legs 3 | Posterior work that does not load the spine like the RDL. Done once, 25 Jul. |
| Nordic Curl (eccentric) | Legs 4, displacing the leg curl | Best-evidence hamstring exercise. **Note:** an earlier version of this file prescribed these as though they were established — they have never been done. Proposed here honestly as new, starting 2 × 4. |
| Z-Press or Half-Kneeling Landmine Press | Push 2 | An overhead variant that is kinder to the shoulder than a strict OHP, if the press is what is holding slot 2 back. |
| Rear-Delt Flye | Push 4, paired with laterals | Rear delts fell from 3.0 to 0.8 sets a week over the last eight weeks. The face pull is currently optional, so this is the real gap. |

None of these are in the programme. They are the shortlist to draw from when a review
calls for a change — one at a time, four sessions, then a decision.

**Bias towards the bodyweight option.** Where two candidates do the same job, the
calisthenic one wins — that is the stated direction of travel. Hanging leg raises over
cable crunches; dips over a triceps machine; dead hangs over a grip trainer.

## The live gaps

From the export of 31 Aug 2026 — **with the caveat that the export is not everything he
does.** He finishes push days with push-ups, pull days with pull-ups, and trains core ad
hoc, none of it reliably logged. Full working in `docs/goals.md`.

- **Core: the gap is the logging, not necessarily the training.** Zero logged sets since
  9 March, against 8.8% of his lifetime volume — but he does it ad hoc and does not
  record it, so nobody can say what it actually amounts to. The finisher slot on pull day
  and the free-text row on the phone page exist to fix that. **Get it logged first, then
  programme it.** Anything else is guessing.
- **Rear delts: 0.8 sets/week, down from 3.0.** The face pull is optional on pull day,
  which is why. This one is a real gap — nothing unlogged is filling it.
- **Grip: never trained.** 12 sets of farmer walks in Feb 2025 and nothing since.
  Usually the limiter on calisthenics progressions. Dead hangs are the cheap entry —
  clear them with the physio first, given the right lat.

Legs are thin and stay thin. That is settled, not a gap.

## Logging the ad hoc work

Confirmed by him on 2026-09-02: the finishers and the core work have been happening all
along and mostly going unrecorded. This matters beyond tidiness — it is why the log said
core was dead, why push days looked like exactly five exercises, and why the pull-up
position numbers read the way they do.

- Both Push and Pull now carry an explicit **finisher slot** in the tables above.
- The phone page has a **free-text row** at the bottom of every session for anything
  else — core, a new movement, whatever actually happened.
- Anything unlogged is invisible to `analyse.py`. That is not a criticism of him; it is
  the reason a finding can be wrong, so treat any claim that something is "absent" as a
  claim about the log until it has been checked with him.
