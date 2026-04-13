# Autonomy and Science Umbrella

This repository keeps two pieces in the same folder tree:
- `geophone_app.py`: a real-time seismic monitoring dashboard built with Flask and Socket.IO.
- `umbrella_autonomy/`: a starter package for autonomy, navigation, and decision-making models.

## Structure

- `geophone_app.py` - Flask app and web dashboard for seismic sensing.
- `requirements.txt` - Python dependencies.
- `umbrella_autonomy/` - autonomy/navigation/decision-making helper modules.
- `umbrella_autonomy/models/` - placeholder package for autonomy models.

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

- The current `umbrella_autonomy` package is a separate scaffold and is not wired into `geophone_app.py`.
- Add your autonomy/navigation models under `umbrella_autonomy/models/`.
