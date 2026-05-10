
# Mission Simulation

This folder contains the first integrated rover-drone mission simulation.

## Current integration
- Manual science candidate outputs
- Hazard adapter
- Real resource / mission-state model
- Execution model
- 2D visualization

## Mars swarm prototype
- `rover_agent.py` implements the local rover decision logic, telemetry, and target scoring.
- `two_rover_main.py` runs a decentralized two-rover simulation with delayed peer messages and shared science target negotiation.
- `../swarm_dashboard.py` renders a live dashboard for the two simulated rovers.

## Purpose
This simulation is the first step toward demonstrating cooperative rover-drone autonomy in one shared loop.
