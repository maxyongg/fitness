You are running unattended in GitHub Actions, straight after the Drain inbox Action wrote
a session from the phone page into `log.md`. Nobody is watching and nobody can answer
you. Your job is step 3 of "The standing job" in `CLAUDE.md`: re-prescribe. This is
programming mode, run without him.

- Last re-prescription (`RX.after`): {{after}}
- Newest session in `log.md`: {{latest}}
- Next session on the template: {{next}}
- Today: {{today}}

## Read first

- `CLAUDE.md` (already loaded), `state.json`, `plan.md`, `docs/goals.md`,
  `docs/incidents.md`.
- `log.md` from the entry named in `RX.after` to the end. Re-prescribe from every
  session in that range. Use Grep to find the line; never read the whole file.
- The `RX` object in `index.html`: from the line `var RX = {` to the line `};`.
  Nothing else in that file.
- The newest files in `debriefs/`, his replies included. What he tells the debrief
  about his body is evidence the log can't hold.
- Never read `data/*.csv`.

## Do

1. **Pass 1, the sessions just logged.** For every slot they touched, update `last`,
   `do` and `why`. `last` comes from `log.md` and only from the same exercise name;
   never quote a number from a different machine. Move the load only when a
   `plan.md` rule fires or something says come down.
2. **Pass 2, the next session.** Make {{next}} current, `brief` included. It is the
   page he opens at the gym.
3. **`plan.md`.** Mirror every change and write the reason next to it.
4. **`log.md`.** Add one short HTML comment under the newest entry, in the style of
   the earlier ones: what moved, what stalled, what changed and why. Never edit or
   remove a logged line.
5. **`RX.asof`** = "{{today}}". **`RX.after`** = "{{latest}}".
6. **`RX.note`**: one or two plain sentences shown at the top of the page. Say what
   changed after this session and why, and ask at most one question. Replace the old
   note; don't append to it.

## Limits

You can't ask him anything. So anything that needs his decision becomes the question in
`RX.note`, not a change.

- Anchors never change exercise. Only their numbers move.
- Never ramp volume. The row protocol governs the right side. His physio overrides
  everything in the repo.
- A rotate slot may change exercise when the data says so: a stall of three sessions,
  a rep band the load doesn't fit, a movement the injury dislikes. Write the reason
  in `plan.md`. A movement he has never logged needs the four-run trial and his
  agreement, so propose it in `RX.note` instead.
- A swap he made in a rotate slot is his choice, not a mistake. A lower load after a
  swap or a form change is not a decline.
- Leave these alone: the weekly template, the "Settled" list in `CLAUDE.md`, and
  anything `plan.md` says he has parked.
- If nothing needs to change, still update the `last` lines, `RX.asof`, `RX.after`
  and `RX.note`.

## Mechanics

- You can only read and edit files. You have no shell and no git. After you finish, the
  workflow checks your edits, rebuilds `state.json` and commits. It rejects the whole
  run if any of these happen:
  - `RX` stops parsing, or `RX.after` isn't "{{latest}}".
  - A file other than `index.html`, `plan.md` or `log.md` changes.
  - Anything in `index.html` outside `RX` changes.
  - A line is removed from `log.md`.
  - An anchor's exercise changes.
- `RX` format: bare keys and double-quoted strings, with no double quotes inside a
  string. Match the surrounding style.
- Skip the `CLAUDE.md` steps that tell you to commit, push, drain the inbox or reply
  to him. The workflow and the page cover them.
- End with two sentences on what you changed. They go to the Action log.
