# Cloudflare Worker setup — instant debriefs

After you save a session on the phone page — from Train or from Import — the browser
calls a Cloudflare Worker that sends the session to Claude (Sonnet 5) and puts a short
debrief on screen. No repo writes — just a card under the save button.

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
npm install
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
2. **Immediately:** the page reads `log.md` through the GitHub API (same token), keeps
   the last 8 weeks, and sends it to the Worker with the session, the `RX` prescriptions
   and your PIN. The Worker calls Claude and the debrief lands on screen, usually within
   10-30 seconds.
3. **Within ~1 minute:** GitHub Action runs `drain.py` + `prescribe.py`, commits
   log + state + updated RX.asof, deletes inbox file

The debrief is display-only — it doesn't write to the repo, and it is gone once
dismissed. The GH Action handles all the repo bookkeeping.

## What the debrief sees

- **The session just logged** — every set, weights, holds, supersets, pain, notes, extra.
- **Its prescription** — each slot's load and rep target plus the `do`, `last` and `why`
  lines from `RX`, so the coach's context travels with it.
- **The next session's prescription**, worked out from `RX.schedule`.
- **The last 8 weeks of `log.md`**, with the HTML commentary stripped.

The standing brief (programme rules, row protocol, how to read the log) is the `SYSTEM`
prompt in `worker/index.js`. The reply is 3-5 labelled paragraphs — Today, Trend,
Right lat, Next session, Rounding — about 180-300 words. If the page can't read
`log.md`, the debrief still runs and says the history was missing.

## Replies and follow-ups

Under every debrief there's a reply box. When the log can't explain something (a set
that dropped, a swapped slot) the debrief ends with one **Question:**, and he can
answer it, or ask anything about the session. The page keeps the conversation and sends
it back to the Worker as `thread`; the Worker is stateless and rebuilds the same context
each time, so the prompt cache serves it on follow-ups (about a tenth of the input cost).
Capped at 25 turns and 2,000 characters a message.

The debrief coach can't change the programme. If he asks for a change it gives a view
and points him at his next planning session.

## Where debriefs are kept

Each debrief is saved to `debriefs/<date>-<session>.json` in the repo with the session
it was about and the whole conversation, updated after every reply. The phone keeps a
copy for the **History → Debriefs** tab, and pulls any it's missing from the repo when
that tab opens. Planning sessions read these files (see `CLAUDE.md`).

The drain Action and these commits both write to `main`, so the Action queues its runs
and rebases before pushing.

## Redeploying

When the Worker code in `worker/index.js` changes, redeploy from a terminal:

```bash
cd fitness/worker
npm install
npx wrangler deploy
```

Secrets persist across deploys — you only set them once. `npm install` pulls the
Anthropic SDK the Worker is built on; wrangler bundles it into the deploy.

## Costs

- **Cloudflare Workers:** free tier covers 100k requests/day. One debrief = one request.
- **Anthropic API:** roughly 3-5 cents per debrief (Claude Sonnet 5 at $2/$10 per million
  tokens: a few thousand tokens of session + history in, the reply and its thinking out).
  At 4-5 sessions a week that's about $1/month.
