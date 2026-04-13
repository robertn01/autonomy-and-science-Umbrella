import torch
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime

from ai_models.hazard_traversability.dataset_utils import prepare_numpy_dataset
from ai_models.hazard_traversability.model import SimpleHazardCNN, logits_to_outputs

LABEL_NAMES = {
    0: "safe",
    1: "moderate",
    2: "hazardous"
}


def run_inference_demo():
    X, y = prepare_numpy_dataset(split="train", num_samples=8, raw_limit=100)

    print("X shape:", X.shape)
    print("y shape:", y.shape)

    unique, counts = np.unique(y, return_counts=True)
    print("Label distribution:", {LABEL_NAMES[int(k)]: int(v) for k, v in zip(unique, counts)})

    X_t = torch.tensor(X).permute(0, 3, 1, 2)

    model = SimpleHazardCNN(num_classes=3)

    model_path = "ai_models/hazard_traversability/hazard_cnn_baseline.pth"
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        print(f"Loaded trained model from: {model_path}")
    else:
        print("WARNING: trained model not found, using untrained weights.")

    model.eval()

    with torch.no_grad():
        logits = model(X_t)
        outputs = logits_to_outputs(logits)

    probs = torch.softmax(logits, dim=1)

    print("=== HAZARD MODEL INFERENCE DEMO ===")
    for i, out in enumerate(outputs):
        print(f"Sample {i}: true_label={LABEL_NAMES[int(y[i])]}, output={out}")
        print("  class probs:",
              {
                  "safe": float(probs[i, 0]),
                  "moderate": float(probs[i, 1]),
                  "hazardous": float(probs[i, 2]),
              })

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()

    for i in range(min(8, len(X))):
        axes[i].imshow(X[i])
        axes[i].axis("off")
        axes[i].set_title(
            f"True: {LABEL_NAMES[int(y[i])]}\n"
            f"Pred: {outputs[i]['hazard_type']}\n"
            f"Conf: {outputs[i]['confidence']:.2f}"
        )

    plt.tight_layout()
    plt.show()

    fig.savefig("hazard_inference_demo.png", dpi=200, bbox_inches="tight")
    print("Saved evidence image as: hazard_inference_demo.png")

    if os.path.exists(model_path):
        print("Loaded model timestamp:", datetime.datetime.fromtimestamp(os.path.getmtime(model_path)))
        print("Loaded model size:", os.path.getsize(model_path))


if __name__ == "__main__":
    run_inference_demo()
