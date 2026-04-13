
from decision_demo.execution_model import ExecutionModel


def run_demo():
    rover_state = {
        "position": (2, 2)
    }

    drone_state = {
        "position": (3, 3)
    }

    decision_output = {
        "mode": "SCOUT_READY",
        "target": (8, 7)
    }

    model = ExecutionModel()
    execution_output = model.execute(rover_state, drone_state, decision_output)

    print("=== EXECUTION MODEL DEMO ===")
    print("Rover state:", rover_state)
    print("Drone state:", drone_state)
    print("Decision output:", decision_output)
    print("Execution output:", execution_output)


if __name__ == "__main__":
    run_demo()
