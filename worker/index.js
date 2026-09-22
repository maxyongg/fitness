export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
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

    try {
      const { session, rx } = await request.json();
      if (!session || !session.exercises || session.exercises.length === 0) {
        return Response.json({ error: "No session data" }, { status: 400, headers: cors });
      }

      const debrief = await getDebrief(session, rx, env.ANTHROPIC_API_KEY);
      return Response.json({ debrief }, { headers: cors });
    } catch (e) {
      return Response.json(
        { error: e.message || "Internal error" },
        { status: 500, headers: cors }
      );
    }
  },
};

async function getDebrief(session, rx, apiKey) {
  const sessionSummary = formatSession(session);
  const rxSummary = rx ? formatRx(rx, session.session_id) : "";

  const system = `You are a concise strength coach reviewing a gym session. The trainee is intermediate, trains 3U/1L per week (Mon Upper A / Thu Upper B / Sat Upper C / Sun Lower) plus Tuesday and Friday football.

Key context:
- Right lat injury since June 2026, under physio. Pain rated each session (0-10). Green: 0-3. Amber: 4+.
- Row protocol: right-side iso-lateral row. Three consecutive green lights earn +2.5kg.
- No shoulder press (PT recommendation). No flat barbell bench (prioritising incline).
- Pull-ups: position in session matters (earlier = more reps). Total and top set are the metrics.
- Anchors keep their exercise always. Rotate slots can change when data says so.

Progression rules:
- Incline bench: +2.5kg once all four sets hit 8 (currently 65kg)
- Lateral raises: +1kg once 20 holds across all three sets (currently 8kg)
- Pull-ups: re-add 5kg vest once 27 total reps holds three sessions
- Everything else: top of rep range on all sets for 2 consecutive sessions → add smallest increment

Give a 2-4 sentence debrief. Flag only what earns it: pain reading if recorded, pull-up position and total on pull day, a lift that moved or stalled 3+ sessions, a progression trigger hit. Nothing notable → one sentence is fine. No greetings, no sign-offs. Direct tone.`;

  const userMsg = `Session:\n${sessionSummary}\n\n${rxSummary}`;

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 300,
      system,
      messages: [{ role: "user", content: userMsg }],
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error("Claude API error: " + res.status);
  }

  const data = await res.json();
  return data.content[0].text;
}

function formatSession(s) {
  const lines = [`${s.date} ${s.session}`];
  const pain = s.pain?.right_lat;
  if (pain != null) lines.push(`Pain (R): ${pain}/10`);
  if (s.notes) lines.push(`Note: ${s.notes}`);

  for (const ex of s.exercises) {
    const sets = ex.sets || [];
    const reps = sets.map((st) => st.reps).filter((r) => r > 0);

    if (ex.weightL != null || ex.weightR != null) {
      lines.push(`- ${ex.name}: L ${ex.weightL}kg x ${reps.join(",")}, R ${ex.weightR}kg x ${reps.join(",")}`);
    } else if (ex.bodyweight) {
      lines.push(`- ${ex.name}: BW x ${reps.join(",")}`);
    } else if (ex.weight > 0) {
      lines.push(`- ${ex.name}: ${ex.weight}kg x ${reps.join(",")}`);
    } else {
      lines.push(`- ${ex.name}: x ${reps.join(",")}`);
    }
  }

  if (s.extra) lines.push(`Extra: ${s.extra}`);
  return lines.join("\n");
}

function formatRx(rx, sessionId) {
  if (!rx.sessions || !sessionId) return "";
  const s = rx.sessions[sessionId];
  if (!s) return "";

  const lines = [`Prescription for ${s.name} (as of ${rx.asof}):`];
  for (const ex of s.exercises) {
    let load = "";
    if (ex.bilateral) load = `L ${ex.loadL}kg / R ${ex.loadR}kg`;
    else if (ex.unit === "BW") load = "BW";
    else if (ex.load > 0) load = `${ex.load}${ex.unit}`;

    lines.push(`- ${ex.name} [${ex.type}]: ${ex.sets}x${ex.reps} @ ${load || "?"}`);
  }
  return lines.join("\n");
}
