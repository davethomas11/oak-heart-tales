import json
import os
from typing import Optional

SAVE_FILE = os.path.join(os.path.dirname(__file__), "save.json")


def save_game(game: dict, path: str) -> None:
    data = game
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_game(path: str) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return None
    except Exception:
        return None
