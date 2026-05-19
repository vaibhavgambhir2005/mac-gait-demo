# 10-minute interview walkthrough

## Before the interview

1. `pip install -r requirements.txt`
2. `python scripts/generate_synthetic_data.py`
3. `streamlit run app.py` — confirm it opens in the browser
4. Optional: record a 30-second screen capture as backup

## Script

| Time | Tab | What to say |
|------|-----|-------------|
| 0:00 | Intro | "MAC combines kinematics, EMG, and kinetics for pediatric surgical and rehab decisions. I built a post-export QC and reporting layer aligned with that workflow—not replacing Visual3D." |
| 1:00 | Repo / Docs | "Code is split into io, qc, events, kinematics, report, and pipeline so it's testable like a clinical pipeline." |
| 2:00 | QC | "Trial 3 fails marker dropout—like mocap occlusion. Trial 4 fails force noise. We exclude them before averaging gait cycles." |
| 4:00 | Kinematics | "Cycles are normalized 0–100% with heel strike at 0%. The band is illustrative pediatric norm ±1 SD. The patient curve is for discussion, not diagnosis." |
| 7:00 | Summary | "Auto-generated bullets: included trials, exclusions, kinematic observations, and suggested MAC follow-ups." |
| 9:00 | Close | "Next steps: ingest real Visual3D exports, validate thresholds with MAC engineers, deploy on-prem without PHI in the cloud." |

## Likely questions

- **Why Python?** Rapid QC automation; happy to work in MATLAB where the lab already has tools.
- **Validation?** Demo only; would compare to clinician-reviewed reports on de-identified sessions.
- **PHI?** Synthetic data only; production stays on hospital network.
