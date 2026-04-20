import os
import argparse
import logging
import numpy as np
import pandas as pd
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.models import densenet121

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    accuracy_score,
    classification_report
)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x, **kwargs: x


CLASS_NAMES_15 = [
    "Atelectasis",
    "Cardiomegaly",
    "Effusion",
    "Infiltration",
    "Mass",
    "Nodule",
    "Pneumonia",
    "Pneumothorax",
    "Consolidation",
    "Edema",
    "Emphysema",
    "Fibrosis",
    "Pleural_Thickening",
    "Hernia",
    "No Finding"
]

CLASS_NAMES_14 = [
    "Atelectasis",
    "Cardiomegaly",
    "Effusion",
    "Infiltration",
    "Mass",
    "Nodule",
    "Pneumonia",
    "Pneumothorax",
    "Consolidation",
    "Edema",
    "Emphysema",
    "Fibrosis",
    "Pleural_Thickening",
    "Hernia"
]


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def get_state_dict(checkpoint):
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        return checkpoint["model_state_dict"]
    return checkpoint


def infer_num_classes_from_checkpoint(checkpoint_path, device):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = get_state_dict(checkpoint)

    if "classifier.weight" in state_dict:
        return state_dict["classifier.weight"].shape[0]

    if "module.classifier.weight" in state_dict:
        return state_dict["module.classifier.weight"].shape[0]

    raise KeyError(
        "Could not infer number of classes from checkpoint. "
        "Expected classifier.weight or module.classifier.weight."
    )


class NIHChestXrayDataset(Dataset):
    def __init__(self, csv_path, image_dir, num_classes, transform=None):
        self.df = pd.read_csv(csv_path)
        self.image_dir = image_dir
        self.transform = transform
        self.num_classes = num_classes

        if "Image Index" not in self.df.columns or "Finding Labels" not in self.df.columns:
            raise ValueError(
                "CSV must contain columns named exactly: 'Image Index' and 'Finding Labels'"
            )

        if num_classes == 15:
            self.class_names = CLASS_NAMES_15
        elif num_classes == 14:
            self.class_names = CLASS_NAMES_14
        else:
            raise ValueError(f"Unsupported number of classes in checkpoint: {num_classes}")

        self.class_to_idx = {c: i for i, c in enumerate(self.class_names)}

    def __len__(self):
        return len(self.df)

    def encode_labels(self, label_string):
        labels = np.zeros(self.num_classes, dtype=np.float32)
        label_string = str(label_string).strip()

        if self.num_classes == 15 and label_string == "No Finding":
            labels[self.class_to_idx["No Finding"]] = 1.0
            return labels

        if label_string == "No Finding":
            return labels

        parts = [p.strip() for p in label_string.split("|") if p.strip()]
        for part in parts:
            if part in self.class_to_idx:
                labels[self.class_to_idx[part]] = 1.0

        return labels

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        img_name = str(row["Image Index"]).strip()
        img_path = os.path.join(self.image_dir, img_name)

        if not os.path.isfile(img_path):
            raise FileNotFoundError(f"Image not found: {img_path}")

        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)

        labels = self.encode_labels(row["Finding Labels"])
        labels = torch.tensor(labels, dtype=torch.float32)

        return image, labels


def load_model(checkpoint_path, num_classes, device):
    logging.info(f"Loading checkpoint from: {checkpoint_path}")

    if not os.path.isfile(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    model = densenet121(weights=None)
    model.classifier = nn.Linear(model.classifier.in_features, num_classes)

    checkpoint = torch.load(checkpoint_path, map_location=device)
    logging.info(f"Checkpoint type: {type(checkpoint)}")

    if isinstance(checkpoint, dict):
        logging.info(f"Checkpoint keys: {list(checkpoint.keys())[:20]}")

    state_dict = get_state_dict(checkpoint)

    logging.info(f"Expected classifier out features: {num_classes}")

    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    logging.info(f"Missing keys: {missing}")
    logging.info(f"Unexpected keys: {unexpected}")

    model.to(device)
    model.eval()

    logging.info("Model loaded and set to eval mode")
    logging.info(f"Classifier weight shape: {tuple(model.classifier.weight.shape)}")

    return model


@torch.no_grad()
def evaluate(model, loader, device, threshold=0.5, max_samples=1000):
    all_true = []
    all_prob = []
    seen = 0

    for batch_idx, (images, labels) in enumerate(tqdm(loader, desc="Testing")):
        images = images.to(device)
        labels = labels.to(device)

        logits = model(images)
        probs = torch.sigmoid(logits)

        if batch_idx == 0:
            logging.info(f"First batch images shape: {tuple(images.shape)}")
            logging.info(f"First batch logits shape: {tuple(logits.shape)}")
            logging.info(f"First batch probs shape: {tuple(probs.shape)}")

        all_true.append(labels.cpu().numpy())
        all_prob.append(probs.cpu().numpy())

        seen += images.size(0)
        if seen >= max_samples:
            break

    y_true = np.vstack(all_true)[:max_samples]
    y_prob = np.vstack(all_prob)[:max_samples]
    y_pred = (y_prob >= threshold).astype(int)

    results = {}
    results["micro_auc"] = roc_auc_score(y_true, y_prob, average="micro")
    results["macro_auc"] = roc_auc_score(y_true, y_prob, average="macro")
    results["micro_ap"] = average_precision_score(y_true, y_prob, average="micro")
    results["macro_ap"] = average_precision_score(y_true, y_prob, average="macro")
    results["micro_f1"] = f1_score(y_true, y_pred, average="micro", zero_division=0)
    results["macro_f1"] = f1_score(y_true, y_pred, average="macro", zero_division=0)
    results["subset_accuracy"] = accuracy_score(y_true, y_pred)
    results["label_accuracy"] = (y_true == y_pred).mean()

    return results, y_true, y_prob, y_pred


def safe_per_class_auc(y_true, y_prob, class_names):
    scores = {}
    for i, cls in enumerate(class_names):
        try:
            scores[cls] = roc_auc_score(y_true[:, i], y_prob[:, i])
        except ValueError:
            scores[cls] = float("nan")
    return scores


def main():
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_path", type=str, required=True)
    parser.add_argument("--image_dir", type=str, required=True)
    parser.add_argument("--checkpoint_path", type=str, required=True)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--num_workers", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--max_samples", type=int, default=1000)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"Using device: {device}")

    num_classes = infer_num_classes_from_checkpoint(args.checkpoint_path, device)
    logging.info(f"Inferred number of classes from checkpoint: {num_classes}")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    dataset = NIHChestXrayDataset(
        csv_path=args.csv_path,
        image_dir=args.image_dir,
        num_classes=num_classes,
        transform=transform
    )

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available()
    )

    logging.info(f"Dataset size: {len(dataset)}")
    logging.info(f"Evaluating first {args.max_samples} samples")

    model = load_model(args.checkpoint_path, num_classes=num_classes, device=device)

    logging.info("Running sanity forward pass")
    with torch.no_grad():
        dummy = torch.randn(1, 3, 224, 224).to(device)
        sanity_out = model(dummy)
    logging.info(f"Sanity output shape: {tuple(sanity_out.shape)}")

    results, y_true, y_prob, y_pred = evaluate(
        model=model,
        loader=loader,
        device=device,
        threshold=args.threshold,
        max_samples=args.max_samples
    )

    class_names = dataset.class_names

    print(f"\nSamples evaluated: {len(y_true)}")
    print(f"Micro AUC:            {results['micro_auc']:.4f}")
    print(f"Macro AUC:            {results['macro_auc']:.4f}")
    print(f"Micro AP:             {results['micro_ap']:.4f}")
    print(f"Macro AP:             {results['macro_ap']:.4f}")
    print(f"Micro F1:             {results['micro_f1']:.4f}")
    print(f"Macro F1:             {results['macro_f1']:.4f}")
    print(f"Subset Accuracy:       {results['subset_accuracy']:.4f}")
    print(f"Label Accuracy:        {results['label_accuracy']:.4f}")

    print("\nClassification Report")
    print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))

    print("\nPer-class AUC")
    per_class_auc = safe_per_class_auc(y_true, y_prob, class_names)
    for cls, score in per_class_auc.items():
        print(f"{cls}: {score:.4f}")


if __name__ == "__main__":
    main()