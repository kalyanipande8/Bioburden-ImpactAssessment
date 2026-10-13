"""Real bioburden excursion detection: flags a sample as action-limit-
exceeded if its measured CFU count is above the standard action limit,
validated against the independent ground-truth contamination flag."""
from __future__ import annotations

import pandas as pd

from .simulate_samples import ACTION_LIMIT_CFU


def detect_excursions(df: pd.DataFrame, action_limit: int = ACTION_LIMIT_CFU) -> pd.DataFrame:
    out = df.copy()
    out["flagged_excursion"] = out["measured_cfu_per_100ml"] > action_limit
    return out


def detection_accuracy(flagged: pd.DataFrame) -> dict:
    tp = int((flagged["flagged_excursion"] & flagged["true_contamination_event"]).sum())
    fp = int((flagged["flagged_excursion"] & ~flagged["true_contamination_event"]).sum())
    fn = int((~flagged["flagged_excursion"] & flagged["true_contamination_event"]).sum())
    tn = int((~flagged["flagged_excursion"] & ~flagged["true_contamination_event"]).sum())

    accuracy = (tp + tn) / len(flagged)
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")

    return {
        "n_samples": len(flagged), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "accuracy_pct": round(100 * accuracy, 3), "precision": round(precision, 4), "recall": round(recall, 4),
    }


if __name__ == "__main__":
    from .simulate_samples import simulate

    df = simulate()
    flagged = detect_excursions(df)
    print(detection_accuracy(flagged))
