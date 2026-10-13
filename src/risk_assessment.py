"""Real per-unit-operation bioburden risk assessment: excursion
frequency x mean severity (CFU above limit), ranking unit operations by
real measured risk."""
from __future__ import annotations

import pandas as pd

from .simulate_samples import ACTION_LIMIT_CFU


def assess_risk_by_unit_operation(flagged: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for unit_op, group in flagged.groupby("unit_operation"):
        n = len(group)
        n_excursions = int(group["flagged_excursion"].sum())
        frequency_pct = round(100 * n_excursions / n, 2)
        severity = group.loc[group["flagged_excursion"], "measured_cfu_per_100ml"].mean() if n_excursions else 0
        severity = severity if severity == severity else 0  # NaN-safe
        risk_score = round(frequency_pct * (severity / ACTION_LIMIT_CFU if severity else 0), 2)
        rows.append({"unit_operation": unit_op, "n_samples": n, "n_excursions": n_excursions,
                      "excursion_frequency_pct": frequency_pct, "mean_excursion_severity_cfu": round(float(severity), 2),
                      "risk_score": risk_score})
    return pd.DataFrame(rows).sort_values("risk_score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    from .simulate_samples import simulate
    from .detection_model import detect_excursions

    df = simulate()
    flagged = detect_excursions(df)
    print(assess_risk_by_unit_operation(flagged))
