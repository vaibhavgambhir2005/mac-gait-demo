"""Gait event detection and cycle normalization (0–100%)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

CYCLE_POINTS = 101


def detect_heel_strikes(grf: np.ndarray, fs: float) -> list[int]:
    """Heel strikes from vertical GRF peaks (simplified heuristic)."""
    height = np.percentile(grf, 55)
    distance = max(1, int(0.45 * fs))
    peaks, _ = find_peaks(grf, height=height, distance=distance)
    return peaks.tolist()


def normalize_to_gait_cycles(
    signal: np.ndarray,
    hs_indices: list[int],
) -> list[np.ndarray]:
    """Resample each inter-heel-strike interval to 101 points."""
    cycles: list[np.ndarray] = []
    if len(hs_indices) < 2:
        return cycles

    for start, end in zip(hs_indices[:-1], hs_indices[1:]):
        segment = signal[start:end]
        if len(segment) < 5:
            continue
        x_old = np.linspace(0, 100, len(segment))
        x_new = np.linspace(0, 100, CYCLE_POINTS)
        cycles.append(np.interp(x_new, x_old, segment))
    return cycles


def extract_cycles_from_trial(
    trial: pd.DataFrame,
    signal_col: str = "knee_flexion_deg",
    fs: float = 100.0,
) -> list[np.ndarray]:
    grf = trial["grf_vertical_N"].to_numpy(dtype=float)
    signal = trial[signal_col].to_numpy(dtype=float)
    hs = detect_heel_strikes(grf, fs)
    return normalize_to_gait_cycles(signal, hs)
