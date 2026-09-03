# The occasional jobs

Not needed on a normal logging session. Read the one you need.

## Draining the phone-UI queue

The published page is **Matchday Block**,
<https://claude.ai/code/artifact/0f918bd3-56b5-439a-9d0d-fbd51a5a0a9b>, built from
`ui/matchday.html`. Three lanes: *week* (the Mon–Sun rotation, Week A or B, Log button
per day), *team sheet* (captures a session), *form guide* (what the last export says).

### How `mb-state` works

The page's `<script id="mb-state">` holds two things:

- **`queue`** — sessions he has saved and nobody has written to `log.md` yet. These live
  **only on the live page**; the repo copy is always empty.
- **`drained`** — a receipt: the ids already written into `log.md`. This one *is* kept in
  the repo file, and the page uses it to ignore anything it sees again, so a stale
  `localStorage` copy on his phone cannot resurrect a session that has already been
  logged. Keep it when you edit the file; never clear it to "tidy up".

### Read this before you republish anything

**Publishing the repo file overwrites the live `queue` with nothing.** Any session he
saved and you have not yet drained is gone from the page.

This applies to *every* republish, not just a drain — a one-line CSS tweak wipes the
queue exactly as thoroughly as a rewrite. It is the single easiest way to lose his data
in this project.

Two things soften it, neither of which is a reason to be careless: the page also keeps
the queue in the browser's `localStorage` and merges it back on load, so **his own phone**
will usually still have the entries; and the publish is refused outright if this
conversation has not read the live version first, which forces the check below.

Nothing wakes this session when he saves something. There is no working subscription —
attempts return 403. **The queue is only ever found by looking.** Read the artifact at
the start of any programming session, and whenever he mentions having trained.

### The safe procedure — follow it for every publish

1. **`Artifact` with `action: "read"` and the URL.** Always first. This is both the
   safety check and what the publish guard requires.
2. **Find `<script id="mb-state">` in the returned HTML and look at `queue`.**
   - Empty (`{"queue":[]}`) → carry on to step 4.
   - Not empty → do step 3 before touching the page.
3. **Drain it.** Each entry carries a ready-made `md` block. Append them to `log.md` in
   date order — they are already in log format, so check them, don't rewrite them —
   then commit and push. Only once that push has succeeded is it safe to publish over
   them.
4. **Publish `ui/matchday.html`**, having first added the drained ids to its `drained`
   array. The empty `queue` now correctly reflects reality because you just drained it,
   and the receipt stops those entries coming back. Never hand-copy *queue* JSON into
   the repo file to "preserve" it — `log.md` is the record, the page is only a buffer.

If a publish is refused because someone republished in between, re-read and start again
from step 1. Do not use `force`.

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
