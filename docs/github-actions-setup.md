# GitHub Actions setup — optional faster drain

The Claude routine already handles everything automatically every 3 hours. This
GitHub Action makes the drain step instant: the moment you save a session on your
phone, the log entry is committed within a minute instead of waiting for the next
routine fire.

The routine still handles the debrief, re-prescribing, and doc updates — the Action
only covers the mechanical transcription.

## Why you have to do this yourself

GitHub requires the `workflow` scope to push workflow files. Claude Code's OAuth
token doesn't have it, so this file has to be committed from your local machine or
the GitHub web UI.

## Option A: GitHub web UI (easiest from phone)

1. Go to https://github.com/maxyongg/fitness
2. Click **Add file → Create new file**
3. Name it `.github/workflows/drain.yml`
4. Paste the YAML below
5. Commit directly to `main`

## Option B: local machine

```bash
cd fitness
mkdir -p .github/workflows
cat > .github/workflows/drain.yml << 'YAML'
name: Drain inbox

on:
  push:
    branches: [main]
    paths: ['inbox/*.json']

permissions:
  contents: write

jobs:
  drain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check inbox
        id: check
        run: |
          if ls inbox/*.json 1>/dev/null 2>&1; then
            echo "has_files=true" >> "$GITHUB_OUTPUT"
          else
            echo "has_files=false" >> "$GITHUB_OUTPUT"
          fi

      - name: Run drain.py
        if: steps.check.outputs.has_files == 'true'
        run: python3 drain.py

      - name: Commit and push
        if: steps.check.outputs.has_files == 'true'
        run: |
          subject=""
          count=0
          for f in inbox/*.json; do
            date=$(python3 -c "import json; print(json.load(open('$f'))['date'])")
            session=$(python3 -c "import json; print(json.load(open('$f'))['session'])")
            if [ $count -eq 0 ]; then
              subject="log: $date $session"
            fi
            count=$((count + 1))
          done
          if [ $count -gt 1 ]; then
            subject="$subject (+$((count - 1)) more)"
          fi

          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add log.md state.json
          git rm inbox/*.json
          git diff --cached --quiet && exit 0
          git commit -m "$subject"
          git push
YAML
git add .github/workflows/drain.yml
git commit -m "Add drain workflow"
git push
```

## What happens after setup

1. You save a workout on your phone → JSON lands in `inbox/`
2. **Within ~1 minute:** GitHub Action runs `drain.py`, commits log + state, deletes inbox file
3. **Within ~3 hours:** Claude routine fires, reads the new session, and handles:
   - Session debrief (written as a comment in log.md)
   - Next session prescriptions (RX in index.html)
   - Same-type session update (loads, rep targets)
   - Page update (RX.asof bumped, GitHub Pages current)
   - Documentation (plan.md, state.json, findings if needed)

Without the Action, step 2 is handled by the routine in step 3 — everything still
works, just up to 3h later instead of instantly.

## The YAML to paste

```yaml
name: Drain inbox

on:
  push:
    branches: [main]
    paths: ['inbox/*.json']

permissions:
  contents: write

jobs:
  drain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check inbox
        id: check
        run: |
          if ls inbox/*.json 1>/dev/null 2>&1; then
            echo "has_files=true" >> "$GITHUB_OUTPUT"
          else
            echo "has_files=false" >> "$GITHUB_OUTPUT"
          fi

      - name: Run drain.py
        if: steps.check.outputs.has_files == 'true'
        run: python3 drain.py

      - name: Commit and push
        if: steps.check.outputs.has_files == 'true'
        run: |
          subject=""
          count=0
          for f in inbox/*.json; do
            date=$(python3 -c "import json; print(json.load(open('$f'))['date'])")
            session=$(python3 -c "import json; print(json.load(open('$f'))['session'])")
            if [ $count -eq 0 ]; then
              subject="log: $date $session"
            fi
            count=$((count + 1))
          done
          if [ $count -gt 1 ]; then
            subject="$subject (+$((count - 1)) more)"
          fi

          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add log.md state.json
          git rm inbox/*.json
          git diff --cached --quiet && exit 0
          git commit -m "$subject"
          git push
```
