"""MAC-Lite: Streamlit demo for pediatric gait QC and reporting."""

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import run_session

DATA_DIR = ROOT / "data"


@st.cache_data
def cached_run_session(included: tuple[str, ...] | None = None):
    ids = list(included) if included is not None else None
    return run_session(DATA_DIR, included_trial_ids=ids)

st.set_page_config(
    page_title="MAC-Lite | Gait QC & Report",
    page_icon="🚶",
    layout="wide",
)

st.title("MAC-Lite: Pediatric Gait QC & Report Assistant")
st.caption(
    "Demonstration prototype for Holland Bloorview Motion Analysis Centre workflows. "
    "**Synthetic data only — not for clinical use.**"
)

with st.sidebar:
    st.header("Session")
    st.selectbox("Walking condition", ["barefoot", "with_AFO"])
    st.info(
        "Post-export automation layer: assumes time-series already processed "
        "(e.g. from Visual3D). Focus = QC, norm comparison, summary."
    )

initial = cached_run_session()
qc_initial = initial["qc_results"]
default_include = [q.trial_id for q in qc_initial if q.passed]

st.markdown(
    """
Holland Bloorview’s **Motion Analysis Centre** combines **kinematics**, **EMG**, and **kinetics**
to support pediatric surgical and rehabilitation decisions. This demo mirrors **QC → cycle normalization →
norm comparison → clinical summary** using bundled synthetic trials.
"""
)

st.subheader("Include trials in report")
include_selection: list[str] = []
cols = st.columns(2)
for i, q in enumerate(qc_initial):
    with cols[i % 2]:
        if st.checkbox(
            f"{q.trial_id} — {'PASS' if q.passed else 'FAIL'}",
            value=q.trial_id in default_include,
            help="; ".join(q.flags) if q.flags else "All QC checks passed",
            key=f"include_{q.trial_id}",
        ):
            include_selection.append(q.trial_id)

results = cached_run_session(
    tuple(include_selection) if include_selection else tuple()
)
qc_results = results["qc_results"]

tab_qc, tab_plot, tab_summary, tab_docs = st.tabs(
    ["QC Dashboard", "Kinematics Report", "Clinical Summary", "Pipeline Docs"]
)

with tab_qc:
    st.subheader("Trial quality control")
    rows = []
    for q in qc_results:
        rows.append(
            {
                "Trial": q.trial_id,
                "Status": "PASS" if q.passed else "FAIL",
                "In report": "Yes" if q.trial_id in results["included_trials"] else "No",
                "Flags": "; ".join(q.flags) if q.flags else "—",
                "Marker mean": q.metrics.get("marker_mean"),
                "Force SNR": q.metrics.get("force_snr"),
                "EMG baseline σ": q.metrics.get("emg_baseline_std_uV"),
                "GRF peaks": q.metrics.get("grf_peaks"),
            }
        )
    st.dataframe(rows, width="stretch")

    for q in qc_results:
        if q.suggested_actions:
            with st.expander(f"Suggested actions — {q.trial_id}"):
                for action in q.suggested_actions:
                    st.markdown(f"- {action}")

with tab_plot:
    st.subheader("Sagittal knee flexion (0–100% gait cycle)")
    if results["figure"] is not None:
        st.pyplot(results["figure"], clear_figure=True)
        k = results["kinematics"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Peak flexion vs norm", f"{k.peak_flexion_diff:+.1f}°")
        c2.metric("RMSE vs norm", f"{k.rmse_deg:.1f}°")
        c3.metric("Trials averaged", len(results["included_trials"]))
    else:
        st.warning("No trials selected. Include at least one QC-passed trial.")

with tab_summary:
    st.subheader("Clinical summary (demo)")
    st.markdown(results["summary_md"])
    st.download_button(
        "Download summary.md",
        data=results["summary_md"],
        file_name="gait_summary_demo.md",
        mime="text/markdown",
    )

with tab_docs:
    st.subheader("Pipeline architecture")
    st.markdown(
        """
| Module | Role |
|--------|------|
| `src/io.py` | Load session metadata and trial exports |
| `src/qc.py` | Marker, force, EMG, trial-length checks |
| `src/events.py` | Heel-strike detection; resample cycles to 101 points |
| `src/kinematics.py` | Ensemble average; compare to normative band |
| `src/report.py` | Plots and markdown summary |
| `src/pipeline.py` | Single entry point: `run_session()` |

**Gait conventions:** 0% = heel strike; shaded band = illustrative pediatric norm ±1 SD.

**Run:** `pip install -r requirements.txt` then `streamlit run app.py`
"""
    )
