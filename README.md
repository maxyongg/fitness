# Matchday Block

Max's training project. Everything Claude needs is in `CLAUDE.md` — read that first.

| File | What it is |
|---|---|
| `CLAUDE.md` | How to work in this repo. Read before anything else. |
| `plan.md` | The programme. Edit here when it changes. |
| `log.md` | Session log. Append-only, newest at the bottom. |
| `analyse.py` | Re-runs the full analysis on a Strong CSV export. |
| `data/` | Strong CSV exports. Never read directly — go through `analyse.py`. |
| `inbox/` | Sessions transcribed while the folder was unreachable. Empty at rest. |
| `screenshots/` | Optional, if screenshots are worth keeping. |

Run the analysis:

```
pip install pandas numpy
python3 analyse.py data/strong_2026-08-31.csv
```

Verified working on pandas 3.0.5 / numpy 2.x as of 2026-09-01.
