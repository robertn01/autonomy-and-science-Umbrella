from datasets import load_dataset
import numpy as np
from PIL import Image


def mask_to_hazard_label(mask_array):
    """
    Convert a segmentation mask into a single patch-level hazard label.

    Label mapping assumption (to refine later if needed):
    - 0 = safe
    - 1 = moderate
    - 2,3 = hazardous
    - 255 = ignore
    """

    IGNORE_LABELS = [255]
    SAFE_LABELS = [0]
    MODERATE_LABELS = [1]
    HAZARDOUS_LABELS = [2, 3]

    # Remove ignore pixels
    valid_mask = mask_array[~np.isin(mask_array, IGNORE_LABELS)]

    if valid_mask.size == 0:
        return None

    unique, counts = np.unique(valid_mask, return_counts=True)
    label_dist = dict(zip(unique.tolist(), counts.tolist()))

    total = valid_mask.size

    safe_fraction = sum(label_dist.get(lbl, 0) for lbl in SAFE_LABELS) / total
    moderate_fraction = sum(label_dist.get(lbl, 0) for lbl in MODERATE_LABELS) / total
    hazardous_fraction = sum(label_dist.get(lbl, 0) for lbl in HAZARDOUS_LABELS) / total

    # Decision thresholds
    if hazardous_fraction > 0.20:
        return 2  # hazardous
    elif moderate_fraction + hazardous_fraction > 0.40:
        return 1  # moderate
    else:
        return 0  # safe


def preprocess_example(example, image_size=(128, 128)):
    image = example["image"]
    mask = example["label_mask"]

    if image is None or mask is None:
        return None, None

    if not isinstance(image, Image.Image):
        image = Image.fromarray(np.array(image).astype(np.uint8))

    image = image.convert("RGB")

    if not isinstance(mask, Image.Image):
        mask = Image.fromarray(np.array(mask).astype(np.uint8))

    image = image.resize(image_size)
    mask = mask.resize(image_size, resample=Image.NEAREST)

    image_np = np.array(image).astype(np.float32) / 255.0
    mask_np = np.array(mask)

    if len(mask_np.shape) > 2:
        mask_np = mask_np[..., 0]

    label = mask_to_hazard_label(mask_np)

    if label is None:
        return None, None

    return image_np, label

def load_ai4mars_subset(split="train", raw_limit=200):
    """
    Load a raw subset first. We do NOT call filter() directly because
    some examples may fail during automatic decoding.
    """
    ds = load_dataset("hassanjbara/AI4MARS", split=split)
    ds = ds.select(range(min(raw_limit, len(ds))))
    return ds


def prepare_numpy_dataset(split="train", num_samples=50, image_size=(128, 128), raw_limit=300):
    ds = load_ai4mars_subset(split=split, raw_limit=raw_limit)

    images = []
    labels = []

    for i, ex in enumerate(ds):
        if len(images) >= num_samples:
            break

        try:
            if not ex.get("has_labels", False):
                continue
            if ex.get("label_mask", None) is None:
                continue

            img, lbl = preprocess_example(ex, image_size=image_size)

            if img is None or lbl is None:
                continue

            images.append(img)
            labels.append(lbl)

        except Exception as e:
            print(f"Skipping sample {i} due to error: {e}")
            continue

    if len(images) == 0:
        raise ValueError("No valid samples were collected from AI4Mars.")

    X = np.stack(images)
    y = np.array(labels)

    return X, y
