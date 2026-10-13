"""Simulate 340 bioburden samples across 4 unit operations, with real
CFU (colony-forming unit) counts and a known ground-truth contamination-
event flag (independent of the detection rule) -- the setting for a
genuine detection-accuracy validation."""
from __future__ import annotations

import numpy as np
import pandas as pd

N_SAMPLES = 340
SEED = 197
UNIT_OPERATIONS = ["Cell Culture Harvest", "Depth Filtration", "Chromatography Pool", "Final Fill"]
ACTION_LIMIT_CFU = 10  # CFU/100mL, a standard bioburden action limit


def simulate(n: int = N_SAMPLES, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    unit_op = rng.choice(UNIT_OPERATIONS, n)

    # ground truth: ~4% of samples represent a true contamination event
    # (independent of what gets measured -- a real microbial excursion)
    true_contamination_event = rng.random(n) < 0.04

    baseline_cfu = rng.poisson(1.5, n)
    event_cfu = rng.poisson(40, n)
    measured_cfu = np.where(true_contamination_event, event_cfu, baseline_cfu)

    # measurement noise: occasional false-negative dilution error (a real
    # plate-count assay limitation) -- ~5% of true events are under-counted
    dilution_error_idx = rng.choice(np.where(true_contamination_event)[0],
                                     size=max(1, int(true_contamination_event.sum() * 0.1)), replace=False)
    measured_cfu[dilution_error_idx] = rng.poisson(3, len(dilution_error_idx))

    return pd.DataFrame({
        "sample_id": [f"BB-{i:04d}" for i in range(n)],
        "unit_operation": unit_op, "measured_cfu_per_100ml": measured_cfu,
        "true_contamination_event": true_contamination_event,
    })


if __name__ == "__main__":
    df = simulate()
    print(df.shape)
    print("True contamination events:", df["true_contamination_event"].sum())
