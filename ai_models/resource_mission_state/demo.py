
from ai_models.resource_mission_state.manual_inputs import get_manual_resource_inputs
from ai_models.resource_mission_state.model import ResourceMissionStateModel


def run_demo():
    rover_state, drone_state, mission_state = get_manual_resource_inputs()

    model = ResourceMissionStateModel()
    resource_state = model.evaluate(rover_state, drone_state, mission_state)

    print("=== RESOURCE / MISSION STATE MODEL DEMO ===")
    print("Rover state:")
    print(rover_state)
    print("\nDrone state:")
    print(drone_state)
    print("\nMission state:")
    print(mission_state)
    print("\nOutput resource_state:")
    print(resource_state)


if __name__ == "__main__":
    run_demo()
