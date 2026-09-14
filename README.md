# Matchday Block

Max's training project — the programme, the session log, and the analysis that produced
them. The repo is the source of truth; it is run mostly from a phone, with Claude doing
the writing and pushing.

`plan.md` prescribes each session: every slot carries an exercise, a working load, a rep
target and the reason for it, all derived from `log.md` and the Strong exports. A
published phone page renders the same prescriptions and queues saved sessions until a
Claude session writes them into `log.md` and pushes.

If you are Claude, read `CLAUDE.md` first and stop there. This file is for humans.

| File | What it is |
|---|---|
| `CLAUDE.md` | How to work in this repo. |
| `plan.md` | The programme — two-week rotation, row protocol, progression rules. |
| `log.md` | Session log. Append-only, newest at the bottom. |
| `docs/workflows.md` | The occasional jobs: queue drain, offline logging, monthly reconcile. |
| `docs/findings.md` | What the data supports, what it doesn't, what's still open. |
| `docs/incidents.md` | Mistakes made here and the rules that came out of them. |
| `docs/goals.md` | What the training is for. |
| `docs/calisthenics.md` | The beginner calisthenics skill route. |
| `analyse.py` | Re-runs the full analysis on a Strong CSV export. |
| `data/` | Strong exports. Read them through `analyse.py`, not directly. |
| `inbox/` | Sessions logged while the repo was unreachable. Empty at rest. |
| `screenshots/` | Optional. |
| `ui/matchday.html` | Source of the published phone page. |

Run the analysis:

```
pip install pandas numpy
python3 analyse.py data/strong_2026-08-31.csv
```

Verified on pandas 3.0.5 / numpy 2.x as of 2026-09-01.
