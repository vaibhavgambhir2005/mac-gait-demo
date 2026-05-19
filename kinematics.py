"""Ensemble kinematics and comparison to normative bands."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.events import CYCLE_POINTS, extract_cycles_from_trial


@dataclass
class KinematicComparison:
    patient_mean: np.ndarray
    norm_mean: np.ndarray
    norm_sd: np.ndarray
    per_trial_curves: dict[str, np.ndarray]
    peak_flexion_diff: float
    rmse_deg: float
    deviation_flags: list[str]


def load_normative(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def ensemble_cycles(cycles_by_trial: dict[str, list[np.ndarray]]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    per_trial_mean: dict[str, np.ndarray] = {}
    stack = []
    for tid, cycles in cycles_by_trial.items():
        if not cycles:
            continue
        arr = np.vstack(cycles)
        mean_curve = np.mean(arr, axis=0)
        per_trial_mean[tid] = mean_curve
        stack.append(mean_curve)
    if not stack:
        return np.full(CYCLE_POINTS, np.nan), per_trial_mean
    return np.mean(np.vstack(stack), axis=0), per_trial_mean


def compare_to_norms(
    patient_mean: np.ndarray,
    norms: pd.DataFrame,
    sd_multiplier: float = 2.0,
    contiguous_pct_threshold: float = 10.0,
) -> KinematicComparison:
    norm_mean = norms["mean_deg"].to_numpy()
    norm_sd = norms["sd_deg"].to_numpy()
    upper = norm_mean + sd_multiplier * norm_sd
    lower = norm_mean - sd_multiplier * norm_sd

    outside = (patient_mean > upper) | (patient_mean < lower)
    flags: list[str] = []
    if np.any(outside):
        run = 0
        max_run = 0
        for val in outside:
            run = run + 1 if val else 0
            max_run = max(max_run, run)
        if max_run >= int(contiguous_pct_threshold):
            flags.append(
                f"Knee flexion outside norm ±{sd_multiplier:.0f} SD for "
                f"≥{contiguous_pct_threshold:.0f}% of gait cycle (clinician review)"
            )

    peak_diff = float(np.nanmax(patient_mean) - np.nanmax(norm_mean))
    rmse = float(np.sqrt(np.nanmean((patient_mean - norm_mean) ** 2)))

    return KinematicComparison(
        patient_mean=patient_mean,
        norm_mean=norm_mean,
        norm_sd=norm_sd,
        per_trial_curves={},
        peak_flexion_diff=round(peak_diff, 2),
        rmse_deg=round(rmse, 2),
        deviation_flags=flags,
    )


def process_trials(
    trials: dict[str, pd.DataFrame],
    normative_path: str | Path,
    fs: float = 100.0,
    signal_col: str = "knee_flexion_deg",
) -> KinematicComparison:
    cycles_by_trial: dict[str, list[np.ndarray]] = {}
    for tid, df in trials.items():
        cycles_by_trial[tid] = extract_cycles_from_trial(df, signal_col=signal_col, fs=fs)

    patient_mean, per_trial = ensemble_cycles(cycles_by_trial)
    norms = load_normative(normative_path)
    result = compare_to_norms(patient_mean, norms)
    result.per_trial_curves = per_trial
    return result
