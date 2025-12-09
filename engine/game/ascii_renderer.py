from .world import Tile


def _box(text: str, title: str = None) -> str:
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


def render_room(tile: Tile, text_loader) -> str:
    # Prefer an explicit ascii filename in the tile; else try normalized name
    try:
        fname = tile.ascii
        if not fname:
            fname = tile.name.lower().replace(" ", "_") + ".txt"
        art = text_loader.load(fname)
        if art:
            return art
        # Fallback box
        return _box('[ --- ]', title=tile.name)
    except:
        return _box('[ --- ]', title=tile.name)
