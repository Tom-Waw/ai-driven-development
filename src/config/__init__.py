from pathlib import Path

import yaml


def load_config(filename: str) -> dict | None:
    path = Path(__file__).parent / filename

    with open(path, "r") as f:
        return yaml.safe_load(f)
