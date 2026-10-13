"""End-to-end: simulate 340 bioburden samples, detect excursions,
validate detection accuracy against ground truth, and assess risk by
unit operation."""
import json
import os

from src.simulate_samples import simulate
from src.detection_model import detect_excursions, detection_accuracy
from src.risk_assessment import assess_risk_by_unit_operation

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating 340 bioburden samples across 4 unit operations ===")
df = simulate()
df.to_csv("data/bioburden_samples.csv", index=False)
print(df.shape)
print("True contamination events:", int(df["true_contamination_event"].sum()))

print("\n=== Detecting excursions (action limit: 10 CFU/100mL) ===")
flagged = detect_excursions(df)
flagged.to_csv("data/flagged_samples.csv", index=False)

print("\n=== Detection accuracy (validated against ground truth) ===")
accuracy = detection_accuracy(flagged)
print(accuracy)

print("\n=== Risk assessment by unit operation ===")
risk = assess_risk_by_unit_operation(flagged)
print(risk)
risk.to_csv("results/risk_by_unit_operation.csv", index=False)

summary = {
    "n_samples": accuracy["n_samples"],
    "n_true_contamination_events": int(df["true_contamination_event"].sum()),
    "detection_accuracy_pct": accuracy["accuracy_pct"],
    "detection_precision": accuracy["precision"],
    "detection_recall": accuracy["recall"],
    "highest_risk_unit_operation": risk.iloc[0]["unit_operation"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
