const express = require("express");
const path = require("path");
const { WebSocketServer } = require("ws");
const pty = require("node-pty");

const app = express();
const PORT = process.env.PORT || 8000;

// Serve static files (our terminal page lives in /public)
app.use(express.static(path.join(__dirname, "public")));
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

const server = app.listen(PORT, () => {
  console.log(`Web terminal on http://localhost:${PORT}`);
});

// WebSocket endpoint for the terminal stream
const wss = new WebSocketServer({ server, path: "/term" });

wss.on("connection", (ws) => {
  // On Heroku (Linux), 'python' resolves to the correct interpreter.
  const shell = "python";
  const p = pty.spawn(shell, ["-u", "run.py"], {
    name: "xterm-color",
    cols: 80,
    rows: 24,
    cwd: process.cwd(),
    env: { ...process.env, PYTHONUNBUFFERED: "1" }
  });

  p.onData((data) => {
    try { ws.send(data); } catch (_) {}
  });

  ws.on("message", (msg) => {
    p.write(msg.toString());
  });

  ws.on("close", () => {
    try { p.kill(); } catch (_) {}
  });
});
