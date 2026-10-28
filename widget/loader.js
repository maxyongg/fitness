// Paste this into a new Scriptable script named "Matchday". It fetches widget/matchday.js
// from the repo each run, so the widget updates without re-pasting; offline it uses the
// last copy it saved.
const fm = FileManager.local();
const path = fm.joinPath(fm.documentsDirectory(), "matchday-widget.js");
try {
  const r = new Request("https://raw.githubusercontent.com/maxyongg/fitness/main/widget/matchday.js?t=" + Date.now());
  const code = await r.loadString();
  if (r.response.statusCode === 200) fm.writeString(path, code);
} catch (e) {}
await importModule(path).run();
