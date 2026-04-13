
# Resource / Mission-State Model

This model estimates the current operational state of the mission using rover, drone, and mission-level inputs.

## Inputs
- Rover state
- Drone state
- Mission state

## Outputs
- energy_state
- comms_state
- compute_margin
- risk_level
- wind_state
- drone_available
- rover_health
- drone_health
- recommended_mode

## Purpose
This model provides the system with a compact summary of mission constraints, so that the Decision Manager can make better choices under current conditions.
