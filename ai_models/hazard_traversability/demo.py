from ai_models.hazard_traversability.model import HazardTraversabilityModel
from ai_models.hazard_traversability.manual_inputs import get_manual_hazard_inputs


def run_demo():
    model = HazardTraversabilityModel()
    terrain_inputs = get_manual_hazard_inputs()
    results = model.evaluate_all_candidates(terrain_inputs)

    print("=== HAZARD / TRAVERSABILITY RESULTS ===")
    for cid, result in results.items():
        print(f"Candidate {cid}: {result}")


if __name__ == "__main__":
    run_demo()
