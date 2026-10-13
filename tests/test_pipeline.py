import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_samples import simulate, UNIT_OPERATIONS
from src.detection_model import detect_excursions, detection_accuracy
from src.risk_assessment import assess_risk_by_unit_operation


@pytest.fixture(scope="module")
def df():
    return simulate()


@pytest.fixture(scope="module")
def flagged(df):
    return detect_excursions(df)


def test_340_samples_simulated(df):
    assert len(df) == 340


def test_all_unit_operations_represented(df):
    assert set(df["unit_operation"].unique()) == set(UNIT_OPERATIONS)


def test_some_true_contamination_events_exist(df):
    assert df["true_contamination_event"].sum() > 0


def test_detection_precision_is_high(flagged):
    result = detection_accuracy(flagged)
    assert result["precision"] >= 0.9


def test_detection_recall_is_not_perfect(flagged):
    """The simulation injects a real dilution-error false-negative mode
    -- recall should be high but honestly below 100%."""
    result = detection_accuracy(flagged)
    assert result["recall"] < 1.0


def test_detection_accuracy_in_realistic_band(flagged):
    result = detection_accuracy(flagged)
    assert 95.0 <= result["accuracy_pct"] <= 100.0


def test_risk_assessment_ranks_all_unit_operations(flagged):
    risk = assess_risk_by_unit_operation(flagged)
    assert len(risk) == len(UNIT_OPERATIONS)
    assert risk["risk_score"].is_monotonic_decreasing
