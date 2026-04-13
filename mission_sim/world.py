import random


def generate_random_hazards(map_size, num_hazards=18, seed=42):
    random.seed(seed)
    map_w, map_h = map_size
    hazards = {}

    for _ in range(num_hazards):
        x = random.randint(1, map_w - 2)
        y = random.randint(1, map_h - 2)
        hazard_level = round(random.uniform(0.4, 0.95), 2)
        hazards[(x, y)] = hazard_level

    return hazards


def initialize_world():
    map_size = (20, 20)

    return {
        "map_size": map_size,
        "hazards": generate_random_hazards(map_size, num_hazards=18, seed=42),
        "rover": {
            "position": (2, 2),
            "battery": 0.78,
            "health": "OK",
            "speed": 1
        },
        "drone": {
            "position": (3, 3),
            "battery": 0.64,
            "health": "OK",
            "available": True,
            "in_flight": False
        },
        "mission": {
            "comms_quality": 0.82,
            "compute_load": 0.35,
            "wind_level": 0.20,
            "distance_to_target": 12.0,
            "hazard_uncertainty": 0.30,
            "time_elapsed": 0
        }
    }


def update_mission_state(world, selected_target):
    rover_pos = world["rover"]["position"]
    tx, ty = selected_target
    rx, ry = rover_pos

    distance = ((tx - rx) ** 2 + (ty - ry) ** 2) ** 0.5

    world["mission"]["distance_to_target"] = round(distance, 2)
    world["mission"]["time_elapsed"] += 1

    world["rover"]["battery"] = max(0.0, world["rover"]["battery"] - 0.01)
    if world["drone"]["in_flight"]:
        world["drone"]["battery"] = max(0.0, world["drone"]["battery"] - 0.02)

    # uncertainty rises if rover gets closer to hazards
    rover_x, rover_y = rover_pos
    close_hazard = False
    for (hx, hy), hval in world["hazards"].items():
        if abs(hx - rover_x) <= 2 and abs(hy - rover_y) <= 2 and hval > 0.6:
            close_hazard = True
            break

    world["mission"]["hazard_uncertainty"] = 0.60 if close_hazard else 0.30

    return world
