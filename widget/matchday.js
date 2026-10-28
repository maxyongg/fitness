// Matchday widget for Scriptable (iOS). The loader in widget/loader.js downloads this
// file from main on every refresh, so changes here reach the phone without re-pasting.
// It reads RX from index.html and last_session from state.json — no copy of the
// prescriptions lives here, so re-prescribing needs no extra step.
// Football comes from RX.football. On a match day it leads the small and lock-screen
// widgets until the final whistle; medium and large show the next match as a footer.
// Sizes: small, medium, large home-screen; rectangular and inline lock-screen.

const RAW = "https://raw.githubusercontent.com/maxyongg/fitness/main/";
const PAGE = "https://maxyongg.github.io/fitness/";
const ORDER = ["upper_a", "upper_b", "upper_c", "lower"];
const DAY = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// The page's palette (index.html :root), light then dark.
const C = {
  ground: Color.dynamic(new Color("#eef0ea"), new Color("#0b100f")),
  ink: Color.dynamic(new Color("#111816"), new Color("#eef2ec")),
  ink2: Color.dynamic(new Color("#47534e"), new Color("#aab5af")),
  ink3: Color.dynamic(new Color("#7a8580"), new Color("#6f7c76")),
  accent: Color.dynamic(new Color("#3b7a17"), new Color("#b4f05a")),
  amber: Color.dynamic(new Color("#b06f06"), new Color("#f2b33d")),
};

async function fetchText(path) {
  const r = new Request(RAW + path + "?t=" + Date.now());
  r.timeoutInterval = 15;
  return await r.loadString();
}

// The RX literal, cut out by brace-matching (strings are double-quoted, per index.html).
function parseRX(html) {
  const start = html.indexOf("{", html.search(/var RX\s*=\s*\{/));
  let depth = 0, inStr = false;
  for (let i = start; i < html.length; i++) {
    const ch = html[i];
    if (inStr) {
      if (ch === "\\") i++;
      else if (ch === '"') inStr = false;
    } else if (ch === '"') inStr = true;
    else if (ch === "{") depth++;
    else if (ch === "}" && --depth === 0) {
      return new Function("return (" + html.slice(start, i + 1) + ")")();
    }
  }
  throw new Error("RX not found in index.html");
}

async function load() {
  const fm = FileManager.local();
  const cache = fm.joinPath(fm.documentsDirectory(), "matchday-cache.json");
  try {
    const [html, state] = await Promise.all([fetchText("index.html"), fetchText("state.json")]);
    const data = { rx: parseRX(html), state: JSON.parse(state) };
    fm.writeString(cache, JSON.stringify(data));
    return data;
  } catch (e) {
    if (fm.fileExists(cache)) return Object.assign(JSON.parse(fm.readString(cache)), { stale: true });
    throw e;
  }
}

function iso(d) {
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

// Today's lift if it's a lift day and nothing is logged today; otherwise the next lift day
// on the template. The page also checks the week's saves on the phone; the widget can't
// see those, so a week moved around shows the template, not what's owed.
function pickNext(rx, state, now) {
  const today = iso(now);
  const last = [state.last_session && state.last_session.date, (rx.after || "").slice(0, 10)].sort().pop() || "";
  for (let i = 0; i < 8; i++) {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i);
    const sid = rx.schedule[d.getDay()];
    if (!rx.sessions[sid]) continue;
    if (i === 0 && last >= today) continue;
    return { sid, when: i === 0 ? "Today" : i === 1 ? "Tomorrow" : DAY[d.getDay()] };
  }
  return { sid: ORDER[0], when: "" };
}

// The next match still to play: tonight's until it ends, then the next football day.
function nextFootball(rx, now) {
  const fb = rx.football || {};
  for (let i = 0; i < 8; i++) {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i);
    const m = fb[d.getDay()];
    if (!m) continue;
    const [eh, em] = m.end.split(":").map(Number);
    if (i === 0 && now >= new Date(d.getFullYear(), d.getMonth(), d.getDate(), eh, em)) continue;
    return Object.assign({ when: i === 0 ? "Tonight" : i === 1 ? "Tomorrow" : DAY[d.getDay()], today: i === 0 }, m);
  }
  return null;
}

// "20:00"–"22:00" → "8–10pm", as on the page.
function timeRange(m) {
  const h = t => { const [n, mm] = t.split(":"); return (+n % 12 || 12) + (mm === "00" ? "" : ":" + mm); };
  const ap = t => +t.split(":")[0] >= 12 ? "pm" : "am";
  return h(m.start) + (ap(m.start) === ap(m.end) ? "" : ap(m.start)) + "–" + h(m.end) + ap(m.end);
}

function footballLine(stack, fb, size) {
  const row = stack.addStack();
  row.centerAlignContent();
  const icon = row.addImage(SFSymbol.named("soccerball").image);
  icon.imageSize = new Size(size, size);
  icon.tintColor = C.amber;
  row.addSpacer(5);
  text(row, fb.when + " " + timeRange(fb) + " · " + fb.format + " · " + fb.venue, Font.mediumSystemFont(size - 1), C.ink2);
}

// Same rendering as the page's load column.
function loadStr(ex) {
  if (ex.bilateral) return "L" + ex.loadL + " R" + ex.loadR;
  if (ex.unit === "BW") return "BW";
  return ex.load + ex.unit;
}

function short(name) {
  return name.replace(/\s*\((Barbell|Dumbbell|Machine|Cable)\)/, "");
}

// Re-prescription is behind when the newest logged session isn't the one RX.after names.
function pending(rx, state) {
  const ls = state.last_session;
  if (!ls || !ls.date) return false;
  return (ls.date + " " + ls.name) !== rx.after && ls.date >= (rx.after || "").slice(0, 10);
}

function text(stack, s, font, color, lines) {
  const t = stack.addText(s);
  t.font = font;
  t.textColor = color;
  t.lineLimit = lines || 1;
  t.minimumScaleFactor = 0.75;
  return t;
}

function exRow(w, ex, nameSize) {
  const row = w.addStack();
  row.centerAlignContent();
  text(row, short(ex.name), Font.mediumSystemFont(nameSize), C.ink);
  row.addSpacer();
  row.addSpacer(6);
  text(row, loadStr(ex) + "  " + ex.sets + "×" + ex.reps, Font.semiboldMonospacedSystemFont(nameSize - 1), C.accent);
}

function build(data, family) {
  const { rx, state } = data;
  const next = pickNext(rx, state, new Date());
  const s = rx.sessions[next.sid];
  const w = new ListWidget();
  w.url = PAGE;
  w.refreshAfterDate = new Date(Date.now() + 30 * 60 * 1000);
  const behind = pending(rx, state);
  const fb = nextFootball(rx, new Date());
  const matchDay = fb && fb.today;

  if (matchDay && family === "accessoryInline") {
    w.addText("Football " + timeRange(fb) + " · " + fb.venue);
    return w;
  }
  if (matchDay && family === "accessoryRectangular") {
    text(w, "FOOTBALL · TONIGHT", Font.boldSystemFont(13), Color.white());
    text(w, timeRange(fb) + " · " + fb.format, Font.systemFont(12), Color.white());
    text(w, fb.venue, Font.systemFont(12), Color.white());
    return w;
  }
  if (family === "accessoryInline") {
    w.addText(s.name + " " + next.when + " · " + short(s.exercises[0].name) + " " + loadStr(s.exercises[0]));
    return w;
  }
  if (family === "accessoryRectangular") {
    text(w, s.name.toUpperCase() + " · " + next.when.toUpperCase(), Font.boldSystemFont(13), Color.white());
    for (const ex of s.exercises.slice(0, 2)) {
      text(w, short(ex.name) + " " + loadStr(ex), Font.systemFont(12), Color.white());
    }
    return w;
  }

  w.backgroundColor = C.ground;
  const pad = family === "small" ? 14 : 16;
  w.setPadding(pad, pad, pad, pad);

  if (matchDay && family === "small") {
    const head = w.addStack();
    text(head, "TONIGHT", Font.semiboldMonospacedSystemFont(10), C.amber);
    head.addSpacer();
    text(head, timeRange(fb).toUpperCase(), Font.semiboldMonospacedSystemFont(10), C.ink3);
    w.addSpacer(2);
    text(w, "FOOTBALL", Font.heavySystemFont(24), C.ink);
    w.addSpacer(4);
    text(w, fb.format, Font.semiboldMonospacedSystemFont(12), C.amber);
    text(w, fb.venue, Font.mediumSystemFont(12), C.ink2, 2);
    w.addSpacer();
    text(w, "Next: " + s.name + " " + next.when, Font.systemFont(11), C.ink3);
    return w;
  }

  const head = w.addStack();
  head.centerAlignContent();
  text(head, next.when.toUpperCase(), Font.semiboldMonospacedSystemFont(10), C.accent);
  head.addSpacer();
  text(head, behind ? "UPDATES 10PM" : (data.stale ? "OFFLINE" : s.mins.replace("~", "").toUpperCase()),
    Font.semiboldMonospacedSystemFont(10), behind || data.stale ? C.amber : C.ink3);
  w.addSpacer(2);
  text(w, s.name.toUpperCase(), Font.heavySystemFont(family === "small" ? 24 : 26), C.ink);
  w.addSpacer(family === "small" ? 6 : 8);

  if (family === "small") {
    for (const ex of s.exercises.slice(0, 2)) {
      text(w, short(ex.name), Font.mediumSystemFont(12), C.ink2);
      text(w, loadStr(ex) + "  " + ex.sets + "×" + ex.reps, Font.semiboldMonospacedSystemFont(12), C.accent);
      w.addSpacer(3);
    }
  } else {
    const n = family === "medium" ? 3 : s.exercises.length;
    for (const ex of s.exercises.slice(0, n)) {
      exRow(w, ex, 13);
      w.addSpacer(family === "medium" ? 3 : 5);
    }
    if (fb) {
      w.addSpacer(family === "medium" ? 1 : 4);
      footballLine(w, fb, 12);
    }
    if (family === "large" && rx.note) {
      w.addSpacer(6);
      text(w, rx.note, Font.systemFont(11), C.ink2, 5);
    }
  }
  w.addSpacer();
  return w;
}

function errorWidget(e) {
  const w = new ListWidget();
  w.backgroundColor = C.ground;
  w.url = PAGE;
  text(w, "MATCHDAY", Font.semiboldMonospacedSystemFont(10), C.amber);
  text(w, String(e.message || e), Font.systemFont(11), C.ink2, 4);
  return w;
}

module.exports.run = async function () {
  const family = config.widgetFamily || "large";
  let w;
  try {
    w = build(await load(), family);
  } catch (e) {
    w = errorWidget(e);
  }
  if (config.runsInWidget || config.runsInAccessoryWidget) Script.setWidget(w);
  else if (family === "small") await w.presentSmall();
  else if (family === "medium") await w.presentMedium();
  else await w.presentLarge();
  Script.complete();
};
