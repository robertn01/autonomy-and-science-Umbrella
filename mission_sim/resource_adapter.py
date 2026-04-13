from ai_models.resource_mission_state.model import ResourceMissionStateModel


def get_resource_state(rover_state, drone_state, mission_state):
    model = ResourceMissionStateModel()
    return model.evaluate(rover_state, drone_state, mission_state)
