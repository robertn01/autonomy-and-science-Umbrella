import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader, random_split
import numpy as np
import os
import datetime

from ai_models.hazard_traversability.dataset_utils import prepare_numpy_dataset
from ai_models.hazard_traversability.model import SimpleHazardCNN


def train_model(
    split="train",
    num_samples=1200,
    raw_limit=1800,
    batch_size=16,
    learning_rate=1e-3,
    num_epochs=12,
    val_fraction=0.2,
    model_save_path="ai_models/hazard_traversability/hazard_cnn_baseline.pth"
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    X, y = prepare_numpy_dataset(split=split, num_samples=num_samples, raw_limit=raw_limit)

    print("Dataset loaded:")
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    unique, counts = np.unique(y, return_counts=True)
    print("Label distribution:", dict(zip(unique.tolist(), counts.tolist())))

    X_t = torch.tensor(X, dtype=torch.float32).permute(0, 3, 1, 2)
    y_t = torch.tensor(y, dtype=torch.long)

    dataset = TensorDataset(X_t, y_t)

    val_size = int(len(dataset) * val_fraction)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = SimpleHazardCNN(num_classes=3).to(device)

    class_counts = np.bincount(y, minlength=3)
    class_weights = 1.0 / class_counts
    class_weights = class_weights / class_weights.sum() * 3.0
    class_weights = torch.tensor(class_weights, dtype=torch.float32).to(device)

    print("Class weights:", class_weights)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_val_acc = 0.0

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)

            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * xb.size(0)
            preds = torch.argmax(logits, dim=1)
            train_correct += (preds == yb).sum().item()
            train_total += yb.size(0)

        train_loss /= train_total
        train_acc = train_correct / train_total

        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                logits = model(xb)
                loss = criterion(logits, yb)

                val_loss += loss.item() * xb.size(0)
                preds = torch.argmax(logits, dim=1)
                val_correct += (preds == yb).sum().item()
                val_total += yb.size(0)

        val_loss /= val_total
        val_acc = val_correct / val_total

        print(
            f"Epoch {epoch+1}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_save_path)
            print(f"New best model saved at epoch {epoch+1}")

    print("Best validation accuracy:", best_val_acc)
    print("Saved model timestamp:", datetime.datetime.fromtimestamp(os.path.getmtime(model_save_path)))
    print("Saved model size:", os.path.getsize(model_save_path))


if __name__ == "__main__":
    train_model()
