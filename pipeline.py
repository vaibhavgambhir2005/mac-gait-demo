"""End-to-end session processing (flat layout for GitHub / Streamlit Cloud)."""

from pathlib import Path

import pandas as pd

from gait_io import load_session, load_trial
from kinematics import load_normative, process_trials
from qc import run_qc
from report import generate_clinical_summary, plot_knee_flexion


def run_session(data_dir: str | Path, included_trial_ids: list[str] | None = None) -> dict:
    session = load_session(data_dir)
    qc_results = []
    trials: dict[str, pd.DataFrame] = {}

    for path in session.trial_paths:
        df = load_trial(path)
        qc = run_qc(df)
        qc_results.append(qc)
        trials[qc.trial_id] = df

    if included_trial_ids is None:
        included = [q.trial_id for q in qc_results if q.passed]
    else:
        included = [t for t in included_trial_ids if t in trials]

    passed_trials = {tid: trials[tid] for tid in included}
    kinematics = None
    figure = None
    norms = load_normative(session.normative_path)

    if passed_trials:
        kinematics = process_trials(passed_trials, session.normative_path)
        figure = plot_knee_flexion(kinematics, norms)

    summary = generate_clinical_summary(
        session.meta, qc_results, kinematics, included
    )

    return {
        "meta": session.meta,
        "qc_results": qc_results,
        "trials": trials,
        "included_trials": included,
        "kinematics": kinematics,
        "norms": norms,
        "figure": figure,
        "summary_md": summary,
    }
