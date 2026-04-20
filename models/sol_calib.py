import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, classification_report, roc_auc_score, average_precision_score, accuracy_score

csv_path = r"D:\\FP\\models\\sol_metrics\\run1_best_val_predictions.csv"  # change this

df = pd.read_csv(csv_path)

# Get class names from columns like true_Atelectasis, prob_Atelectasis, pred_Atelectasis
labels = [c.replace("true_", "") for c in df.columns if c.startswith("true_")]

y_true = np.stack([df[f"true_{c}"].values for c in labels], axis=1)
y_prob = np.stack([df[f"prob_{c}"].values for c in labels], axis=1)

def find_best_thresholds(y_true, y_prob, thresholds=np.arange(0.05, 0.96, 0.05)):
    best_thresholds = []
    best_f1s = []

    for i, cls in enumerate(labels):
        best_t = 0.5
        best_f1 = -1.0

        for t in thresholds:
            y_pred_cls = (y_prob[:, i] >= t).astype(int)
            f1 = f1_score(y_true[:, i], y_pred_cls, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_t = t

        best_thresholds.append(best_t)
        best_f1s.append(best_f1)
        print(f"{cls}: best threshold = {best_t:.2f}, best F1 = {best_f1:.4f}")

    return np.array(best_thresholds), np.array(best_f1s)

thresholds, per_class_best_f1 = find_best_thresholds(y_true, y_prob)

# Apply tuned thresholds
y_pred = (y_prob >= thresholds.reshape(1, -1)).astype(int)

# Overall metrics
micro_auc = roc_auc_score(y_true, y_prob, average="micro")
macro_auc = roc_auc_score(y_true, y_prob, average="macro")
micro_ap = average_precision_score(y_true, y_prob, average="micro")
macro_ap = average_precision_score(y_true, y_prob, average="macro")
micro_f1 = f1_score(y_true, y_pred, average="micro", zero_division=0)
macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
subset_acc = accuracy_score(y_true, y_pred)
label_acc = (y_true == y_pred).mean()

print("\nFinal metrics with tuned thresholds")
print(f"Micro AUC:      {micro_auc:.4f}")
print(f"Macro AUC:      {macro_auc:.4f}")
print(f"Micro AP:       {micro_ap:.4f}")
print(f"Macro AP:       {macro_ap:.4f}")
print(f"Micro F1:       {micro_f1:.4f}")
print(f"Macro F1:       {macro_f1:.4f}")
print(f"Subset Accuracy: {subset_acc:.4f}")
print(f"Label Accuracy:  {label_acc:.4f}")

print("\nClassification Report")
print(classification_report(y_true, y_pred, target_names=labels, zero_division=0))

print("\nChosen thresholds")
for cls, t in zip(labels, thresholds):
    print(f"{cls}: {t:.2f}")