# The occasional jobs

Not needed on a normal logging session. Read the one you need.

## Draining the phone-UI queue

The published page is **Matchday Block**,
<https://claude.ai/code/artifact/0f918bd3-56b5-439a-9d0d-fbd51a5a0a9b>, built from
`ui/matchday.html`. Three lanes: *week* (the Mon–Sun rotation, Week A or B, Log button
per day), *team sheet* (captures a session against the prescribed line-up), *form
guide* (what the last export says).

Published pages cannot call GitHub, so the page holds saved sessions inside itself and
**you** are what moves them into the repo. When he says the queue has something in it:

1. `Artifact` with `action: "read"` and that URL. Saved sessions are JSON in the
   `<script id="mb-state">` tag, each carrying a ready-made `md` block.
2. Append those blocks to `log.md` in date order. They are already in log format —
   check them, don't rewrite them.
3. Commit and push.
4. Republish `ui/matchday.html` with `url` set to that artifact, **having first cleared
   the drained entries from the `mb-state` JSON**. Skip this and everything in the
   queue gets written twice next time.

### Three ways a session reaches the queue

The team sheet lane accepts all three, and all three end up as the same `md` block:

1. **Tapped in against the template** — the prescribed line-up, with the rotating slots
   already picked.
2. **Pasted from Strong** — he shares the workout from Strong as plain text and pastes
   the lot, trailing `link.strong.app` URL included. The page parses the title, the
   date, every exercise and every set, and hands back an **editable** session rather
   than a blind import. It reads `40 kg × 10`, `12 reps`, `1:00` and lbs, and a generic
   title like "Morning Workout" is replaced by the session type guessed from the
   exercises. Exercise names are kept exactly as Strong writes them, so they match the
   CSV export.
3. **Free-text rows** — the "anything else you did" box at the bottom of every session,
   for ad hoc core and finishers.

A screenshot in the chat is still fine and still the fastest for a single session. What
the page adds is `pain(R)` and the ad hoc work — neither of which a screenshot can give
you, and `pain(R)` has never once been logged.

## Keeping the page in step with the programme

`plan.md` is the source for the week lane and the line-ups. Change the programme there
and you must update `WEEK` and `SESSIONS` in `ui/matchday.html` and republish, or the
page goes quietly stale.

## When the repo is not reachable

Git failing — no network, auth trouble, a checkout you can't push — is not a reason to
stall, and not something he can fix from a phone. Instead:

1. Transcribe the session into your reply as a fenced block in `log.md` format.
2. Tell him in one line that it is not committed yet.
3. If the working copy is writable, also write it to `inbox/YYYY-MM-DD.md`.

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
