# Incidents — what went wrong, and how

`CLAUDE.md` carries the rules. This file carries the reasons, so the rules can stay
short without becoming arbitrary. Read it before asserting anything the data "shows",
and before changing the queue or publish machinery.

Every entry follows the same shape: what was claimed or done, why it was wrong, and the
rule that came out of it.

---

## Reading the data

### Deleting the calisthenics day — 2026-09-01

A session removed the Sunday calisthenics day from `plan.md` because the export showed
zero recorded sets against it. He does the session; he had not been logging it.

**The log tells you about adherence, never about intent.** Absence from the export is a
question to ask him, not a licence to cut a session. `plan.md` keeps the template and
the adherence figures in separate sections — keep them separate.

### Inventing the calisthenics contents — 2026-09-01

Having kept the session, a session then filled it with front lever holds, pike push-ups,
L-sits and Nordic curls. Zero recorded sets, ever, for any of them.

The session was real; that exercise list was not. It is now built from movements he has
history with. **A movement he has never done needs the four-run trial in `plan.md`, not
a quiet insertion.**

### Inventing goals — 2026-09-02

A session inferred four goals — lat parity, an overhead press number, weighted pull-ups,
football availability — and wrote them into the docs as his. His reply: *"None of these
are my actual goals."*

**There is no target and no date.** `docs/goals.md` holds the brief in his own words.
Don't turn a lift that happens to be moving into an objective he never set.

### "Pull days always end on a curl" — 2026-09-02

Miscounted. Pull days *contain* a curl 22 of 22; only 9 of 22 *end* on one, and since
June 12 of 13 end on pull-ups. The wrong version propagated into two documents before
anyone checked.

**State exactly what you computed.** "Contains" and "ends on" are different queries.

### "Core is zero since 9 March" — 2026-09-02

True of the export, false of his training. He does core ad hoc and does not record it.

**Check whether a gap is in the training or only in the log, then ask him.** Rear delts
(3.0 sets/week down to 0.8) is the one gap the data actually supports, because nothing
unlogged fills it.

### Time of day — 2026-09-03

He suspected he was stronger at certain times. Raw numbers favour mornings by 0.39 SD —
entirely a calendar artefact, because he moved from evening training in 2024 to mornings
in 2026 while getting stronger. Within 2026 the spread is 0.09 SD and only 6 of 18 lifts
favour AM.

A null result, and worth having. **De-trend before believing any cross-year comparison.**
Don't re-derive this, and don't tell him he is wrong about how he feels — the log cannot
see it.

### The leg press "regression" — 2026-09-12

`plan.md` listed 130kg for the leg press and 35kg for the leg curl. He logged 80kg and
10kg. Those came from different machines — the Seated Leg Press and the Kneeling Leg
Curl are not the stations the old numbers described.

Caught before it was written down as a decline. Corrected in the table.

### "The 50kg ceiling is gone" — 2026-09-13, withdrawn 09-14

The worst one, because it was confidently reported to him. On 09-13 he rowed 57kg for
two sets of 8 on the **Uni Lateral Seated Row**, both sides equal. A session read that
against the 50kg on the **Iso Lateral Row** and announced the right-side ceiling broken
and the strength-gap story retired.

His correction: *"the seated row is a different exercise from iso lateral. so the 57kg >
50kg is entirely an unreasonable assumption."* Correct. Different machine, different
leverage, loads never on the same scale.

**Never compare loads across machines. Machine identity is part of the measurement.**
The row protocol gates on the right-side iso-lateral row alone; a substitute row, however
similar it looks in Strong, is not a reading on it. This is the second instance of the
same error in three days — see the leg press above — which is why it is now a standing
rule rather than a note.

### "The overhead press regressed because its slot rotates" — asserted, then withdrawn

OHP e1RM ran 49.6 → 60.2 → **61.7** (2026Q1) → 57.0 → 50.7. The rotation explanation was
written into `plan.md` and `CLAUDE.md` as established, and nearly justified anchoring the
slot. It was never tested. The June 2026 lat injury and the two-week August trip cover
the same window, and nobody checked whether slot 2 was already rotating in 2026Q1 when
the lift *peaked*.

Still open; `analyse.py` can settle it at the next export. **A mechanism you have not
tested is a hypothesis, and it goes in `docs/findings.md`, not in a rule.**

---

## The machinery

### Three sessions lost to republishing — 9–10 Sep 2026

Saving a session used to mean republishing the whole page. That fails two ways which
look identical on his phone — the publish is refused because his copy is behind, or the
`artifact` grant is not there — and in both the save fell back to `localStorage` with
nothing to push it up.

Fixed by moving the queue into the artifact's own document store. **The page must declare
`capabilities: {artifact: {}, db: {}}` on every publish**; passing a non-empty
`capabilities` that omits one silently revokes it, which is how the grant lapsed.

### The `outerHTML` snapshot — Sep 2026

`stateDoc()` snapshotted `document.documentElement.outerHTML` from inside the first
script block. That runs mid-parse, so the snapshot stopped at that tag and silently
dropped everything below it — the week lane, the form guide, the boot block. Every save
published a page that could no longer render itself.

Now clones `document.body` and undoes the four things rendering mutates. **Do not go
back to a snapshot taken during parse.**

### Anchors that rotated — Sep 2026

`variantFor` applied the date-derived pick to every slot, including anchors, turning the
calisthenics Pull Up into a Chin Up. The whole point of an anchor is that it does not
move. (The date-derived pick is itself gone now — see below.)

### A logged session that looked unlogged — 2026-09-13

Two faults with opposite symptoms, both reported by him as "it wasn't there".

1. **Drained sessions vanished without trace.** A session left the queue and appeared
   nowhere else — no way to tell "written to `log.md` and pushed" from "the save never
   landed". He re-entered a session because of it. The page now shows a **Written to
   log.md** card.
2. **`syncDb` honoured only one of the two receipts.** It built its already-drained set
   from the store document's `drained: true` flag and never read the `drained` array in
   `mb-state`. Since 09-12 that array is the only receipt a Claude session can write —
   `write_db` refuses every update to an existing document without an `if_version` the
   tool does not expose — so each newly drained session was filtered out by the boot
   block and pushed straight back into the queue three lines later.

Both verified in a headless browser before and after. **Never drop either receipt check.**

### Prefilled sets leaking into the log — 2026-09-14

When the team sheet began opening prefilled at the prescribed load, `markdown()` still
counted a set as performed if it had a *weight*. Every exercise he skipped would have
landed in `log.md` as a bare "65kg".

**Reps or a time make a set. A weight on its own does not.**

---

## The pattern

Seven of the entries above are the same mistake: a number compared to a number it does
not belong with, or a mechanism assumed from a correlation. The calendar explained three
of them, machine identity explained two.

He is right about his own body more often than the log is. **Ask why before inferring**,
and when he pushes back, he is usually correcting a real error — take it, fix it
everywhere it propagated, and move on.
