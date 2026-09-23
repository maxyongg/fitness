# Cloudflare Worker setup — instant debriefs

After you save a session on the phone page, the browser calls a Cloudflare Worker
that sends the session data to Claude and returns a 2-4 sentence debrief within
seconds. No repo writes, no waiting — just a card on screen.

Requests are gated by a PIN: the Worker rejects any call without a valid PIN,
so random visitors can't burn your API credits.

## One-time setup (~5 min)

### 1. Create a Cloudflare account

Sign up at https://dash.cloudflare.com if you don't have one. The free tier
covers this easily (~100k requests/day). You'll need to register a `workers.dev`
subdomain — find it under **Workers & Pages** in the sidebar.

### 2. Deploy the Worker

From a terminal (not Claude Code — it needs interactive input for secrets):

```bash
cd fitness/worker
npx wrangler login
npx wrangler deploy
```

Wrangler prints the Worker URL: `https://matchday-debrief.<your-subdomain>.workers.dev`

### 3. Set the secrets

Either via the Cloudflare dashboard (Worker → Settings → Variables and Secrets)
or via the terminal:

```bash
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler secret put DEBRIEF_PIN
```

- **ANTHROPIC_API_KEY** — get one at https://console.anthropic.com/settings/keys
- **DEBRIEF_PIN** — any string you choose (e.g. `1234`, a word). You'll enter the
  same PIN on the phone page.

### 4. Enter the PIN on the phone page

Open https://maxyongg.github.io/fitness/ → tap the gear icon → enter your PIN
in the "Debrief PIN" field → Save.

The Worker URL is already hardcoded in the page (`RX.workerUrl`). The PIN is
stored in your browser's `localStorage` — it never appears in the repo.

## What happens after setup

1. You save a session on the phone page → JSON goes to `inbox/`
2. **Immediately:** the page calls the Worker with your PIN, which calls
   Claude Sonnet and returns a debrief card on screen (2-5 seconds)
3. **Within ~1 minute:** GitHub Action runs `drain.py` + `prescribe.py`, commits
   log + state + updated RX.asof, deletes inbox file

The debrief is display-only — it doesn't write to the repo. The GH Action handles
all the repo bookkeeping.

## Redeploying

When the Worker code in `worker/index.js` changes, redeploy from a terminal:

```bash
cd fitness/worker
npx wrangler deploy
```

Secrets persist across deploys — you only set them once.

## Costs

- **Cloudflare Workers:** free tier covers 100k requests/day. One debrief = one request.
- **Anthropic API:** ~$0.005-0.01 per debrief (Sonnet, short prompt + 300 token reply).
  At 4 sessions/week that's ~$2/month.
