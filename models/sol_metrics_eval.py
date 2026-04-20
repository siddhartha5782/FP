import pandas as pd
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    accuracy_score,
    classification_report,
)

csv_path = r"D:\\FP\\models\\sol_metrics\\run1_best_val_predictions.csv"   # change this

df = pd.read_csv(csv_path)

# Find labels from the column names
labels = []
for col in df.columns:
    if col.startswith("true_"):
        labels.append(col.replace("true_", ""))

# Build arrays
y_true = np.stack([df[f"true_{label}"].values for label in labels], axis=1)
y_prob = np.stack([df[f"prob_{label}"].values for label in labels], axis=1)
y_pred = np.stack([df[f"pred_{label}"].values for label in labels], axis=1)

# Overall metrics
micro_auc = roc_auc_score(y_true, y_prob, average="micro")
macro_auc = roc_auc_score(y_true, y_prob, average="macro")
micro_ap = average_precision_score(y_true, y_prob, average="micro")
macro_ap = average_precision_score(y_true, y_prob, average="macro")

micro_f1 = f1_score(y_true, y_pred, average="micro", zero_division=0)
macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

subset_accuracy = accuracy_score(y_true, y_pred)
label_accuracy = (y_true == y_pred).mean()

print(f"Samples evaluated: {len(df)}")
print(f"Micro AUC:         {micro_auc:.4f}")
print(f"Macro AUC:         {macro_auc:.4f}")
print(f"Micro AP:          {micro_ap:.4f}")
print(f"Macro AP:          {macro_ap:.4f}")
print(f"Micro F1:          {micro_f1:.4f}")
print(f"Macro F1:          {macro_f1:.4f}")
print(f"Subset Accuracy:    {subset_accuracy:.4f}")
print(f"Label Accuracy:     {label_accuracy:.4f}")

print("\nClassification Report")
print(classification_report(y_true, y_pred, target_names=labels, zero_division=0))

print("\nPer-class AUC")
for i, label in enumerate(labels):
    try:
        auc = roc_auc_score(y_true[:, i], y_prob[:, i])
        print(f"{label}: {auc:.4f}")
    except ValueError:
        print(f"{label}: NaN")

print("\nPer-class AP")
for i, label in enumerate(labels):
    try:
        ap = average_precision_score(y_true[:, i], y_prob[:, i])
        print(f"{label}: {ap:.4f}")
    except ValueError:
        print(f"{label}: NaN")