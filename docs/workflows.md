# The occasional jobs

Not needed on a normal logging session. Read the one you need.

The failures described below are summarised with the rest of this project's mistakes in
`docs/incidents.md`. This file is the procedure; that one is the reasoning.

## Draining the inbox

The phone page at `https://maxyongg.github.io/fitness/` (source: `index.html`) saves
sessions as JSON files to `inbox/` via the GitHub API. Each file is named
`{date}-{session-id}.json` and contains the full session data: exercises, weights, reps,
notes, and extras.

The page also stores sessions locally in `localStorage` under `matchday_history` and can
pull from `inbox/` via its History tab, so saved sessions are visible to him even before
draining. The page's Import tab can also parse pasted Strong text and save to `inbox/`.

### Automated path (normal case)

When a session is saved from the phone page, two things happen automatically:

1. **Instant debrief** — the browser calls the Cloudflare Worker, which returns a
   2-4 sentence AI debrief card on screen within seconds. PIN-gated; doesn't write
   to the repo. Setup: `docs/cloudflare-worker-setup.md`.
2. **Drain inbox Action** (within ~1 minute) — runs `drain.py` (transcribes to
   `log.md`, updates `state.json`), commits, deletes the inbox file.
3. **Re-prescribe routine** (22:00 SGT, Mon/Thu/Sat/Sun). A scheduled Claude Code
   session on his Claude plan, so there's no API bill. If `log.md` is ahead of
   `RX.after`, it re-prescribes from `docs/represcribe-prompt.md` (the steps below,
   unattended). `represcribe.py finish` checks the edits, then it pushes to `main`. His
   next session is never the same day, so a 10pm run on each training day is in time
   for the next one. A session logged on an off day waits for the next training-day
   run.

A Claude session that finds the log ahead of `RX.after` re-prescribes from there by
hand, the same way. The routine would otherwise pick it up at its next run.

### The routine

Routine "Re-prescribe after logged sessions" (`trig_01FRxLVvPLuBk3PWCWvc3hvp`), cron
`0 14 * * 0,1,4,6` (UTC = 22:00 SGT, same day), a fresh session each run, created
2026-09-24 at his request. It runs on the routine default model (Sonnet 5 at setup)
and counts toward his Claude plan's usage. An empty check used ~$0.30 of
API-equivalent allowance in the setup test, so it runs only on his training days (his
call). The page's `nextRunLabel()` hard-codes the same days; change both together. It
replaced a Re-prescribe GitHub Action that
billed about $1 a session in API credits. That Action is still documented in
`docs/github-actions-setup.md` if instant re-prescription is ever worth paying for. The
routine's instructions, verbatim:

> Scheduled check for Max's training repo, maxyongg/fitness. Work on `main` and push
> to `main`: that is his standing instruction in the repo's CLAUDE.md, so don't create
> a branch or a pull request.
>
> 1. Get the latest `main` with push access. If the repo is already checked out (look
>    for `fitness/` under /home/user), `cd` into it and
>    `git checkout main && git pull origin main`. If it isn't, attach it first with the
>    add_repo tool (Claude_Code_Remote; try ToolSearch if it isn't listed) for owner
>    maxyongg, repo fitness, access "push", then clone with the command it gives you
>    and `git checkout main`. A plain `git clone` without add_repo reads the repo but
>    can never push to it, so if the repo isn't checked out and add_repo is missing or
>    refuses, stop and reply "Re-prescription not done: the routine has no push access
>    to maxyongg/fitness — add the repo to the routine in its settings."
> 2. Run `python3 represcribe.py pending`. If it prints `pending=false`, stop there:
>    reply "Nothing to re-prescribe." and end. Read nothing else.
> 3. Prove you can push before doing any work: `git push --dry-run origin main`. If it
>    fails, stop, change nothing, and reply "Re-prescription not done:" followed by the
>    exact error.
> 4. Run `python3 represcribe.py prompt` and do what it says. It is the full brief.
> 5. Run `python3 represcribe.py finish`. If it reports errors, fix your edits and run
>    it again. Never work around it.
> 6. `git add index.html plan.md log.md state.json`, commit with the subject `finish`
>    printed, and `git push origin main`. If the push is rejected,
>    `git pull --rebase origin main` and push again. If you can't push at all, say
>    exactly which step failed in your reply.
> 7. Reply with the two-sentence summary the brief asks for.

**It must have push access, and at first it didn't (2026-09-26).** The first real run,
after the 09-26 Upper C, did the whole re-prescription and then couldn't push. The
routine was created from a Claude session through the remote-session tools, and a
routine made that way stores no repository and no connectors. So its session had no
repo checked out and no `add_repo` tool. The repo is public, so a plain `git clone`
worked, but a clone like that can't push. The re-prescription was done by hand that
night. **The fix has to be made in the routine's own settings** (claude.ai/code →
Routines → this routine): add `maxyongg/fitness` as its repository. A Claude session
can't attach one to a routine. Until that's done, the routine stops at step 1 or 3 and
says why, in about a minute, instead of doing 12 minutes of work and losing it. The
same night also turned up a bug in `represcribe.py finish`: running it a second time
rejected the `state.json` its first run had written. That is fixed.

To change what it does, change `docs/represcribe-prompt.md` or `represcribe.py`; the
routine reads both fresh each run.

### Manual draining procedure

Use this when the Action hasn't run (e.g. it failed, or you're in a Claude session
that finds unprocessed files in `inbox/`).

1. **Run `python3 drain.py`.** It reads every JSON in `inbox/`, appends formatted entries
   to `log.md`, updates `state.json`, and prints an editorial summary. If the inbox is
   empty it says so and exits.
2. **Read the stdout summary.** It tells you the session, next session, and
   any flags worth attention.
3. **Commit `log.md` + `state.json`, delete the inbox files, push to `main`.** One commit,
   subject `log: YYYY-MM-DD <session name>`.
4. **Re-prescribe — required, every drain.** See below.

### Re-prescribing after a drain

The page is static HTML on GitHub Pages. Prescriptions only move when you move them.

**Two passes, and the second is the one that matters.**

**Pass 1 — the session he just did.** Update its exercise data in the `RX` object in
`index.html` so the loads and rep expectations reflect what happened.

**Pass 2 — the session he does next.** Work out which it is from the weekly template
(Mon Upper A / Thu Upper B / Sat Upper C / Sun Lower), then make that whole session
current. **This is the one he opens at the gym.** An Upper B that ends badly
should change the Upper C that follows; carrying a finding across sessions is
the job.

For every slot you touch, update both `plan.md` and the `RX` object in `index.html`:

- **Load** — moves only when a progression rule fires or something says come down.
  Write the reason into `plan.md`.
- **The exercise itself** — rotate slots are yours to change when the data says so
  (a stall of three, a rep band that does not fit, a movement he says doesn't sit right).
  Write the reason into `plan.md`; a silent swap is the thing the prescription model
  replaced.
- **`last`, `do`, `why`** — the three lines the page prints on every slot. `last` is
  what he did last time on *that machine*, from `log.md` (never a number from a different
  station); `do` is today's instruction in a sentence or two; `why` is the reason the
  slot is what it is. Each session also carries a one-line `brief`. A stale `last` is
  worse than none, so rewrite it whenever the slot runs.
- **`RX.asof`** — bump the date. **`RX.after`** — the session re-prescribed from,
  as "YYYY-MM-DD Name" matching its `log.md` header. The page shows "Prescribed after
  …", and "updating" while a newer save is waiting. **`RX.note`** — one or two sentences
  at the top of the next session: what changed and why, and at most one question.

- **`call`** — on every slot the load review calls flat (and on any other slot with
  something to say): the decision and its reason in a sentence or two. `python3
  review.py` prints the review; it is also the `review` at the end of `state.json`.
  Each session's **`short`** lists the slot indexes of its flat-day version, the same
  slots its brief's "Flat? …" names. `represcribe.py finish` checks both.
- **Which session is next** is the one he's owed, not the weekday's: `python3 review.py
  --next`, the same rule the page and the widget run (`plan.md`, "When life interferes").

Keep `RX` in its current shape: bare keys, double-quoted strings. `drain.py` parses it
and `prescribe.py` rewrites `asof:` by regex.

Anchors keep their exercise always; only their numbers move.

Commit both files to `main` and push.

## Keeping the page in step with the programme

`plan.md` is the source for the programme. Change it and you must also update the `RX`
object in `index.html` and push to `main`, or the page goes quietly stale.

## When the repo is not reachable

Git failing — no network, auth trouble, a checkout you can't push — is not a reason to
stall, and not something he can fix from a phone. Instead:

1. Transcribe the session into your reply as a fenced block in `log.md` format.
2. Tell him in one line that it is not committed yet.
3. If the working copy is writable, write it to `inbox/YYYY-MM-DD-<session>.json` in
   the same format the phone page uses.

The next session that can reach the repo appends it to `log.md`, deletes the inbox
file in the same commit, and pushes.

## Apple Health: `data/health.json`

He wears an Apple Watch for football and some lifting (from 2026-10-30). Two routes put
it in `data/health.json`, and neither needs a Claude session:

- **After each workout: the shortcut.** An iPhone automation fires when a watch workout
  ends and runs the shortcut "Matchday watch". It uploads the watch's heart-rate
  readings (and active energy) for the last day to `inbox/watch-<time>.txt`. The
  Watch upload Action (`.github/workflows/watch.yml`) runs `watch.py`, which finds the
  workout as a block of dense readings, adds a summary marked `"via": "shortcut"`, and
  deletes the upload. If the phone was locked when the workout ended, iOS blocks Health
  and nothing goes up, which is most days. So the page has a **Send watch data**
  button (debrief card, Football tab, History, added 2026-11-07) that runs the shortcut
  through `shortcuts://run-shortcut`, then checks `data/health.json` every 15s for three
  minutes and says when the workout is in. `WATCH_SHORTCUT` in `index.html` must match
  the shortcut's name on his phone ("HR Upload Automation"). Tapping the shortcut in
  Shortcuts does the same.
  Re-sending is harmless: a newer upload replaces the older record for the same stretch.
- **Now and then: the Health export** (Import tab → Apple Health), for backfill or after
  a gap. Health app → profile picture → Export All Health Data → Save to Files, then
  pick the zip on the page. It is read **on the phone**. Its records are Apple's own
  (exact start/end, workout type, workout time), and they replace any shortcut record
  they overlap. Each export is the phone's full history, so re-importing is safe.

Shortcuts can't read a workout record out of Health (there is no Workouts type in Find
Health Samples, checked on his phone 2026-11-04). It reads samples only, which is why
`watch.py` has to find the workout itself.

**Privacy.** The repo is public. Only workout summaries are kept: date, times, type,
minutes, kcal, km, and heart rate as average/min/max plus minutes per 10-bpm band, and
since 2026-11-14 (he asked for the graph) each watch workout's heart-rate curve in
`data/hr/YYYY-MM.json`: 15-second means over the workout's own minutes, nothing outside
them. History draws it when a watch workout is opened. A
shortcut upload holds up to a day of raw readings, overnight included. It sits in
`inbox/` for about a minute and stays in git history. **His choice, 2026-11-05**, over
sending uploads to the Cloudflare Worker, which would find the workout there and commit
only the summary, keeping raw readings out of the repo entirely. That route is still
open if he changes his mind: Worker endpoint plus a GitHub token secret on the Worker,
and step 8 pointed at the Worker with the PIN. The full Health export never reaches
the repo. Don't ask for it, and don't add daily data (resting HR, HRV,
sleep, weight) without asking him first.

- **Reading it:** `python3 health.py` (last 12 weeks; `--since`, `--all`; `--curve`
  adds each workout's curve as 5-minute means). Football
  rows carry the log's effort and load, lifting rows the log's session name. Workouts
  Strong wrote to Health have no heart rate and are hidden unless `--all`.
- **Curves.** `watch.py` keeps one per shortcut workout, and the page's Health import
  writes them for the watch's workouts of the last 180 days (its readings carry
  seconds, so they replace a shortcut's). His phone prints the shortcut's times to the
  minute only, so within a minute the readings are spread evenly, in the watch's order.
  **The Watch upload Action must commit `data/hr/`** (`watch.yml`, `git add`); if a
  curve is missing for a workout in `health.json`, `python3 watch.py --from-git`
  rebuilds every curve from the uploads in git history, then commit `data/hr/`.
- **Football** is the Soccer type, or any workout that fills 45+ minutes of a
  `RX.football` slot. A shortcut workout outside a slot is `lifting` on a lift day and
  `other` otherwise; it can't tell a walk from a session.
- **`min` differs by route.** From the export it's workout time, which leaves out
  pauses; from the shortcut it's elapsed time. The 10-30 match was 102 min of workout
  time in 116 elapsed. The log's 80 min is minutes on the pitch by format, a third
  number. Don't reconcile them.
- **The bands assume no max HR or zones.** If zones ever matter, ask him. Don't
  estimate a max from age.
- **A watch upload stuck in `inbox/`** means `watch.py` couldn't read it (the Action run
  failed). Run `python3 watch.py inbox/<file>` to see why. The likely cause is a date
  format `parse_when()` doesn't know yet: add it, then run `python3 watch.py`, commit
  `data/health.json` and the deletion, and push. **`data/health.json` must exist**, even with
  no workouts in it: the Action's `git add` fails without it. That failed the first
  four uploads (2026-11-05). Fixing the Action file needs him, because Claude sessions
  can't push workflow files; keeping the file in place avoids the problem.

**On the page** (2026-11-05, at his request): History is one list. Each session saved
from the phone shows the watch workout recorded alongside it (same date, football with
football, a lift with anything else), and watch workouts no session claims get cards
of their own. Only the Apple Watch's workouts are shown; the import also holds Strong's
and his WHOOP's (Jul 2025 to Jul 2026), which only `health.py --all` lists.

**Other devices' heart rate** (2026-11-05, his ask: a year of WHOOP football to compare
against). The import's first pass keeps the watch's readings and counts other apps'
heart-rate readings. If an app that recorded workouts (the WHOOP) also saved heart rate,
a second pass reads the file again for that app's readings inside its own workouts
only, since all of them could be tens of millions. Each workout takes heart rate from
its own device; Strong's workouts don't borrow the WHOOP's. If the WHOOP's readings are
sparser than one a minute, its band minutes undercount (each reading counts for at most
a minute), though average and max still hold. `python3 health.py --all --since
2025-07-01` shows them, marked [WHOOP]. Until a re-import after this change, the WHOOP
workouts have no heart rate.

**The debrief reads it.** While he's wearing the watch (an Apple Watch workout in the
last 14 days), saving a lift doesn't start the debrief. The card waits with a button,
and he taps it once the shortcut's upload is in (his plan: the debrief should see the
watch data). The page sends the session to the Worker with `watch` (this session's
workout) and `watch_recent` (the week before) attached, and the Worker adds a WATCH
section to the prompt. If he taps before the upload arrives, the page asks first.

Heart rate is context for the lifts around football, not a target.

### Setting up the shortcut (on his phone, once)

New shortcut "Matchday watch":

1. **Find Health Samples**: Type Heart Rate. Filters: Start Date *is in the last* 1
   day; Source *is* his Apple Watch. Sort by Start Date, Oldest First. No limit. A
   window shorter than a day can't be set: the date filters are *is on*, *is today*,
   *is between* and *is in the last* (days and up), and *is between* compares dates
   only, so "between 6 hours ago and now" finds nothing. Checked on his phone
   2026-11-05.
2. **Get Details of Health Sample**: Value.
3. **Get Details of Health Sample**: Start Date, with its input set to step 1's Health
   Samples.
4. **Find Health Samples**: Type Active Energy, same filters and sort. The Source
   filter matters here: the iPhone records active energy too, and without it a
   session with the phone in a pocket counts twice. Steps 4–6 are
   optional; without them there's no kcal.
5. **Get Details of Health Sample**: Value, input step 4.
6. **Get Details of Health Sample**: Start Date, input step 4.
7. **Text**, exactly these lines, with each `[...]` a variable:
   ```
   matchday-watch 1
   sent: [Current Date]
   hr:
   [step 2]
   times:
   [step 3]
   kcal:
   [step 5]
   kcal times:
   [step 6]
   ```
8. **Base64 Encode**: input the Text; Line Breaks None.
9. **Format Date**: Current Date, Custom format `yyyyMMdd-HHmmss`.
10. **Get Contents of URL**:
    `https://api.github.com/repos/maxyongg/fitness/contents/inbox/watch-[step 9].txt`,
    Method PUT, Header `Authorization` = `token ` + the page's GitHub token, Request
    Body JSON: `message` (Text) `watch upload`, `content` (Text) = step 8.

Two iPhone settings, both found missing while setting it up (2026-11-05): Settings →
Privacy & Security → Health → Shortcuts must allow reading Heart Rate and Active
Energy (refused, iOS returns nothing rather than an error), and Settings → Apps →
Shortcuts → Advanced → **Allow Sharing Large Amounts of Data** must be on (off, the
upload stops with "trying to share N Health items").

Then Automation → + → **Apple Watch Workout** → *Is Ended*, any workout → Run
Immediately → Run Shortcut "Matchday watch". **On his phone** the shortcut is named
**HR Upload Automation**, and Shortcuts uses the newer layout: the automation is a
shortcut whose first block is the trigger, and the › beside "Ended" opens Automation
(on), Notify (on) and Confirm Before Run (off, the old "Run Immediately"). First real
run 2026-11-05, Upper B: the automation fired with the phone locked and nothing went
up; tapping the shortcut afterwards worked (12:51–14:09, 935 readings). Add the shortcut to the Home Screen as the
catch-up button. The token lives in the shortcut, so the shortcut is never shared.

## Monthly: a new export lands in `data/`

When he drops a fresh Strong CSV export in `data/`:

```
pip install pandas numpy      # if the session lacks them
python3 analyse.py data/<latest export>.csv
```

Verified on pandas 3.0.5 / numpy 2.x as of 2026-09-01.

Then rebuild the phone page's full history, so the Progress tab's records and muscle map
reach back past `log.md`:

```
python3 history.py            # latest data/strong_*.csv → data/history.json
```

It keeps only sessions dated before the first `log.md` entry; from there on `log.md` is
the record. Commit `data/history.json` with the reconcile.

Then reconcile `log.md` against the export — loads, reps, and above all the order
exercises were performed in. Fix errors silently and leave an HTML comment saying what
was corrected, as with the 2026-08-31 entry. Update the baseline comment at the foot of
`log.md` if the headline numbers moved.

`analyse.py` uses the performed order deliberately. Ignoring that ordering is what
produced three wrong conclusions in this project. Don't drop it.
