
class ResourceMissionStateModel:
    def __init__(self):
        pass

    def evaluate(self, rover_state, drone_state, mission_state):
        rover_battery = rover_state["battery"]
        drone_battery = drone_state["battery"]
        comms_quality = mission_state["comms_quality"]
        compute_load = mission_state["compute_load"]
        wind_level = mission_state["wind_level"]
        hazard_uncertainty = mission_state["hazard_uncertainty"]

        energy_state = 0.6 * rover_battery + 0.4 * drone_battery
        compute_margin = max(0.0, 1.0 - compute_load)

        if comms_quality > 0.7:
            comms_state = "OK"
        elif comms_quality > 0.4:
            comms_state = "DEGRADED"
        else:
            comms_state = "LOST"

        drone_available = (
            drone_state["available"]
            and drone_state["health"] == "OK"
            and drone_battery > 0.25
            and wind_level < 0.75
        )

        risk_level = (
            0.30 * (1.0 - energy_state)
            + 0.25 * (1.0 - comms_quality)
            + 0.20 * compute_load
            + 0.15 * wind_level
            + 0.10 * hazard_uncertainty
        )
        risk_level = min(max(risk_level, 0.0), 1.0)

        if comms_state == "LOST" or energy_state < 0.25 or wind_level > 0.85:
            recommended_mode = "SAFE"
        elif not drone_available and hazard_uncertainty > 0.5:
            recommended_mode = "CAUTION"
        elif drone_available and hazard_uncertainty > 0.55:
            recommended_mode = "SCOUT_READY"
        else:
            recommended_mode = "NORMAL"

        resource_state = {
            "energy_state": round(energy_state, 3),
            "comms_state": comms_state,
            "compute_margin": round(compute_margin, 3),
            "risk_level": round(risk_level, 3),
            "wind_state": round(wind_level, 3),
            "drone_available": drone_available,
            "rover_health": rover_state["health"],
            "drone_health": drone_state["health"],
            "recommended_mode": recommended_mode
        }

        return resource_state
