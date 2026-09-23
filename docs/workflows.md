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
2. **GitHub Action** (within ~1 minute) — runs `drain.py` (transcribes to `log.md`,
   updates `state.json`), runs `prescribe.py` (bumps `RX.asof` in `index.html`),
   commits everything, deletes the inbox file. Setup: `docs/github-actions-setup.md`.

Re-prescribing (changing loads, exercises, or rep targets) is still a Claude decision
in a manual session — the Action only bumps the date.

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
- **`RX.asof`** — bump the date. The page renders it, and it is how he can tell at a
  glance whether prescriptions are current.

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
