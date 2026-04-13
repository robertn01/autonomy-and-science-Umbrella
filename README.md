# Autonomy and Science Umbrella

This repository combines:
- **Geophone Seismic Dashboard**: A real-time web dashboard for seismic sensing (`geophone_app.py`) built with Flask and Socket.IO.
- **Autonomy & AI Models**: Complete autonomy system, mission simulation, and AI models from the umbrella-autonomy project.

## Structure

- `geophone_app.py` - Flask web dashboard for real-time seismic monitoring with WAV recording.
- `decision_demo/` - Decision-making demo and execution logic.
- `mission_sim/` - Mission simulation framework with world simulation and hazard adaptation.
- `ai_models/` - AI model code:
  - `hazard_traversability/` - Model for terrain/hazard assessment.
  - `resource_mission_state/` - Model for mission state estimation.
- `requirements.txt` - Python dependencies.
- `.devcontainer/` - Development container configuration.

## Setup

```bash
cd ~/autonomy-and-science-umbrella
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `sounddevice` cannot access hardware, the app falls back to demo mode.

## Run

```bash
python geophone_app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Notes

- `geophone_app.py` and the autonomy modules run independently. The dashboard is a standalone Flask app; decision-making, mission simulation, and AI models are available as separate modules.
- Customize decision logic in `decision_demo/decision_manager.py`.
- Add or modify missions in `mission_sim/`.
- Train or improve AI models in `ai_models/`.
