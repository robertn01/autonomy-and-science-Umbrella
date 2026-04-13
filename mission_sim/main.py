
from mission_sim.manual_science import get_manual_science_candidates
from mission_sim.hazard_adapter import get_hazard_outputs
from mission_sim.resource_adapter import get_resource_state
from mission_sim.world import initialize_world, update_mission_state
from mission_sim.renderer import render_world

from decision_demo.execution_model import ExecutionModel


def choose_target(science_candidates, hazard_outputs):
    best_candidate = None
    best_utility = -999

    for c in science_candidates:
        cid = c["id"]
        science_score = c["science_score"] * c["confidence"]
        hazard_score = hazard_outputs[cid]["hazard_score"]
        distance_cost = hazard_outputs[cid]["distance_cost"]

        utility = science_score - 0.5 * hazard_score - 0.3 * distance_cost

        if utility > best_utility:
            best_utility = utility
            best_candidate = c

    return best_candidate


def decide_mode(resource_state):
    return resource_state["recommended_mode"]


def run_sim(steps=6):
    world = initialize_world()
    science_candidates = get_manual_science_candidates()
    hazard_outputs = get_hazard_outputs()
    execution_model = ExecutionModel()

    for step in range(steps):
        selected_candidate = choose_target(science_candidates, hazard_outputs)
        selected_target = (selected_candidate["x"], selected_candidate["y"])

        world = update_mission_state(world, selected_target)

        rover_state_for_resource = {
            "x": world["rover"]["position"][0],
            "y": world["rover"]["position"][1],
            "battery": world["rover"]["battery"],
            "health": world["rover"]["health"],
            "speed": world["rover"]["speed"],
        }

        drone_state_for_resource = {
            "x": world["drone"]["position"][0],
            "y": world["drone"]["position"][1],
            "battery": world["drone"]["battery"],
            "health": world["drone"]["health"],
            "available": world["drone"]["available"],
            "in_flight": world["drone"]["in_flight"],
        }

        resource_state = get_resource_state(
            rover_state_for_resource,
            drone_state_for_resource,
            world["mission"]
        )

        mode = decide_mode(resource_state)

        decision_output = {
            "mode": mode,
            "target": selected_target
        }

        rover_exec_state = {"position": world["rover"]["position"]}
        drone_exec_state = {"position": world["drone"]["position"]}

        execution_output = execution_model.execute(
            rover_exec_state,
            drone_exec_state,
            decision_output
        )

        world["rover"]["position"] = execution_output["rover_next"]
        world["drone"]["position"] = execution_output["drone_next"]
        world["drone"]["in_flight"] = execution_output["drone_action"] in ["SCOUT_AREA", "RETURN_TO_ROVER"]

        print(f"\n=== STEP {step} ===")
        print("Selected candidate:", selected_candidate)
        print("Resource state:", resource_state)
        print("Decision output:", decision_output)
        print("Execution output:", execution_output)

        render_world(world, science_candidates, selected_target, execution_output, step)


if __name__ == "__main__":
    run_sim()
