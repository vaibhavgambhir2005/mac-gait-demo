"""One-time script to generate synthetic trial CSVs and normative data."""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def knee_flexion_profile(phase: np.ndarray, peak1: float, peak2: float) -> np.ndarray:
    """Typical double-hump sagittal knee flexion (degrees)."""
    return peak1 * np.sin(np.pi * phase) ** 2 + peak2 * np.sin(2 * np.pi * phase) ** 2 + 5


def grf_profile(phase: np.ndarray, body_weight: float = 350) -> np.ndarray:
    """Two-peak vertical GRF pattern per gait cycle."""
    return body_weight * (
        0.2 + 1.1 * np.exp(-((phase - 0.15) ** 2) / 0.02)
        + 0.9 * np.exp(-((phase - 0.55) ** 2) / 0.025)
    )


def build_trial(
    trial_id: str,
    n_steps: int = 8,
    fs: float = 100.0,
    marker_dropout: bool = False,
    force_noise: bool = False,
    emg_noisy: bool = False,
) -> pd.DataFrame:
    frames_per_step = int(fs * 1.0)
    n_frames = n_steps * frames_per_step
    rows = []

    for step in range(n_steps):
        t0 = step * frames_per_step
        for i in range(frames_per_step):
            idx = t0 + i
            phase = i / frames_per_step
            time_s = idx / fs

            knee = knee_flexion_profile(phase, 42, 28)
            ankle = 5 + 15 * np.sin(2 * np.pi * phase)
            hip = 20 + 25 * np.sin(np.pi * phase)
            grf = grf_profile(phase)
            if idx < 40 and not emg_noisy:
                emg = 12 + 2 * np.random.randn()
            elif phase > 0.12:
                emg = 50 + 120 * np.maximum(0, np.sin(2 * np.pi * (phase - 0.12)))
            else:
                emg = 15 + 3 * np.random.randn()
            marker = 1.0

            if marker_dropout and step >= 4 and 0.25 < phase < 0.55:
                marker = 0.0
                knee += np.random.normal(0, 8)

            if force_noise:
                grf += np.random.normal(0, 80)
                if i % 17 == 0:
                    grf += np.random.uniform(200, 400)

            if emg_noisy:
                emg += np.random.normal(0, 55)

            rows.append(
                {
                    "time_s": round(time_s, 4),
                    "trial_id": trial_id,
                    "marker_visible": marker,
                    "grf_vertical_N": round(grf, 2),
                    "emg_tib_ant_uV": round(emg, 2),
                    "ankle_angle_deg": round(ankle, 2),
                    "knee_flexion_deg": round(knee, 2),
                    "hip_flexion_deg": round(hip, 2),
                }
            )

    return pd.DataFrame(rows)


def build_normative() -> pd.DataFrame:
    pct = np.linspace(0, 100, 101)
    phase = pct / 100.0
    mean = knee_flexion_profile(phase, 45, 30)
    sd = 4.5 + 2.0 * np.sin(2 * np.pi * phase)
    return pd.DataFrame({"gait_pct": pct, "mean_deg": mean.round(2), "sd_deg": sd.round(2)})


def main() -> None:
    (DATA / "trials").mkdir(parents=True, exist_ok=True)
    (DATA / "normative").mkdir(parents=True, exist_ok=True)

    trials = [
        ("trial_01_good.csv", "trial_01", {}),
        ("trial_02_good.csv", "trial_02", {}),
        ("trial_03_bad_dropout.csv", "trial_03", {"marker_dropout": True}),
        ("trial_04_bad_force.csv", "trial_04", {"force_noise": True}),
    ]
    for fname, tid, kwargs in trials:
        df = build_trial(tid, **kwargs)
        df.to_csv(DATA / "trials" / fname, index=False)

    build_normative().to_csv(DATA / "normative" / "knee_flexion_norm.csv", index=False)

    meta = {
        "patient_id": "DEMO-001",
        "age_years": 10,
        "sex": "F",
        "condition": "cerebral_palsy_unilateral",
        "assessment_date": "2026-05-16",
        "conditions_tested": ["barefoot", "with_AFO"],
        "selected_condition": "barefoot",
    }
    import json

    (DATA / "session_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("Synthetic data written to", DATA)


if __name__ == "__main__":
    main()
