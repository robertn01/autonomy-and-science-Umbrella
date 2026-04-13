
def get_manual_resource_inputs():
    rover_state = {
        "x": 2,
        "y": 2,
        "battery": 0.78,
        "health": "OK",
        "speed": 0.4
    }

    drone_state = {
        "x": 3,
        "y": 4,
        "battery": 0.64,
        "health": "OK",
        "available": True,
        "in_flight": False
    }

    mission_state = {
        "comms_quality": 0.82,      # 0 to 1
        "compute_load": 0.35,       # 0 to 1
        "wind_level": 0.20,         # 0 to 1
        "distance_to_target": 12.0,
        "hazard_uncertainty": 0.30, # 0 to 1
        "time_elapsed": 18          # arbitrary unit
    }

    return rover_state, drone_state, mission_state
