from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def save_json(data: Dict[str, Any], directory: str, base_name: str) -> str:
    ensure_dir(directory)
    out_path = os.path.join(directory, f"{base_name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return out_path


def save_csv(rows: List[Dict[str, Any]], directory: str, base_name: str) -> str:
    ensure_dir(directory)
    out_path = os.path.join(directory, f"{base_name}.csv")
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    return out_path


