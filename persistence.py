import json
import os
from typing import Optional

from game import Game


SAVE_FILE = os.path.join(os.path.dirname(__file__), "save.json")


def save_game(game: Game, path: str) -> None:
    data = game.to_dict()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_game(path: str) -> Optional[Game]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Game.from_dict(data)
    except FileNotFoundError:
        return None
    except Exception:
        return None
