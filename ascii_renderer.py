import os
from typing import Optional
from models import Enemy
from world import Tile


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ROOMS_DIR = os.path.join(DATA_DIR, "rooms")
ENEMIES_FILE = os.path.join(DATA_DIR, "enemies.json")


def _read_text_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().rstrip("\n")
    except FileNotFoundError:
        return None


def _box(text: str, title: Optional[str] = None) -> str:
    lines = text.splitlines() if text else []
    width = max([len(l) for l in lines] + ([len(title)] if title else [0, 0]))
    border = "+" + "-" * (width + 2) + "+"
    out = [border]
    if title:
        out.append("| " + title.ljust(width) + " |")
        out.append("| " + ("-" * width) + " |")
    for l in lines:
        out.append("| " + l.ljust(width) + " |")
    out.append(border)
    return "\n".join(out)


def render_room(tile: Tile) -> str:
    # Prefer an explicit ascii filename in the tile; else try normalized name
    fname = tile.ascii
    if not fname:
        fname = tile.name.lower().replace(" ", "_") + ".txt"
    path = os.path.join(ROOMS_DIR, fname)
    art = _read_text_file(path)
    if art:
        return art
    # Fallback box
    return _box("", title=tile.name)
