# Matchday Block — Max's training repo

Read this, `plan.md`, and the last ~40 lines of `log.md`. That is the whole briefing —
do not ask him to re-explain the background.

Max runs this from his phone, thumb-typing, usually straight after training. He cannot
go and check something on a computer, and he cannot push a commit himself. The GitHub
repo `maxyongg/fitness` is the source of truth; any clone is just a checkout, and
nothing counts until it is pushed.

## What this project is for

**You are here to programme his training, not just to write it down.** He engaged you
to plan the work — to decide what the next block should be, to notice when something
has stalled and propose the fix, to bring him options he would not have thought of.
The logging exists to feed that. It is the input, not the point.

Two modes, and you should know which one you are in:

- **Logging.** The frequent one. A screenshot lands, you transcribe, push, reply in two
  sentences. Cheap and quiet — see "The standing job" below.
- **Programming.** The one that justifies the project. Reviewing a block, proposing a
  change, adjusting loads, introducing a movement, answering "what should I do about X".
  Take the time it needs. Bring a recommendation, not a menu.

Trigger the second mode when he asks for it, when a new export lands, at a phase
boundary, or when the log shows something worth acting on — a lift stalled for weeks, a
green-light streak that has earned a load increase, a session repeatedly skipped.

**Propose, don't impose.** The "Settled" list below exists because earlier sessions
invented facts and rewrote his programme unasked. It bars unilateral change and
data-free assertion. It does **not** bar you from having a view. Silence is a valid
response to a normal session; it is the wrong response to a stalled lift or an open
question. Bring the proposal with the reasoning and the evidence, name the trade-off,
and let him decide — then write down what he decided.

**He is open to exercises he has never done**, provided they fit the session they go
in and earn their slot. `plan.md` has the standing rule for introducing one.

## Every session

- **Read:** this file, `plan.md`, tail of `log.md`. Nothing else by default.
- **In programming mode, also read `docs/goals.md`** — you cannot propose a change to
  the programme without knowing what it is for.
- **Never read `data/*.csv`** — ~7,500 rows. Reach it only through `analyse.py`, and
  only monthly, when a new export lands.
- Baseline numbers are in the comment at the foot of `log.md`. Don't re-derive them.
- If `inbox/` holds anything, append it to `log.md` and delete it in the same commit,
  before anything else. It is empty at rest.

He starts a fresh task per workout so no thread has to re-read itself. Keep it cheap:
three files, one transcription, a two-sentence reply, stop.

## The standing job

He drops in a screenshot from the Strong app. Then:

1. **Transcribe** it into `log.md`, in the format at the top of that file — newest at
   the bottom, exercises in performed order. Screenshots are lossy: mark anything
   unreadable `?` rather than guessing. The monthly CSV export is the fix.
2. **Commit and push** — straight to `main`, one commit, subject
   `log: YYYY-MM-DD <session name>`. Push *before* you reply; he has no way to do it
   afterwards. Use a branch only for what he'd want to review first: `plan.md`,
   this file, `analyse.py`.
3. **Reply in two sentences**, flagging only what earns it:
   - right-side row load, and whether he noted pain
   - were pull-ups first on pull day
   - a lift that moved up, or one stalled 3+ sessions
   - session length, only if it changed sharply — it is not a rule, see `docs/findings.md`

   Nothing notable → say nothing. Silence is a valid response to a normal session.

The occasional jobs — draining the phone-UI queue, logging when git is unreachable,
the monthly reconcile, republishing the page — live in `docs/workflows.md`. Read it
when one comes up, not before.

## Settled — do not relitigate

- **The two-week rotation is real and it is his.** He gave the template on 2026-09-02
  and it is written out in full at the top of `plan.md`. Week A: Push / Football /
  Rest / Pull / Push / Legs+yoga / Pull. Week B: Push / Football / Rest / Pull /
  Football / yoga / Calisthenics. Do not redesign it. Do not infer it from the log.
- **The log tells you about adherence, never about intent.** On 2026-09-01 a session
  deleted the Sunday calisthenics day from `plan.md` because it had zero recorded sets.
  That was wrong — it is a real part of his week that he has not been logging. Absence
  from the export is a question to ask him, not a licence to cut a session. `plan.md`
  keeps the template and the adherence figures in separate sections; keep them separate.
- **The invented calisthenics *contents* are still out.** Front lever holds, pike
  push-ups, L-sits and Nordic curls have zero recorded sets ever. The session is real;
  that exercise list was not. It is now built from movements he actually has history
  with — pull-ups, chin-ups, dips, hanging leg raises, planks.
- **The RDL belongs to the legs day.** It appears on 10 of 11 leg days and on none of
  22 pull days. It was briefly moved to Thursday to patch Week B's hamstring gap; that
  was wrong and has been undone. Do not move it again.
- **Push always ends on triceps (23 of 23 sessions); Pull always ends on a curl
  (22 of 22).** Both days run five exercises. Do not prescribe a sixth without asking.
- **He dislikes leg training.** Legs sit once a fortnight, Week A only, and in practice
  run about monthly. Never push it, never guilt him, never offer "just a short one".
  Week B has no direct leg work by design — that is the accepted trade, not a gap to
  fill by smuggling a leg lift onto another day.
- **Wednesday is a protected rest day.** Late food after Tuesday football. Nothing goes there.
- **Football is fixed** — Tuesday evening, sometimes Friday too, 2h of 7-a-side.
  Schedule under it, never around it.
- **Flat bench was dropped** deliberately to prioritise incline. His call, sound, it stands.
- **The Sep 2025 row drop (80 → 70 → 60kg) is a form change, not the injury.** He
  changed how he rows and reset the load to match. Not pathology, and not a decline.
  Do not discover it again.
- **Right lat injury since June 2026**, under physiotherapy care. He has decided
  against imaging. You are not his physio; their guidance overrides anything here.
  The "left 70kg / right 50kg" split often quoted for this predates the Sep 2025 form
  change and is **not established by any 2026 data** — the only 2026 row session put
  both sides in at 50kg. Treat the gap as unmeasured until he logs the two sides
  separately.

## What his data does and doesn't say

- **Order beats content.** Pull-ups at position 2 → 27 reps; same month at position 5
  → 15. Session order is programming, not a detail.
- **Left and right lat are separate lifts.** Left trains at 70kg and progresses; right
  is governed by pain. Never hold the left back to match the right.
- **Session length is UNKNOWN.** An earlier version of this file called 5–6 exercises
  his tested optimum. It was an artefact of the calendar. Don't reassert it.
- **He is right about his own body more often than the log is.** Three confident
  findings here turned out to be scheduling artefacts read as physiology. Ask why
  before inferring. The log records what he lifted, never why he stopped.

Full working and the open questions: `docs/findings.md`.

## Tone

Direct. He'll push back when you're wrong — take it, correct it, move on. Don't soften
findings into mush, don't over-apologise, don't explain the basics. He isn't a beginner.

## Files

| | |
|---|---|
| `plan.md` | The programme. Edit here when it changes. |
| `log.md` | Session log. Append-only, newest at the bottom. |
| `docs/workflows.md` | The occasional jobs. On demand. |
| `docs/goals.md` | What the training is *for*. Draft until he confirms it. |
| `docs/findings.md` | What the data supports, what it doesn't, what's open. On demand. |
| `analyse.py` | Full analysis of a Strong export. Monthly, not per session. |
| `data/` | Strong CSV exports. Never read directly. |
| `inbox/` | Sessions logged while the repo was unreachable. Empty at rest. |
| `screenshots/` | Optional, if he wants them kept. |
| `ui/matchday.html` | Source of the published phone page. Republish after editing. |
| `README.md` | Orientation for a human landing on the repo. Not for you. |
