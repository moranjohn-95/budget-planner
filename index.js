const express = require("express");
const path = require("path");
const { WebSocketServer } = require("ws");
const pty = require("node-pty");

const app = express();
const PORT = process.env.PORT || 8000;

// First, handle root by redirecting to the terminal page.
// This must come BEFORE express.static, otherwise the static middleware
// will serve public/index.html for '/'.
app.get("/", (req, res) => {
  res.redirect("/terminal.html");
});

// Serve static files (our terminal page lives in /public). Disable default
// index serving so it can't shadow the redirect above if order changes.
app.use(express.static(path.join(__dirname, "public"), { index: false }));

const server = app.listen(PORT, () => {
  console.log(`Web terminal on http://localhost:${PORT}`);
});

// WebSocket endpoint for the terminal stream
const wss = new WebSocketServer({ server, path: "/term" });

wss.on("connection", (ws) => {
  // Keep the websocket alive on Heroku by sending ping frames regularly.
  // Heroku routers can drop idle connections (~55s) without traffic.
  ws.isAlive = true;
  ws.on("pong", () => { ws.isAlive = true; });

  // On Heroku (Linux), 'python' resolves to the correct interpreter.
  const shell = "python";
  const p = pty.spawn(shell, ["-u", "run_interactive.py"], {
    name: "xterm-color",
    // Start with a reasonable default, then the client will resize us.
    cols: 80,
    rows: 24,
    cwd: process.cwd(),
    env: { ...process.env, PYTHONUNBUFFERED: "1" }
  });

  p.onData((data) => {
    try { ws.send(data); } catch (_) {}
  });

  ws.on("message", (msg) => {
    // Support structured control messages from the browser
    // (e.g., terminal resize) as well as raw input.
    const text = msg.toString();
    try {
      const data = JSON.parse(text);
      if (data && data.type === "resize") {
        const c = parseInt(data.cols, 10);
        const r = parseInt(data.rows, 10);
        if (Number.isInteger(c) && Number.isInteger(r) && c > 0 && r > 0) {
          try { p.resize(c, r); } catch (_) {}
        }
        return;
      }
      // Fallthrough: not a control message
    } catch (_) {
      // Not JSON; treat as raw input
    }
    p.write(text);
  });

  ws.on("close", () => {
    try { p.kill(); } catch (_) {}
    clearInterval(keepalive);
  });

  const keepalive = setInterval(() => {
    if (ws.readyState === ws.OPEN) {
      try { ws.ping(); } catch (_) {}
    }
  }, 30000); // 30s ping
});
