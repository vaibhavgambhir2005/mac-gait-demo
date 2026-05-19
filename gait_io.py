"""Load session metadata and trial CSV exports."""

from dataclasses import dataclass
from pathlib import Path
import json

import pandas as pd


@dataclass
class SessionData:
    meta: dict
    trial_paths: list[Path]
    normative_path: Path
    data_dir: Path


def load_session(data_dir: str | Path) -> SessionData:
    root = Path(data_dir)
    meta_path = root / "session_meta.json"
    with meta_path.open(encoding="utf-8") as f:
        meta = json.load(f)

    trials_dir = root / "trials"
    if trials_dir.is_dir():
        trial_paths = sorted(trials_dir.glob("*.csv"))
    else:
        trial_paths = sorted(root.glob("trial_*.csv"))

    normative_nested = root / "normative" / "knee_flexion_norm.csv"
    normative_flat = root / "knee_flexion_norm.csv"
    normative_path = normative_nested if normative_nested.exists() else normative_flat

    return SessionData(
        meta=meta,
        trial_paths=trial_paths,
        normative_path=normative_path,
        data_dir=root,
    )


def load_trial(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)
