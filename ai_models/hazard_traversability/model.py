import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleHazardCNN(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 16 * 16, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def logits_to_outputs(logits):
    probs = F.softmax(logits, dim=1)
    pred_class = torch.argmax(probs, dim=1)

    outputs = []
    for i in range(len(pred_class)):
        cls = pred_class[i].item()
        conf = probs[i, cls].item()

        if cls == 0:
            hazard_type = "safe"
            hazard_score = 1.0 - conf * 0.3
        elif cls == 1:
            hazard_type = "moderate"
            hazard_score = 0.5
        else:
            hazard_type = "hazardous"
            hazard_score = min(1.0, 0.6 + conf * 0.4)

        traversability_score = 1.0 - hazard_score

        outputs.append({
            "hazard_type": hazard_type,
            "hazard_score": float(hazard_score),
            "traversability_score": float(traversability_score),
            "confidence": float(conf)
        })

    return outputs
