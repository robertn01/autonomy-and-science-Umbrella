import numpy as np


def create_mock_maps(size=20):
    science_map = np.random.uniform(0.0, 1.0, (size, size))
    hazard_map = np.random.uniform(0.0, 1.0, (size, size))

    # Add a dangerous band / obstacle region
    hazard_map[8:12, 6:15] = 0.95

    # Add a high-science zone
    science_map[15:18, 15:18] = 0.95

    return science_map, hazard_map


def create_mock_resources():
    return {
        "energy_state": 0.75,      # 0 to 1
        "comms_state": "OK",       # OK / DEGRADED / LOST
        "compute_margin": 0.8,     # 0 to 1
        "risk_level": 0.2          # 0 to 1
    }
