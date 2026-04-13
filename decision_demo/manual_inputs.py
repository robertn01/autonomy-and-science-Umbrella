def get_manual_inputs():
    science_candidates = [
        {"id": 2, "x": 14, "y": 16, "science_score": 0.61, "confidence": 0.82, "mineral_type": "clay"},
        {"id": 1, "x": 6, "y": 9,  "science_score": 0.78, "confidence": 0.50, "mineral_type": "basalt"},
        {"id": 4, "x": 8, "y": 5, "science_score": 0.8, "confidence": 0.95, "mineral_type": "aluminium"},
        {"id": 3, "x": 17, "y": 4, "science_score": 0.69, "confidence": 0.75, "mineral_type": "sulfate"}
    ]

    resource_state = {
        "energy_state": 0.82,
        "comms_state": "OK",       # OK / DEGRADED / LOST
        "compute_margin": 0.58,
        "risk_level": 0.93,
        "wind_state": 0.20
    }

    hazard_overrides = {
        1: {"hazard_score": 0.5, "distance_cost": 0.90},
        2: {"hazard_score": 0.65, "distance_cost": 0.55},
        4: {"hazard_score": 0.68, "distance_cost": 0.70},
        3: {"hazard_score": 0.77, "distance_cost": 0.76}
    }

    rover_position = (4, 3)

    return science_candidates, resource_state, hazard_overrides, rover_position
