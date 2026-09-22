# Cloudflare Worker setup — instant debriefs

After you save a session on the phone page, the browser calls a Cloudflare Worker
that sends the session data to Claude and returns a 2-4 sentence debrief within
seconds. No repo writes, no waiting — just a card on screen.

## One-time setup (~5 min)

### 1. Create a Cloudflare account

Sign up at https://dash.cloudflare.com if you don't have one. The free tier
covers this easily (~100k requests/day).

### 2. Install Wrangler (Cloudflare CLI)

```bash
npm install -g wrangler
wrangler login
```

### 3. Get an Anthropic API key

Go to https://console.anthropic.com/settings/keys and create a key.
Each debrief costs ~$0.005-0.01 (Sonnet, ~300 tokens out).

### 4. Deploy the Worker

```bash
cd fitness/worker
wrangler secret put ANTHROPIC_API_KEY
# paste your Anthropic key when prompted

wrangler deploy
```

Wrangler prints the Worker URL (e.g. `https://matchday-debrief.<you>.workers.dev`).

### 5. Add the URL to the phone page

Open the page → tap the gear icon → paste the Worker URL into "Debrief Worker URL" → Save.

## What happens after setup

1. You save a session on the phone page → JSON goes to `inbox/`
2. **Immediately:** the page calls the Worker, which calls Claude Sonnet and returns
   a debrief card on screen (2-5 seconds)
3. **Within ~1 minute:** GitHub Action runs `drain.py` + `prescribe.py`, commits
   log + state + updated RX.asof, deletes inbox file

The debrief is display-only — it doesn't write to the repo. The GH Action handles
all the repo bookkeeping.

## Updated drain.yml

The GitHub Action needs one extra step (`prescribe.py`) and `index.html` in the
commit. Since Claude Code can't push workflow files, update `.github/workflows/drain.yml`
yourself — same as last time, via the GitHub web UI or local machine.

Replace the full YAML with:

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
          git push
```

## Costs

- **Cloudflare Workers:** free tier covers 100k requests/day. One debrief = one request.
- **Anthropic API:** ~$0.005-0.01 per debrief (Sonnet, short prompt + 300 token reply).
  At 4 sessions/week that's ~$2/month.
