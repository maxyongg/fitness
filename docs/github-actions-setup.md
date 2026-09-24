# GitHub Actions — automatic drain

A GitHub Action runs whenever a session JSON lands in `inbox/`. Within a minute
it runs `drain.py` (transcribes to `log.md`, updates `state.json`), commits, and
deletes the inbox file. The prescriptions are then updated by a twice-daily routine
on his Claude plan (`docs/workflows.md`). No manual intervention needed. (`drain.yml` still calls `prescribe.py`,
which is now a no-op; drop that line the next time you edit it.)

## Why workflow changes have to be done manually

GitHub requires the `workflow` scope to push workflow files. Claude Code's OAuth
token doesn't have it, so `.github/workflows/drain.yml` has to be committed from
your local machine or the GitHub web UI.

## Updating the workflow

### Option A: GitHub web UI (easiest from phone)

1. Go to https://github.com/maxyongg/fitness
2. Navigate to `.github/workflows/drain.yml`
3. Click the pencil icon to edit
4. Replace the contents with the YAML below
5. Commit directly to `main`

### Option B: local machine

```bash
cd fitness
# edit .github/workflows/drain.yml, then:
git add .github/workflows/drain.yml
git commit -m "Update drain workflow"
git push
```

## Current YAML

This matches what is deployed on `main` as of 2026-09-23:

```yaml
name: Drain inbox

on:
  push:
    branches: [main]
    paths: ['inbox/*.json']

permissions:
  contents: write

# One drain at a time, each starting from the latest main, so two quick saves
# can't drain the same inbox file twice.
concurrency:
  group: drain
  cancel-in-progress: false

jobs:
  drain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main

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

      - name: Run prescribe.py
        if: steps.check.outputs.has_files == 'true'
        run: python3 prescribe.py

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
          git add log.md state.json index.html
          git rm inbox/*.json
          git diff --cached --quiet && exit 0
          git commit -m "$subject"
          # The page commits debriefs to main while this runs; rebase onto them and retry.
          for i in 1 2 3 4; do
            git push && exit 0
            sleep $((i * 3))
            git pull --rebase origin main
          done
          exit 1
```

## What happens

1. You save a workout on your phone → JSON lands in `inbox/` on `main`
2. **Within ~1 minute:** GitHub Action runs `drain.py` + `prescribe.py`,
   commits `log.md` + `state.json` + `index.html`, deletes inbox file
3. The Cloudflare Worker handles the instant debrief separately —
   see `docs/cloudflare-worker-setup.md`

## Deploy Worker

Deploys the debrief Worker (`worker/`) on every push to `worker/` on `main`, and on
demand from Actions → Deploy Worker → Run workflow. Needs the `CLOUDFLARE_API_TOKEN`
and `CLOUDFLARE_ACCOUNT_ID` secrets — setup in `docs/cloudflare-worker-setup.md`.

On `main` since 2026-09-24 (added by hand, commit b89f21f). To change it, edit
`.github/workflows/deploy-worker.yml` in the web UI, as with `drain.yml`.

```yaml
name: Deploy Worker

# The debrief Worker only changes when it is redeployed. Before this, that needed a
# laptop, and the Worker ran stale code for days after worker/index.js changed.
# Runs on any push to worker/ on main, or by hand: Actions → Deploy Worker → Run workflow.
# Needs two repo secrets: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID
# (docs/cloudflare-worker-setup.md). ANTHROPIC_API_KEY and DEBRIEF_PIN live in
# Cloudflare and survive every deploy.

on:
  push:
    branches: [main]
    paths: ['worker/**']
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: deploy-worker
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: worker
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - name: Install
        run: npm ci

      - name: Deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        run: |
          if [ -z "$CLOUDFLARE_API_TOKEN" ] || [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
            echo "::error::Add the CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID repo secrets — see docs/cloudflare-worker-setup.md"
            exit 1
          fi
          npx --yes wrangler@4 deploy
```

## Re-prescribe Action — not in use

**Not set up.** On 2026-09-24 he chose the twice-daily routine on his Claude plan
(`docs/workflows.md`), which has no API bill. This Action re-prescribes minutes after
a save rather than by 2pm / 10pm, but bills API credits. Kept here in case instant is
ever worth paying for.

Runs after every Drain inbox run. If `log.md` has a session newer than `RX.after`,
Claude Code re-prescribes. It updates the slots that session touched and the whole next
session in `RX` and `plan.md`, adds a note under the log entry, and writes `RX.note` for
the page. `represcribe.py` then checks the edits and commits them. Claude can only read
and edit files, and each run is capped at $3; a normal run costs about $1. If a check
fails, nothing is pushed and the page keeps saying "updating for …".

The model, the spend cap and the prompt live in `represcribe.py` and
`docs/represcribe-prompt.md`, not in this file. They can change without re-pasting it.

One-time setup, all from the phone:

1. **Anthropic API key.** Open `console.anthropic.com/settings/keys` → **Create Key**,
   name it `github-represcribe` → copy it. It is shown once. A separate key from the
   Worker's means you can revoke one without breaking the other.
2. **GitHub secret.** Open `github.com/maxyongg/fitness/settings/secrets/actions` →
   **New repository secret**. Name: `ANTHROPIC_API_KEY`. Value: the key → **Add secret**.
3. **The workflow file.** Repo → Add file → Create new file → name it
   `.github/workflows/represcribe.yml` → paste the YAML below → commit to `main`.
4. **Check it.** Actions → **Re-prescribe** → **Run workflow**. With nothing pending it
   finishes in seconds with a green tick. A red cross naming `ANTHROPIC_API_KEY` means
   step 2 didn't take. The real first run follows your next save.

```yaml
name: Re-prescribe

# After Drain inbox writes a session into log.md, Claude re-prescribes: the slots that
# session touched and the whole next session, in RX (index.html) and plan.md. The logic,
# prompt, model and spend cap live in represcribe.py and docs/represcribe-prompt.md, so
# this file rarely needs to change. Needs the ANTHROPIC_API_KEY repo secret.

on:
  workflow_run:
    workflows: ["Drain inbox"]
    types: [completed]
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: represcribe
  cancel-in-progress: false

jobs:
  represcribe:
    if: github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main

      - name: Anything new since the last re-prescription?
        id: check
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python3 represcribe.py pending >> "$GITHUB_OUTPUT"

      - uses: actions/setup-node@v4
        if: steps.check.outputs.pending == 'true'
        with:
          node-version: 22

      - name: Install Claude Code
        if: steps.check.outputs.pending == 'true'
        run: npm install -g @anthropic-ai/claude-code

      - name: Re-prescribe
        if: steps.check.outputs.pending == 'true'
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python3 represcribe.py run

      - name: Check and commit
        if: steps.check.outputs.pending == 'true'
        run: |
          subject=$(python3 represcribe.py finish)
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add index.html plan.md log.md state.json
          git diff --cached --quiet && exit 0
          git commit -m "$subject"
          # The page and the drain also push to main; rebase onto them and retry.
          for i in 1 2 3 4; do
            git push && exit 0
            sleep $((i * 3))
            git pull --rebase origin main
          done
          exit 1
```
