from ai_models.hazard_traversability.dataset_utils import load_ai4mars_subset
import numpy as np


def inspect_label_values(split="train", raw_limit=50):
    ds = load_ai4mars_subset(split=split, raw_limit=raw_limit)

    global_counts = {}

    for i, ex in enumerate(ds):
        try:
            if not ex.get("has_labels", False):
                continue
            if ex.get("label_mask", None) is None:
                continue

            mask = np.array(ex["label_mask"])

            if len(mask.shape) > 2:
                mask = mask[..., 0]

            unique, counts = np.unique(mask, return_counts=True)

            for u, c in zip(unique.tolist(), counts.tolist()):
                global_counts[u] = global_counts.get(u, 0) + c

        except Exception as e:
            print(f"Skipping sample {i} due to error: {e}")
            continue

    print("=== GLOBAL LABEL VALUE COUNTS ===")
    for k in sorted(global_counts.keys()):
        print(f"Label {k}: {global_counts[k]}")


if __name__ == "__main__":
    inspect_label_values()
