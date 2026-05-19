"""Quality control checks for gait trial time-series."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks

QC_CONFIG = {
    "marker_mean_min": 0.92,
    "marker_max_gap_frames": 15,
    "force_snr_max": 0.35,
    "emg_baseline_std_max": 35.0,
    "emg_baseline_seconds": 0.35,
    "min_grf_peaks": 4,
    "sample_rate_hz": 100.0,
}

SUGGESTED_ACTIONS = {
    "marker": "Re-check lateral knee marker placement; reduce occlusion during mid-swing.",
    "force": "Inspect force plate mounting; repeat trial if impact artifacts persist.",
    "emg": "Verify skin prep and electrode contact; re-apply EMG if baseline is noisy.",
    "length": "Collect additional steady-state walking trials (target ≥6 steps).",
}


@dataclass
class QCResult:
    trial_id: str
    passed: bool
    flags: list[str]
    metrics: dict
    suggested_actions: list[str]


def _max_gap_length(visible: np.ndarray) -> int:
    gaps = []
    current = 0
    for v in visible:
        if v < 0.5:
            current += 1
        else:
            if current:
                gaps.append(current)
            current = 0
    if current:
        gaps.append(current)
    return max(gaps) if gaps else 0


def _force_snr(grf: np.ndarray, fs: float) -> float:
    nyq = fs / 2
    b_lo, a_lo = butter(2, 6 / nyq, btype="low")
    b_hi, a_hi = butter(2, 12 / nyq, btype="high")
    low = filtfilt(b_lo, a_lo, grf)
    high = filtfilt(b_hi, a_hi, grf)
    denom = np.std(low)
    if denom < 1e-6:
        return 999.0
    return float(np.std(high) / denom)


def _emg_baseline_std(emg: np.ndarray, fs: float) -> float:
    n = max(10, int(QC_CONFIG["emg_baseline_seconds"] * fs))
    return float(np.std(emg[:n]))


def _count_grf_peaks(grf: np.ndarray, fs: float) -> int:
    peaks, _ = find_peaks(grf, height=np.percentile(grf, 60), distance=int(0.4 * fs))
    return len(peaks)


def run_qc(trial: pd.DataFrame, fs: float | None = None) -> QCResult:
    fs = fs or QC_CONFIG["sample_rate_hz"]
    trial_id = str(trial["trial_id"].iloc[0])
    flags: list[str] = []
    actions: list[str] = []
    metrics: dict = {}

    marker = trial["marker_visible"].to_numpy(dtype=float)
    grf = trial["grf_vertical_N"].to_numpy(dtype=float)
    emg = trial["emg_tib_ant_uV"].to_numpy(dtype=float)

    marker_mean = float(np.mean(marker))
    max_gap = _max_gap_length(marker)
    metrics["marker_mean"] = round(marker_mean, 3)
    metrics["marker_max_gap_frames"] = max_gap

    if marker_mean < QC_CONFIG["marker_mean_min"] or max_gap > QC_CONFIG["marker_max_gap_frames"]:
        flags.append("Marker dropout — check lateral knee marker / occlusion")
        actions.append(SUGGESTED_ACTIONS["marker"])

    snr = _force_snr(grf, fs)
    metrics["force_snr"] = round(snr, 3)
    if snr > QC_CONFIG["force_snr_max"]:
        flags.append("Noisy force plate — check mounting / impact artifacts")
        actions.append(SUGGESTED_ACTIONS["force"])

    emg_std = _emg_baseline_std(emg, fs)
    metrics["emg_baseline_std_uV"] = round(emg_std, 2)
    if emg_std > QC_CONFIG["emg_baseline_std_max"]:
        flags.append("EMG baseline noise — skin prep/electrode contact")
        actions.append(SUGGESTED_ACTIONS["emg"])

    n_peaks = _count_grf_peaks(grf, fs)
    metrics["grf_peaks"] = n_peaks
    if n_peaks < QC_CONFIG["min_grf_peaks"]:
        flags.append("Insufficient steady-state walking")
        actions.append(SUGGESTED_ACTIONS["length"])

    passed = len(flags) == 0
    return QCResult(
        trial_id=trial_id,
        passed=passed,
        flags=flags,
        metrics=metrics,
        suggested_actions=list(dict.fromkeys(actions)),
    )
