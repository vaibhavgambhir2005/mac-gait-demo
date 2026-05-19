"""Integration tests for session pipeline."""

from pathlib import Path
import sys

import matplotlib
import pytest

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import run_session

DATA = ROOT / "data"


def test_default_session_includes_passing_trials():
    r = run_session(DATA)
    assert r["included_trials"] == ["trial_01", "trial_02"]
    assert r["figure"] is not None
    assert r["kinematics"] is not None
    assert len(r["kinematics"].patient_mean) == 101


def test_trial_04_fails_force_qc():
    r = run_session(DATA)
    t4 = next(q for q in r["qc_results"] if q.trial_id == "trial_04")
    assert not t4.passed
    assert any("force" in f.lower() for f in t4.flags)


def test_empty_selection_no_figure():
    r = run_session(DATA, included_trial_ids=[])
    assert r["figure"] is None
    assert "Insufficient" in r["summary_md"]


def test_summary_contains_disclaimer():
    r = run_session(DATA)
    assert "Not for clinical use" in r["summary_md"]
