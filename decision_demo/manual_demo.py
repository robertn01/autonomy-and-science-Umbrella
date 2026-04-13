from decision_demo.manual_inputs import get_manual_inputs
from decision_demo.candidate_decision_manager import CandidateDecisionManager


def run_manual_demo():
    science_candidates, resource_state, hazard_overrides, rover_position = get_manual_inputs()
    manager = CandidateDecisionManager()

    decision = manager.decide(
        science_candidates=science_candidates,
        resource_state=resource_state,
        hazard_overrides=hazard_overrides,
        rover_position=rover_position
    )

    print("=== MANUAL INPUTS ===")
    print("Rover position:", rover_position)
    print("Science candidates:")
    for c in science_candidates:
        print(c)

    print("\nResource state:")
    print(resource_state)

    print("\nHazard overrides:")
    print(hazard_overrides)

    print("\n=== FINAL DECISION ===")
    print(decision)


if __name__ == "__main__":
    run_manual_demo()
