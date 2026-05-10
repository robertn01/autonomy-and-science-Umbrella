from __future__ import annotations

import threading
import time

from flask import Flask, render_template_string
from flask_socketio import SocketIO

from mission_sim.two_rover_main import MarsSwarmSimulator


app = Flask(__name__)
app.config["SECRET_KEY"] = "mars-swarm-demo"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

simulator = MarsSwarmSimulator()
sim_lock = threading.Lock()
running = False
background_started = False


HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mars Swarm Dashboard</title>
  <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
  <style>
    :root {
      --bg: #071017;
      --panel: rgba(12, 24, 33, 0.9);
      --panel-2: rgba(10, 18, 25, 0.92);
      --text: #eaf2f7;
      --muted: #86a5b8;
      --accent: #ff9f43;
      --accent-2: #47d7ac;
      --danger: #ff6b6b;
      --line: rgba(151, 193, 214, 0.18);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(255, 159, 67, 0.16), transparent 28%),
        radial-gradient(circle at bottom right, rgba(71, 215, 172, 0.13), transparent 26%),
        linear-gradient(180deg, #081118 0%, #05090d 100%);
    }
    .shell {
      display: grid;
      grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.75fr);
      gap: 18px;
      padding: 18px;
      max-width: 1600px;
      margin: 0 auto;
    }
    .hero {
      grid-column: 1 / -1;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 20px;
      padding: 18px 22px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(19, 31, 41, 0.92), rgba(9, 17, 24, 0.88));
      border-radius: 22px;
      box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
    }
    .title { margin: 0; font-size: 30px; letter-spacing: 0.04em; }
    .subtitle { margin-top: 8px; color: var(--muted); max-width: 900px; line-height: 1.5; }
    .hero-actions { display: flex; gap: 10px; flex-wrap: wrap; }
    button {
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }
    button:hover { transform: translateY(-1px); }
    .primary { background: var(--accent); color: #1a1209; }
    .secondary { background: rgba(255,255,255,0.08); color: var(--text); border: 1px solid var(--line); }
    .danger { background: rgba(255,107,107,0.12); color: #ffdede; border: 1px solid rgba(255,107,107,0.35); }
    .panel {
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 22px;
      padding: 16px;
      box-shadow: 0 16px 46px rgba(0, 0, 0, 0.22);
    }
    .map-wrap { position: relative; min-height: 760px; }
    canvas {
      width: 100%;
      height: 760px;
      display: block;
      background: radial-gradient(circle at 50% 10%, rgba(255,255,255,0.06), transparent 20%), #091018;
      border-radius: 18px;
      border: 1px solid rgba(255,255,255,0.06);
    }
    .status-grid {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .card {
      padding: 14px;
      border-radius: 18px;
      background: var(--panel-2);
      border: 1px solid rgba(255,255,255,0.05);
    }
    .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .value { font-size: 26px; font-weight: 800; margin-top: 6px; }
    .section-title { margin: 0 0 12px; font-size: 16px; letter-spacing: 0.03em; }
    .rover-list, .event-list {
      display: grid;
      gap: 10px;
    }
    .rover-card {
      padding: 12px;
      border-radius: 16px;
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.05);
    }
    .row { display: flex; justify-content: space-between; gap: 10px; align-items: center; }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      background: rgba(255,255,255,0.06);
      color: #dbe9f2;
    }
    .pill.good { background: rgba(71,215,172,0.14); color: #bdfbe4; }
    .pill.warn { background: rgba(255,159,67,0.14); color: #ffe0be; }
    .pill.bad { background: rgba(255,107,107,0.14); color: #ffd1d1; }
    .tiny { color: var(--muted); font-size: 12px; line-height: 1.4; }
    .spaced { display: grid; gap: 14px; }
    .log-item {
      font-size: 13px;
      padding: 10px 12px;
      border-radius: 14px;
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.05);
    }
    @media (max-width: 1120px) {
      .shell { grid-template-columns: 1fr; }
      .map-wrap, canvas { min-height: 620px; height: 620px; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="hero panel">
      <div>
        <h1 class="title">Mars Swarm Dashboard</h1>
        <div class="subtitle">Two rover agents exchange delayed telemetry, negotiate science targets, and coordinate decentralized exploration across a shared Martian map.</div>
      </div>
      <div class="hero-actions">
        <button class="primary" onclick="startSim()">Start</button>
        <button class="secondary" onclick="pauseSim()">Pause</button>
        <button class="danger" onclick="resetSim()">Reset</button>
      </div>
    </header>

    <section class="panel map-wrap">
      <canvas id="map" width="1120" height="760"></canvas>
    </section>

    <aside class="spaced">
      <section class="panel">
        <h2 class="section-title">Mission Summary</h2>
        <div class="status-grid">
          <div class="card"><div class="label">Step</div><div class="value" id="step">0</div></div>
          <div class="card"><div class="label">Explored</div><div class="value" id="explored">0%</div></div>
          <div class="card"><div class="label">Network</div><div class="value" id="network">OK</div></div>
          <div class="card"><div class="label">Targets Sampled</div><div class="value" id="sampled">0</div></div>
        </div>
      </section>

      <section class="panel">
        <h2 class="section-title">Rovers</h2>
        <div class="rover-list" id="rovers"></div>
      </section>

      <section class="panel">
        <h2 class="section-title">Consensus Target</h2>
        <div id="consensus" class="tiny">Waiting for swarm telemetry...</div>
      </section>

      <section class="panel">
        <h2 class="section-title">Recent Events</h2>
        <div class="event-list" id="events"></div>
      </section>
    </aside>
  </div>

  <script>
    const socket = io();
    const canvas = document.getElementById('map');
    const ctx = canvas.getContext('2d');
    let latest = null;

    function startSim() { socket.emit('start_sim'); }
    function pauseSim() { socket.emit('pause_sim'); }
    function resetSim() { socket.emit('reset_sim'); }

    function drawGrid(mapSize, padding, cellW, cellH) {
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.lineWidth = 1;
      for (let x = 0; x <= mapSize[0]; x++) {
        const px = padding + x * cellW;
        ctx.beginPath();
        ctx.moveTo(px, padding);
        ctx.lineTo(px, canvas.height - padding);
        ctx.stroke();
      }
      for (let y = 0; y <= mapSize[1]; y++) {
        const py = padding + y * cellH;
        ctx.beginPath();
        ctx.moveTo(padding, py);
        ctx.lineTo(canvas.width - padding, py);
        ctx.stroke();
      }
    }

    function cellToPx(x, y, padding, cellW, cellH) {
      return [padding + (x + 0.5) * cellW, padding + (y + 0.5) * cellH];
    }

    function drawTarget(target, padding, cellW, cellH) {
      const [cx, cy] = cellToPx(target.x, target.y, padding, cellW, cellH);
      ctx.save();
      ctx.translate(cx, cy);
      ctx.fillStyle = target.sampled ? 'rgba(71,215,172,0.9)' : 'rgba(79, 158, 255, 0.95)';
      ctx.strokeStyle = target.sampled ? '#47d7ac' : '#a8d2ff';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, 0, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(-12, 0); ctx.lineTo(12, 0);
      ctx.moveTo(0, -12); ctx.lineTo(0, 12);
      ctx.stroke();
      ctx.restore();
    }

    function drawRover(rover, index, padding, cellW, cellH) {
      const colors = ['#ff9f43', '#f25f5c'];
      const [cx, cy] = cellToPx(rover.position[0], rover.position[1], padding, cellW, cellH);
      const color = colors[index % colors.length];

      ctx.save();
      ctx.fillStyle = color;
      ctx.strokeStyle = '#061018';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(cx, cy, 12, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = 'rgba(255,255,255,0.45)';
      rover.path.slice(-28).forEach((point, idx) => {
        const alpha = 0.08 + (idx / Math.max(1, rover.path.length - 1)) * 0.28;
        const [px, py] = cellToPx(point[0], point[1], padding, cellW, cellH);
        ctx.fillStyle = `rgba(255,255,255,${alpha})`;
        ctx.fillRect(px - 1.5, py - 1.5, 3, 3);
      });

      if (rover.assigned_target_id !== null && latest) {
        const target = latest.science_targets.find(t => t.id === rover.assigned_target_id);
        if (target) {
          const [tx, ty] = cellToPx(target.x, target.y, padding, cellW, cellH);
          ctx.strokeStyle = color;
          ctx.setLineDash([7, 6]);
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(tx, ty);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }
      ctx.restore();
    }

    function drawTerrain() {
      if (!latest) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const padding = 36;
      const mapSize = latest.map_size;
      const cellW = (canvas.width - padding * 2) / mapSize[0];
      const cellH = (canvas.height - padding * 2) / mapSize[1];

      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      gradient.addColorStop(0, '#0d1821');
      gradient.addColorStop(1, '#091018');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      drawGrid(mapSize, padding, cellW, cellH);

      latest.hazards.forEach(hazard => {
        const [hx, hy] = cellToPx(hazard.x, hazard.y, padding, cellW, cellH);
        const size = 6 + hazard.intensity * 16;
        ctx.fillStyle = `rgba(255, 90, 90, ${0.12 + hazard.intensity * 0.45})`;
        ctx.fillRect(hx - size / 2, hy - size / 2, size, size);
      });

      latest.science_targets.forEach(target => drawTarget(target, padding, cellW, cellH));
      latest.rovers.forEach((rover, index) => drawRover(rover, index, padding, cellW, cellH));

      if (latest.consensus_target) {
        const target = latest.consensus_target;
        const [cx, cy] = cellToPx(target.x, target.y, padding, cellW, cellH);
        ctx.save();
        ctx.strokeStyle = 'rgba(71,215,172,0.95)';
        ctx.setLineDash([4, 4]);
        ctx.lineWidth = 2;
        ctx.strokeRect(cx - 18, cy - 18, 36, 36);
        ctx.restore();
      }
    }

    function roverClass(health) {
      if (health === 'LOW_POWER') return 'bad';
      return 'good';
    }

    function updateSidebar(state) {
      document.getElementById('step').textContent = state.step;
      document.getElementById('explored').textContent = `${Math.round(state.mission.explored_ratio * 100)}%`;
      document.getElementById('sampled').textContent = state.mission.sampled_targets;
      document.getElementById('network').textContent = `Q ${state.network.comms_quality.toFixed(2)} / ${state.network.queued} queued`;

      const rovers = document.getElementById('rovers');
      rovers.innerHTML = '';
      state.rovers.forEach(rover => {
        const div = document.createElement('div');
        div.className = 'rover-card';
        div.innerHTML = `
          <div class="row">
            <strong>${rover.name}</strong>
            <span class="pill ${roverClass(rover.health)}">${rover.role}</span>
          </div>
          <div class="tiny">Pos ${rover.position[0]}, ${rover.position[1]} · Battery ${Math.round(rover.battery * 100)}% · Assigned ${rover.assigned_target_id ?? 'none'}</div>
          <div class="tiny">Proposal ${rover.proposal.target_id ?? 'none'} · Utility ${rover.proposal.utility ?? 'n/a'}</div>
          <div class="tiny">Peer proposal ${rover.peer_snapshot?.proposal?.target_id ?? 'n/a'} · Telemetry link is ${state.network.queued > 0 ? 'lagged' : 'fresh'}</div>
        `;
        rovers.appendChild(div);
      });

      const consensus = document.getElementById('consensus');
      if (state.consensus_target) {
        consensus.innerHTML = `Target ${state.consensus_target.id} at (${state.consensus_target.x}, ${state.consensus_target.y})<br>${state.consensus_target.terrain}<br>Consensus utility ${state.consensus_target.utility}`;
      } else {
        consensus.textContent = 'All science targets sampled or unavailable.';
      }

      const events = document.getElementById('events');
      events.innerHTML = '';
      if (!state.events.length) {
        const empty = document.createElement('div');
        empty.className = 'tiny';
        empty.textContent = 'No samples recorded yet.';
        events.appendChild(empty);
      } else {
        state.events.slice().reverse().forEach(event => {
          const div = document.createElement('div');
          div.className = 'log-item';
          div.textContent = `${event.rover} sampled target ${event.target_id} (${event.terrain})`;
          events.appendChild(div);
        });
      }
    }

    socket.on('swarm_state', state => {
      latest = state;
      drawTerrain();
      updateSidebar(state);
    });

    socket.on('connect', () => {
      socket.emit('request_state');
    });
  </script>
</body>
</html>
"""


def _start_background_loop() -> None:
    global background_started
    if background_started:
        return
    background_started = True

    def loop() -> None:
        global simulator, running
        while True:
            if running:
                with sim_lock:
                    state = simulator.step()
                socketio.emit("swarm_state", state)
                time.sleep(0.35)
            else:
                time.sleep(0.1)

    threading.Thread(target=loop, daemon=True).start()


@app.route("/")
def index() -> str:
    return render_template_string(HTML)


@socketio.on("connect")
def handle_connect() -> None:
    _start_background_loop()
    socketio.emit("swarm_state", simulator.snapshot())


@socketio.on("request_state")
def handle_request_state() -> None:
    socketio.emit("swarm_state", simulator.snapshot())


@socketio.on("start_sim")
def handle_start_sim() -> None:
    global running
    running = True
    socketio.emit("swarm_state", simulator.snapshot())


@socketio.on("pause_sim")
def handle_pause_sim() -> None:
    global running
    running = False
    socketio.emit("swarm_state", simulator.snapshot())


@socketio.on("reset_sim")
def handle_reset_sim() -> None:
    global simulator, running
    with sim_lock:
        simulator = MarsSwarmSimulator()
    running = False
    socketio.emit("swarm_state", simulator.snapshot())


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5050, debug=False, allow_unsafe_werkzeug=True)
