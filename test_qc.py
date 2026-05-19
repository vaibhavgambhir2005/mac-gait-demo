"""Basic QC tests for demo trials."""

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qc import run_qc

DATA = ROOT / "data" / "trials"


def test_trial_03_fails_marker_qc():
    df = pd.read_csv(DATA / "trial_03_bad_dropout.csv")
    result = run_qc(df)
    assert not result.passed
    assert any("Marker" in f for f in result.flags)


def test_trial_01_passes_qc():
    df = pd.read_csv(DATA / "trial_01_good.csv")
    result = run_qc(df)
    assert result.passed
