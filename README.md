# MAC-Lite: Pediatric Gait QC & Report Assistant

Demonstration prototype aligned with [Holland Bloorview Motion Analysis Centre](https://hollandbloorview.ca/services/programs-services/motion-analysis-centre) clinical gait workflows: **quality control → cycle-normalized kinematics → normative comparison → summary for clinical review**.

> **Not for clinical use.** Synthetic data only. Does not replace Cortex, Visual3D, MATLAB, or Theia3D.

## Quick start

```bash
cd mac
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
streamlit run app.py
```

## What it demonstrates

| MAC responsibility | This prototype |
|------------------|----------------|
| Data screening | Per-trial QC: marker dropout, force SNR, EMG baseline, step count |
| Reporting & visualization | Knee flexion vs illustrative norm band (0–100% gait) |
| Report automation | Markdown summary with included/excluded trials |
| Documentation | Modular `src/` pipeline + README |

## Project structure

```
app.py              # Streamlit UI
src/
  io.py             # Load trials and metadata
  qc.py             # Quality checks
  events.py         # Heel-strike detection, cycle normalization
  kinematics.py     # Ensemble + norm comparison
  report.py         # Plots and clinical summary
  pipeline.py       # run_session() entry point
data/               # Synthetic session (regenerate via scripts/)
```

## Demo narrative (≈10 min)

1. **QC Dashboard** — `trial_03` fails marker continuity; `trial_04` fails force noise.
2. **Kinematics** — Ensemble curve vs norm ±1 SD (heel strike = 0%).
3. **Summary** — Download rounds-style bullets; emphasize clinician interpretation.

## About the author

_Add your resume highlights here after uploading to this folder._

Suggested talking points:

- Python for QC automation and rapid reporting layers on top of lab exports
- Interest in pediatric biomechanics and interdisciplinary clinical collaboration
- Eager to learn Cortex / Visual3D / MATLAB workflows on the job

## Disclaimers

- Normative curves are **illustrative**, not GOS-ICH or MAC-validated references.
- Event detection uses simplified heuristics; clinical workflows verify events in Visual3D.
- No PHI; production deployment would require hospital network and validation studies.
