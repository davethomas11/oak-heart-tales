# combat_start_screens.py
import sys
import time
import re
import html
from typing import Iterable, Optional, List, Dict

# ========= ANSI + Layout Helpers (ANSI-safe) =========
ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')  # CSI ... final letter


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub('', s or '')


def visible_len(s: str) -> int:
    return len(strip_ansi(s or ''))


def pad_line_vis(s: str, w: int) -> str:
    """Pad/truncate a possibly-colored string to visible width w."""
    if s is None:
        s = ""
    out, vis, i = [], 0, 0
    while i < len(s) and vis < w:
        if s[i] == "\x1b":
            m = ANSI_RE.match(s, i)
            if m:
                out.append(m.group(0))
                i = m.end()
                continue
        out.append(s[i])
        vis += 1
        i += 1
    if vis < w:
        out.append(" " * (w - vis))
    return "".join(out)


def center_line(s: str, w: int) -> str:
    vl = visible_len(s)
    if vl > w:
        return pad_line_vis(s, w)
    pad = w - vl
    return (" " * (pad // 2)) + s + (" " * (pad - pad // 2))


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def clamp(n, lo, hi):
    return max(lo, min(hi, n))


# ========= Colors =========
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDER = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    GRAY = "\033[90m"
    BR_RED = "\033[91m"
    BR_GREEN = "\033[92m"
    BR_YELLOW = "\033[93m"
    BR_BLUE = "\033[94m"
    BR_MAGENTA = "\033[95m"
    BR_CYAN = "\033[96m"
    BR_WHITE = "\033[97m"


def color(s: str, *codes: str, end_reset=True) -> str:
    if not codes:
        return s
    seq = "".join(codes)
    return f"{seq}{s}{C.RESET if end_reset else ''}"


# ========= Panels (ANSI-safe borders) =========
def draw_panel(title: str, lines: List[str], width: int,
               title_color=(C.BOLD, C.BR_GREEN)) -> List[str]:
    inner_w = width - 2
    title_str = f" {title} "
    if title_color:
        title_str = color(title_str, *title_color)
    fill_count = max(0, inner_w - visible_len(title_str))
    top_body = pad_line_vis(title_str + ("─" * fill_count), inner_w)
    top = "┌" + top_body + "┐"
    body = ["│" + pad_line_vis(line, inner_w) + "│" for line in lines]
    bottom = "└" + ("─" * inner_w) + "┘"
    return [top] + body + [bottom]


def print_block(lines: Iterable[str]):
    for ln in lines:
        sys.stdout.write(ln + "\n")
    sys.stdout.flush()


# ========= Generic Animation Engine =========
def animate(
        text: str,
        style: str = "typewriter",
        color_code: Optional[str] = C.BR_WHITE,
        speed: float = 0.03,
        width: Optional[int] = None,
        loops: int = 1,
        pad: int = 0
):
    """
    Styles:
      - typewriter : prints characters one-by-one
      - blink      : toggles visibility
      - pulse      : brightness pulsing (dim/bold)
      - slide_in   : slides from left into centered position
      - reveal_box : draws a box around text then reveals the text
      - marquee    : scrolls horizontally across width
      - flicker    : subtle on/off flicker for alert/glow
    """
    base = text if color_code is None else color(text, color_code)
    w = width or 80

    if style == "typewriter":
        for ch in base:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write("\n");
        sys.stdout.flush()

    elif style == "blink":
        for _ in range(clamp(loops, 1, 50)):
            sys.stdout.write(base + "\r");
            sys.stdout.flush()
            time.sleep(speed * 6)
            sys.stdout.write(" " * visible_len(base) + "\r");
            sys.stdout.flush()
            time.sleep(speed * 6)
        sys.stdout.write(base + "\n");
        sys.stdout.flush()

    elif style == "pulse":
        plain = strip_ansi(base)
        for _ in range(clamp(loops, 1, 50)):
            sys.stdout.write(color(plain, C.DIM, color_code) + "\r");
            sys.stdout.flush()
            time.sleep(speed * 3)
            sys.stdout.write(color(plain, C.BOLD, color_code) + "\r");
            sys.stdout.flush()
            time.sleep(speed * 3)
        sys.stdout.write(color(plain, color_code) + "\n");
        sys.stdout.flush()

    elif style == "slide_in":
        plain = strip_ansi(base)
        target = center_line(plain, w)
        for i in range(w):
            frame = (" " * i) + plain
            sys.stdout.write(color(pad_line_vis(frame, w), color_code) + "\r")
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write(color(target, color_code) + "\n");
        sys.stdout.flush()

    elif style == "reveal_box":
        plain = strip_ansi(base)
        inner_w = max(10, visible_len(plain) + 2)
        lines = [
            "┌" + "─" * inner_w + "┐",
            "│" + " " * inner_w + "│",
            "│" + pad_line_vis(center_line(plain, inner_w), inner_w) + "│",
            "│" + " " * inner_w + "│",
            "└" + "─" * inner_w + "┘",
        ]
        left_pad = max(0, (w - (inner_w + 2)) // 2)
        for idx, ln in enumerate(lines):
            sys.stdout.write(" " * left_pad + color(ln, color_code) + "\n")
            sys.stdout.flush()
            time.sleep(speed * (1.5 if idx == 0 else 0.5))

    elif style == "marquee":
        plain = strip_ansi(base)
        padding = " " * pad
        span = padding + plain + padding
        for _ in range(clamp(loops, 1, 50)):
            for i in range(len(span)):
                vis = span[i:i + w]
                sys.stdout.write(color(pad_line_vis(vis, w), color_code) + "\r")
                sys.stdout.flush()
                time.sleep(speed)
        sys.stdout.write("\n");
        sys.stdout.flush()

    elif style == "flicker":
        plain = strip_ansi(base)
        import random
        for _ in range(clamp(loops, 1, 40)):
            bright = random.random() < 0.65
            code = C.BR_YELLOW if bright else C.YELLOW
            sys.stdout.write(color(plain, code) + "\r");
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write(color(plain, C.BR_YELLOW) + "\n");
        sys.stdout.flush()

    else:
        sys.stdout.write(base + "\n");
        sys.stdout.flush()


# ========= Bars / Stat Formatting =========
def hbar(label: str, cur: int, mx: int, bar_w: int = 24, good: bool = False) -> str:
    cur = clamp(cur or 0, 0, mx or 1)
    filled = int((cur / (mx or 1)) * bar_w)
    empty = bar_w - filled
    fill_char = "█"
    empty_char = "░"
    fill = fill_char * filled
    empty = empty_char * empty
    fill_col = C.BR_RED if not good else C.BR_GREEN
    bar = color(fill, fill_col) + color(empty, C.GRAY)
    left = pad_line_vis(f"{label}: {cur}/{mx}", 15)
    bar = pad_line_vis(bar, bar_w)
    return f"{left} {bar}"


def format_stat_line(name: str, val: int, color_code: str = C.BR_WHITE, width: int = 90) -> str:
    s = f"{name}: {val}"
    return center_line(color(s, color_code), width - 2)


# ========= ASCII Art Helpers =========
def normalize_ascii_art(s: str) -> List[str]:
    """Unescape HTML entities (&gt;, &lt;, etc.) and split into lines."""
    if not s:
        return ["(no art)"]
    un = html.unescape(s)
    return un.splitlines()


def tint_ascii_lines(lines: List[str], tint: str = C.BR_GREEN) -> List[str]:
    return [color(line, tint) for line in lines]


# ========= Combat Start Screen =========
def combat_start_screen(payload: Dict, width: int = 90):
    """
    Payload example (ENTERED_COMBAT):
    {
        "position": (x, y),
        "location": "Oakheart Road",
        "enemy_name": "Wolf",
        "enemy_ascii_art": "/\\_/\\\n( o.o )\n > ^ <",
        "enemy_level": 3,
        "enemy_hp": 12,
        "enemy_max_hp": 12,
        "enemy_attack": 5,
        "enemy_defense": 2
    }
    """
    clear_screen()

    enemy_name = payload.get("enemy_name", "Unknown")
    location = payload.get("location", "Unknown")
    lvl = int(payload.get("enemy_level", 1))
    hp = int(payload.get("enemy_hp", 1))
    hp_max = int(payload.get("enemy_max_hp", max(1, hp)))
    atk = int(payload.get("enemy_attack", 0))
    df = int(payload.get("enemy_defense", 0))

    # Header: red alert + location
    header = [
        center_line(color("ENEMY APPROACHES!", C.BOLD, C.BR_RED), width - 2),
        center_line(color(f"Location: {location}", C.GRAY), width - 2),
        center_line(color(f"Enemy: {enemy_name} (Lv {lvl})", C.BR_WHITE), width - 2),
    ]
    print_block(draw_panel("Combat Start", header, width, title_color=(C.BOLD, C.BR_RED)))

    # Dramatic intro box
    animate("Prepare yourself...", style="reveal_box", color_code=C.BR_YELLOW, speed=0.03, width=width)
    sys.stdout.write("\a")  # subtle bell (may be ignored by some terminals)

    # Enemy ASCII art
    art_lines = normalize_ascii_art(payload.get("enemy_ascii_art", ""))
    art_lines = tint_ascii_lines(art_lines, tint=C.BR_GREEN)
    art_centered = [center_line(ln, width - 2) for ln in art_lines]
    print_block(draw_panel("Foe", art_centered, width, title_color=(C.BOLD, C.BR_GREEN)))

    # Alert scan effect (a quick red sweep line under art)
    scan_text = center_line("▼ scanning...", width - 2)
    animate(scan_text, style="marquee", color_code=C.BR_RED, speed=0.01, width=width, loops=1, pad=8)

    # Stats panel
    stats_lines = [
        center_line(color(hbar("HP", hp, hp_max, bar_w=30, good=False), C.BR_WHITE), width - 2),
        format_stat_line("Attack", atk, color_code=C.BR_YELLOW, width=width),
        format_stat_line("Defense", df, color_code=C.BR_CYAN, width=width),
    ]
    print_block(draw_panel("Enemy Stats", stats_lines, width, title_color=(C.BOLD, C.BR_GREEN)))


# ========= Dispatcher from your event manager =========
def show_combat_start_event(payload: dict, width: int = 90):
    """
    Call this from your ENTERED_COMBAT event listener.
    """
    combat_start_screen(payload, width=width)


# ========= Optional: simple blocking key wait =========
def wait_keypress(prompt: str = "", color_code: Optional[str] = C.BR_WHITE):
    if prompt:
        animate(prompt, style="typewriter", color_code=color_code, speed=0.02)
    try:
        input()
    except KeyboardInterrupt:
        pass


# ========= Demo (run directly) =========
if __name__ == "__main__":
    demo_payload = {
        "position": (12, 7),
        "location": "Oakheart Road",
        "enemy_name": "Wolf",
        "enemy_ascii_art": "/\\_/\\\n( o.o )\n > ^ <",
        "enemy_level": 3,
        "enemy_hp": 12,
        "enemy_max_hp": 12,
        "enemy_attack": 5,
        "enemy_defense": 2
    }
    show_combat_start_event(demo_payload, width=90)
    wait_keypress("Press Enter to continue...")
