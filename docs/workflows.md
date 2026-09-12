# The occasional jobs

Not needed on a normal logging session. Read the one you need.

## Draining the phone-UI queue

The published page is **Matchday Block**,
<https://claude.ai/code/artifact/0f918bd3-56b5-439a-9d0d-fbd51a5a0a9b>, built from
`ui/matchday.html`. Three lanes: *week* (the Mon–Sun rotation, Week A or B, Log button
per day), *team sheet* (captures a session), *form guide* (what the last export says).

### Where a saved session actually lives

Since 2026-09-10 the queue lives in **the artifact's own document store** (`db`), one
document per session in the `queue` collection. That is the record. The page also keeps
a `localStorage` copy on his phone, written first and always, and reconciled into the
store on the next load.

The `<script id="mb-state">` block still carries two things, but both are now secondary:

- **`queue`** — the legacy buffer, used only if the store cannot be reached. The repo
  copy is always empty.
- **`drained`** — the pre-db receipt: ids written into `log.md` before the store
  existed. Keep it; never clear it to "tidy up". New drains are recorded in the store
  instead, by flagging the document `drained: true`.

**The page declares `capabilities: {artifact: {}, db: {}}`.** Both must stay declared.
Passing a non-empty `capabilities` that omits one revokes it, and a page that cannot
reach either can only save to the phone — which is exactly the failure below.

### Reading the queue from a Claude session

No need to open the page at all:

```
Artifact  action: "read_db"  url: <the artifact>  db_op: "list"  collection: "queue"
```

`No documents matched` means the queue is empty (the store is created on first write).

### If a save looks like it vanished

**What happened on 9–10 Sep 2026, and the reason the store exists.** Saving used to mean
republishing the whole page. That fails in two ways that look identical to him — the
publish is refused because his page was behind the live version, or the `artifact` grant
is not there at all — and in both the save fell back to `localStorage` with nothing to
push it up. Three sessions' worth of work sat invisible on his phone.

A one-document write has neither failure mode. What remains:

1. **Ask him to reload the page.** On load the page pushes anything in `localStorage`
   that the store has never seen, and says so on screen. This is the recovery path and
   it is usually enough.
2. **Check the store** with `read_db` above.
3. If it is still not there, the queue card shows a coloured banner naming the problem —
   ask him what it says. `This phone only` means neither capability resolved, and the
   **Copy** button per entry is the way out: the markdown is already in log format, so
   he can paste it straight into the chat.

Never tell him a save is lost without checking `localStorage` recovery first. It almost
never is.

### Read this before you republish anything

The old hazard — *publishing the repo file wipes the live queue* — **is gone for anything
in the store.** Republishing no longer touches `db`. This is the main reason for the
change.

Two caveats keep the check worth doing:

- A session saved while the store was unreachable sits in the legacy `mb-state.queue` on
  the live page, and publishing over it *does* still destroy it.
- The publish is refused outright unless this conversation has read the live version
  first, so you cannot skip the read anyway.

**Nothing wakes this session when he saves.** Wake subscriptions do not register here
(the gateway returns 404; it was 403 before). The queue is still only ever found by
looking. Check it at the start of any programming session and whenever he mentions
having trained.

### The safe procedure — follow it for every publish

1. **`read_db`** the `queue` collection. That is the real queue.
2. **`Artifact` with `action: "read"` and the URL.** Still required — it is what the
   publish guard checks — and it shows whether the legacy `mb-state.queue` holds
   anything.
3. **Drain whatever either one holds.** Each entry carries a ready-made `md` block.
   Append them to `log.md` in date order — they are already in log format, so check
   them, don't rewrite them — then commit and push.
4. **Mark them drained, only after the push succeeded.** Marking rather than deleting
   is deliberate: his phone's `localStorage` copy would otherwise walk the session
   straight back in on the next load.

   **Use the `drained` array in `ui/matchday.html`, not `write_db`.** The obvious route
   — `write_db` with `db_op: "update"` setting `drained: true` — no longer works from a
   Claude session. Every write against a document that already exists is refused with
   `version_mismatch` unless it carries `if_version`, and the `Artifact` tool exposes no
   such parameter; `db_op: "set"` is refused the same way, and putting `if_version`
   inside `data` does nothing. Confirmed 2026-09-12 draining the legs session. So add
   the id to the array at `#mb-state` instead and republish. The page treats the two
   identically — the boot block filters the queue against `drained` before anything
   renders — so the session stays out of his queue either way. The store document keeps
   `drained: false` forever and that is now cosmetic; **the array is the receipt.**
   The same array was always the route for legacy entries.

   If `write_db` ever starts accepting `if_version`, go back to flagging the document:
   it survives a stale republish, and the array does not.
5. **Publish `ui/matchday.html`** if you changed it, with `capabilities` naming both
   `artifact` and `db`.

If a publish is refused because someone republished in between, re-read and start again.
Do not use `force`.

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
