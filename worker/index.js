import Anthropic from "@anthropic-ai/sdk";

const MODEL = "claude-sonnet-5";
const HISTORY_CHARS = 40000;
const DAY = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export default {
  async fetch(request, env) {
    const allowed = env.ALLOWED_ORIGIN || "https://maxyongg.github.io";
    const cors = {
      "Access-Control-Allow-Origin": allowed,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405, headers: cors });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return Response.json({ error: "Bad request body" }, { status: 400, headers: cors });
    }

    const { session, rx, history, pin } = body;
    if (!env.DEBRIEF_PIN || pin !== env.DEBRIEF_PIN) {
      return Response.json({ error: "Invalid PIN" }, { status: 403, headers: cors });
    }
    if (!session || !Array.isArray(session.exercises) || session.exercises.length === 0) {
      return Response.json({ error: "No session data" }, { status: 400, headers: cors });
    }

    try {
      const debrief = await getDebrief(session, rx, history, env);
      return Response.json({ debrief }, { headers: cors });
    } catch (e) {
      return Response.json({ error: describeError(e) }, { status: 502, headers: cors });
    }
  },
};

/* ---------- the prompt ----------

   The system prompt is the standing brief: who he is, how the programme works, how
   to read the log without repeating the mistakes in docs/incidents.md, and the shape
   of the reply. The user message carries this session, its prescription, the next
   session's prescription and the last eight weeks of log.md.                        */

const SYSTEM = `You debrief a gym session for Max straight after he logs it. He reads it on his phone.

How the programme works:
- Weekly template: Mon Upper A, Tue football (2h of 7-a-side), Wed rest, Thu Upper B, Fri football, Sat Upper C, Sun Lower. Legs once a week is deliberate. He dislikes leg training, so never push for more.
- The goal is holistic fitness at his own pace, shifting towards more calisthenics. There is no target, no date and no peaking. Rounding beats peaking: notice what is missing before what could be heavier. Never push volume he did not ask for, never chase a number on his behalf, and never nag about a missed session.
- Anchor slots keep the same exercise and carry progressive overload. Rotate slots change when the data says so.
- Right lat injury since June 2026, under a physio whose guidance overrides everything here. He rates right-lat pain 0-10 during sets: 0-3 is a green light, 4 or more is amber. Row protocol: the left and right iso-lateral rows are separate lifts. The left progresses normally. The right is governed by pain: three green lights held over two weeks earns +2.5kg, and any red goes back to the last green load. Never hold the left back to match the right.
- No shoulder press (his personal trainer's call). No flat barbell bench (dropped to prioritise incline).
- Progression rules: incline bench +2.5kg once all four sets hit 8. Lateral raise +1kg once 20 holds on all three sets. Pull-ups re-add 5kg once 27 total holds for three sessions. Squat +2.5kg once 10 holds on all sets with no joint complaints. Everything else: the top of the rep range on all sets for two consecutive sessions earns the smallest increment.
- Session order matters. Pull-ups done second in a session have given about ten more reps than pull-ups done fifth.

How to read the data:
- Compare loads only between entries with exactly the same exercise name. A different name is a different machine or movement, and its numbers are not on the same scale.
- A lower load after a form change or a swap is not a decline. If a drop has no explanation in the data, say it is worth a word with him, not that he regressed.
- The log records what he lifted, never why he stopped. He also does finishers and core work he does not always log, so something missing from the log is not necessarily missing from his training.
- The prescription's "last time" and "why" lines were written by his coach and are reliable context.
- If the history does not cover something, say you cannot tell rather than guessing.

What to write:
- Plain text with no markdown, bullets or headings. Three to five short paragraphs separated by blank lines, about 180-300 words in total.
- Start each paragraph with one of these labels and a colon: "Today:", "Trend:", "Right lat:", "Next session:", "Rounding:". Always include Today and Next session. Include the others only when there is something real to say.
- Today: how the session went against the prescription. Name the slots that hit, missed or beat their targets, with the numbers.
- Trend: what moved or stalled against earlier sessions of the same exercise, citing dates and numbers. Call out any progression rule that has just been met, and anything stalled for three or more sessions.
- Right lat: the pain reading and what it means for the row protocol. If a session with pulling has no reading, say so once, plainly.
- Next session: name it and give one or two concrete things to carry into it: a load, a rep target or an order.
- Rounding: something the week is missing, only when the data clearly shows it.
- Direct tone. He is not a beginner, so do not explain basics. No greetings, no sign-offs, no praise for its own sake.`;

async function getDebrief(session, rx, history, env) {
  const client = new Anthropic({
    apiKey: env.ANTHROPIC_API_KEY,
    // Only for local testing against a mock; unset in production.
    ...(env.ANTHROPIC_BASE_URL ? { baseURL: env.ANTHROPIC_BASE_URL } : {}),
  });

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 16000,
    system: SYSTEM,
    messages: [{ role: "user", content: buildMessage(session, rx, history) }],
  });

  if (response.stop_reason === "refusal") {
    throw new Error("Claude declined to write this debrief");
  }
  const text = response.content
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();
  if (!text) throw new Error("Empty debrief (stop reason: " + response.stop_reason + ")");
  return text;
}

function describeError(e) {
  if (e instanceof Anthropic.AuthenticationError) return "Anthropic API key rejected — check the ANTHROPIC_API_KEY secret";
  if (e instanceof Anthropic.NotFoundError) return "Model " + MODEL + " not available on this API key";
  if (e instanceof Anthropic.RateLimitError) return "Rate limited by the Anthropic API — try again in a minute";
  if (e instanceof Anthropic.APIConnectionError) return "Could not reach the Anthropic API";
  if (e instanceof Anthropic.APIError) return "Anthropic API error " + (e.status || "") + ": " + e.message;
  return e && e.message ? e.message : "Internal error";
}

/* ---------- the user message ---------- */

function buildMessage(session, rx, history) {
  const parts = [];
  parts.push("SESSION JUST LOGGED\n" + formatSession(session));

  const cur = rx && rx.sessions && rx.sessions[session.session_id];
  if (cur) {
    parts.push("PRESCRIPTION FOR THIS SESSION (as of " + (rx.asof || "?") + ")\n" + formatRx(cur, true));
  } else {
    parts.push("PRESCRIPTION FOR THIS SESSION\nNot matched to a programme session (imported). Judge it against the history.");
  }

  const next = nextSession(session.date, rx);
  if (next) {
    parts.push("NEXT SESSION: " + next.rx.name + ", " + next.label + "\n" + formatRx(next.rx, false));
  }

  let hist = typeof history === "string" ? history.trim() : "";
  if (hist.length > HISTORY_CHARS) hist = hist.slice(hist.length - HISTORY_CHARS);
  parts.push(
    "RECENT HISTORY (from log.md, oldest first, this session excluded)\n" +
      (hist || "Not available — judge the session against the prescription only, and say the history was missing.")
  );

  return parts.join("\n\n");
}

function formatSession(s) {
  const lines = [s.date + " · " + (s.session || "Session")];
  const pain = s.pain && s.pain.right_lat;
  lines.push(pain != null ? "Right-lat pain: " + pain + "/10" : "Right-lat pain: not recorded");
  if (s.notes && s.notes !== "Imported from Strong") lines.push("Note: " + s.notes);

  let lastGroup = 0;
  for (const ex of s.exercises) {
    const ss = ex.supersetGroup && ex.supersetGroup !== lastGroup ? " [superset]" : "";
    lastGroup = ex.supersetGroup || 0;
    lines.push("- " + ex.name + ss + " — " + formatSets(ex) + (ex.notes ? " (" + ex.notes + ")" : ""));
  }
  if (s.extra) lines.push("Extra (unprescribed work): " + s.extra);
  return lines.join("\n");
}

/* Mirrors drain.py: per-set weights grouped, timed holds as m:ss, bodyweight labelled. */
function formatSets(ex) {
  const sets = (ex.sets || []).filter((st) => st.reps > 0 || st.duration > 0);
  if (sets.some((st) => st.duration > 0)) {
    return sets.map((st) => (st.duration > 0 ? mmss(st.duration) : String(st.reps))).join(", ");
  }
  if (ex.weightL != null || ex.weightR != null) {
    const reps = sets.map((st) => st.reps).join(", ");
    return "L " + ex.weightL + "kg × " + reps + ", R " + ex.weightR + "kg × " + reps;
  }
  if (sets.some((st) => st.weight > 0)) {
    const groups = [];
    for (const st of sets) {
      const g = groups[groups.length - 1];
      if (g && g.w === st.weight) g.reps.push(st.reps);
      else groups.push({ w: st.weight, reps: [st.reps] });
    }
    return groups.map((g) => (g.w > 0 ? g.w + "kg" : "bodyweight") + " × " + g.reps.join(", ")).join(", ");
  }
  const reps = sets.map((st) => st.reps).join(", ");
  if (ex.bodyweight || !(ex.weight > 0)) return "bodyweight × " + reps;
  return ex.weight + "kg × " + reps;
}

function mmss(secs) {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return m + ":" + String(s).padStart(2, "0");
}

function formatRx(s, full) {
  const lines = [];
  if (s.brief) lines.push(s.brief);
  s.exercises.forEach((ex, i) => {
    let load;
    if (ex.bilateral) load = "L " + ex.loadL + "kg / R " + ex.loadR + "kg";
    else if (ex.unit === "BW") load = "bodyweight";
    else load = ex.load > 0 ? ex.load + "kg" : "load to be set";
    lines.push(
      i + 1 + ". " + ex.name + " [" + (ex.type === "anchor" ? "anchor" : "rotate" + (ex.slot ? ", " + ex.slot : "")) + "] " +
        ex.sets + "×" + ex.reps + " @ " + load
    );
    if (ex.do) lines.push("   Instruction: " + ex.do);
    if (full && ex.last) lines.push("   Last time: " + ex.last);
    if (full && ex.why) lines.push("   Why: " + ex.why);
  });
  return lines.join("\n");
}

/* The first lifting day after the session's date, per the page's weekly schedule. */
function nextSession(dateStr, rx) {
  if (!rx || !rx.sessions || !rx.schedule || !/^\d{4}-\d{2}-\d{2}$/.test(dateStr || "")) return null;
  const [y, m, d] = dateStr.split("-").map(Number);
  for (let i = 1; i <= 7; i++) {
    const dt = new Date(Date.UTC(y, m - 1, d + i));
    const id = rx.schedule[dt.getUTCDay()];
    if (id && rx.sessions[id]) {
      return { rx: rx.sessions[id], label: DAY[dt.getUTCDay()] + " " + dt.getUTCDate() + " " + MON[dt.getUTCMonth()] };
    }
  }
  return null;
}
