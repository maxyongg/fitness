# The occasional jobs

Not needed on a normal logging session. Read the one you need.

The failures described below are summarised with the rest of this project's mistakes in
`docs/incidents.md`. This file is the procedure; that one is the reasoning.

## Draining the inbox

The phone page at `https://maxyongg.github.io/fitness/` (source: `index.html`) saves
sessions as JSON files to `inbox/` via the GitHub API. Each file is named
`{date}-{session-id}.json` and contains the full session data: exercises, weights, reps,
pain rating, notes, and extras.

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
3. **Re-prescribe routine** (14:00 and 22:00 SGT). A scheduled Claude Code session on
   his Claude plan, so there's no API bill. If `log.md` is ahead of `RX.after`, it
   re-prescribes from `docs/represcribe-prompt.md` (the steps below, unattended).
   `represcribe.py finish` checks the edits, then it pushes to `main`. His next session
   is never the same day, so twice a day is always in time.

A Claude session that finds the log ahead of `RX.after` re-prescribes from there by
hand, the same way. The routine would otherwise pick it up at its next run.

### The routine

Routine "Re-prescribe after logged sessions", cron `0 6,14 * * *` (UTC), a fresh session
each run, created 2026-09-24 at his request. It replaced a Re-prescribe GitHub Action
that billed about $1 a session in API credits; that Action is still documented in
`docs/github-actions-setup.md` if instant re-prescription is ever worth paying for. The
routine's instructions, verbatim:

> Scheduled check for Max's training repo, maxyongg/fitness. Work on `main` and push
> to `main`: that is his standing instruction in the repo's CLAUDE.md, so don't create
> a branch or a pull request.
>
> 1. Get the latest `main`. Clone https://github.com/maxyongg/fitness if it isn't
>    checked out; otherwise `git checkout main && git pull origin main`.
> 2. Run `python3 represcribe.py pending`. If it prints `pending=false`, stop there:
>    reply "Nothing to re-prescribe." and end. Read nothing else.
> 3. If it prints `pending=true`, run `python3 represcribe.py prompt` and do what it
>    says. It is the full brief.
> 4. Run `python3 represcribe.py finish`. If it reports errors, fix your edits and run
>    it again. Never work around it.
> 5. `git add index.html plan.md log.md state.json`, commit with the subject `finish`
>    printed, and `git push origin main`. If the push is rejected,
>    `git pull --rebase origin main` and push again.
> 6. Reply with the two-sentence summary the brief asks for.

To change what it does, change `docs/represcribe-prompt.md` or `represcribe.py`; the
routine reads both fresh each run.

### Manual draining procedure

Use this when the Action hasn't run (e.g. it failed, or you're in a Claude session
that finds unprocessed files in `inbox/`).

1. **Run `python3 drain.py`.** It reads every JSON in `inbox/`, appends formatted entries
   to `log.md`, updates `state.json`, and prints an editorial summary. If the inbox is
   empty it says so and exits.
2. **Read the stdout summary.** It tells you the session, pain reading, next session, and
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
current. **This is the one he opens at the gym.** An Upper B that ends with a bad pain
reading should change the Upper C that follows; carrying a finding across sessions is
the job.

For every slot you touch, update both `plan.md` and the `RX` object in `index.html`:

- **Load** — moves only when a progression rule fires or something says come down.
  Write the reason into `plan.md`.
- **The exercise itself** — rotate slots are yours to change when the data says so
  (a stall of three, a rep band that does not fit, a movement the injury dislikes).
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

## Monthly: a new export lands in `data/`

When he drops a fresh Strong CSV export in `data/`:

```
pip install pandas numpy      # if the session lacks them
python3 analyse.py data/<latest export>.csv
```

Verified on pandas 3.0.5 / numpy 2.x as of 2026-09-01.

Then reconcile `log.md` against the export — loads, reps, and above all the order
exercises were performed in. Fix errors silently and leave an HTML comment saying what
was corrected, as with the 2026-08-31 entry. Update the baseline comment at the foot of
`log.md` if the headline numbers moved.

`analyse.py` uses the performed order deliberately. Ignoring that ordering is what
produced three wrong conclusions in this project. Don't drop it.
