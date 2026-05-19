"""Clinical-style plots and markdown summaries."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.kinematics import KinematicComparison
from src.qc import QCResult


def plot_knee_flexion(
    kinematics: KinematicComparison,
    norms: pd.DataFrame,
    title: str = "Sagittal knee flexion vs age-matched normative band",
) -> plt.Figure:
    pct = norms["gait_pct"].to_numpy()
    fig, ax = plt.subplots(figsize=(9, 5))
    mean = norms["mean_deg"].to_numpy()
    sd = norms["sd_deg"].to_numpy()

    ax.fill_between(pct, mean - sd, mean + sd, alpha=0.25, label="Norm ±1 SD")
    ax.plot(pct, mean, "k--", linewidth=1.2, label="Norm mean")

    for tid, curve in kinematics.per_trial_curves.items():
        ax.plot(pct, curve, alpha=0.35, linewidth=1, label=f"{tid} (trial mean)")

    ax.plot(pct, kinematics.patient_mean, "C0", linewidth=2.5, label="Patient ensemble")
    ax.axvline(0, color="gray", linestyle=":", alpha=0.6)
    ax.axvline(60, color="gray", linestyle=":", alpha=0.4)
    ax.set_xlabel("Gait cycle (%) — 0% = heel strike")
    ax.set_ylabel("Knee flexion (deg)")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def generate_clinical_summary(
    meta: dict,
    qc_results: list[QCResult],
    kinematics: KinematicComparison | None,
    included_trials: list[str],
) -> str:
    excluded = [q.trial_id for q in qc_results if q.trial_id not in included_trials]
    lines = [
        "# Clinical Gait Summary (Demo — Not for clinical use)",
        "",
        "## Session",
        f"- **Patient ID:** {meta.get('patient_id', 'N/A')} (synthetic)",
        f"- **Age:** {meta.get('age_years', 'N/A')} years",
        f"- **Condition (label):** {meta.get('condition', 'N/A').replace('_', ' ')}",
        f"- **Assessment date:** {meta.get('assessment_date', 'N/A')}",
        f"- **Walking condition:** {meta.get('selected_condition', 'barefoot')}",
        "",
        "## Trials included in analysis",
    ]
    if included_trials:
        for t in included_trials:
            lines.append(f"- {t}")
    else:
        lines.append("- None (all trials failed QC)")

    lines.append("")
    lines.append("## Trials excluded (QC)")
    if excluded:
        for q in qc_results:
            if q.trial_id in excluded:
                lines.append(f"- **{q.trial_id}:** {'; '.join(q.flags)}")
                for action in q.suggested_actions:
                    lines.append(f"  - *Suggested action:* {action}")
    else:
        lines.append("- None")

    lines.extend(["", "## Kinematic observations (for clinician interpretation)"])
    if kinematics is not None and included_trials:
        direction = "reduced" if kinematics.peak_flexion_diff < 0 else "increased"
        lines.append(
            f"- Observed ensemble peak knee flexion is **{abs(kinematics.peak_flexion_diff):.1f}°** "
            f"**{direction}** relative to illustrative normative peak."
        )
        lines.append(f"- Cycle RMSE vs norm mean: **{kinematics.rmse_deg:.1f}°**.")
        for flag in kinematics.deviation_flags:
            lines.append(f"- {flag}")
        if not kinematics.deviation_flags:
            lines.append("- No sustained deviation beyond illustrative ±2 SD band.")
    else:
        lines.append("- Insufficient QC-passed trials for kinematic summary.")

    lines.extend(
        [
            "",
            "## Suggested follow-up in MAC pipeline",
            "- Verify gait events in Visual3D Signals & Events if curves appear atypical.",
            "- Compare barefoot vs orthotic conditions when applicable.",
            "- Present findings with physiotherapy and surgical team for shared decision-making.",
            "",
            "## Limitations",
            "- Synthetic demonstration data only; thresholds are illustrative.",
            "- Not validated against GOS-ICH or MAC internal normative databases.",
            "- Does not replace Cortex / Visual3D / MATLAB clinical reporting.",
        ]
    )
    return "\n".join(lines)
