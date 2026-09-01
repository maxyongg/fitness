# Matchday Block — Max's training repo

Read this, `plan.md`, and the last ~40 lines of `log.md`. That is the whole briefing —
do not ask him to re-explain the background.

Max runs this from his phone, thumb-typing, usually straight after training. He cannot
go and check something on a computer, and he cannot push a commit himself. The GitHub
repo `maxyongg/fitness` is the source of truth; any clone is just a checkout, and
nothing counts until it is pushed.

## Every session

- **Read:** this file, `plan.md`, tail of `log.md`. Nothing else by default.
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

- **Legs are optional.** He dislikes them; Saturday is optional by design. Never push
  it, never guilt him, never offer "just a short one".
- **Wednesday is a protected rest day.** Late food after Tuesday football. Nothing goes there.
- **Football is fixed** — Tuesday evening, sometimes Friday too, 2h of 7-a-side.
  Schedule under it, never around it.
- **Flat bench was dropped** deliberately to prioritise incline. His call, sound, it stands.
- **The Sep 2025 row drop (80 → 70 → 60kg) is a form change, not the injury.** He
  changed how he rows and reset the load to match. Not pathology, and not a decline.
  Do not discover it again.
- **Right lat injury since June 2026**, under physiotherapy care. Left rows 70kg, right
  ~50kg and painful there. He has decided against imaging. You are not his physio;
  their guidance overrides anything here.

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
| `docs/findings.md` | What the data supports, what it doesn't, what's open. On demand. |
| `analyse.py` | Full analysis of a Strong export. Monthly, not per session. |
| `data/` | Strong CSV exports. Never read directly. |
| `inbox/` | Sessions logged while the repo was unreachable. Empty at rest. |
| `screenshots/` | Optional, if he wants them kept. |
| `ui/matchday.html` | Source of the published phone page. Republish after editing. |
| `README.md` | Orientation for a human landing on the repo. Not for you. |
