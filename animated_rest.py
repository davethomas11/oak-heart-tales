
# rest_screens.py
import sys
import time
import re
import random
from typing import Iterable, Optional, List

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
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"

    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    GRAY    = "\033[90m"
    BR_RED  = "\033[91m"
    BR_GREEN= "\033[92m"
    BR_YELLOW="\033[93m"
    BR_BLUE = "\033[94m"
    BR_MAGENTA="\033[95m"
    BR_CYAN = "\033[96m"
    BR_WHITE="\033[97m"

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
      - flicker    : subtle on/off flicker (campfire / lantern vibe)
    """
    base = text if color_code is None else color(text, color_code)
    w = width or 80

    if style == "typewriter":
        for ch in base:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write("\n"); sys.stdout.flush()

    elif style == "blink":
        for _ in range(clamp(loops, 1, 50)):
            sys.stdout.write(base + "\r"); sys.stdout.flush()
            time.sleep(speed * 6)
            sys.stdout.write(" " * visible_len(base) + "\r"); sys.stdout.flush()
            time.sleep(speed * 6)
        sys.stdout.write(base + "\n"); sys.stdout.flush()

    elif style == "pulse":
        plain = strip_ansi(base)
        for _ in range(clamp(loops, 1, 50)):
            sys.stdout.write(color(plain, C.DIM, color_code) + "\r"); sys.stdout.flush()
            time.sleep(speed * 3)
            sys.stdout.write(color(plain, C.BOLD, color_code) + "\r"); sys.stdout.flush()
            time.sleep(speed * 3)
        sys.stdout.write(color(plain, color_code) + "\n"); sys.stdout.flush()

    elif style == "slide_in":
        plain = strip_ansi(base)
        target = center_line(plain, w)
        for i in range(w):
            frame = (" " * i) + plain
            sys.stdout.write(color(pad_line_vis(frame, w), color_code) + "\r")
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write(color(target, color_code) + "\n"); sys.stdout.flush()

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

    elif style == "flicker":
        # subtle visibility flicker (like candle/campfire)
        plain = strip_ansi(base)
        for _ in range(clamp(loops, 1, 40)):
            bright = random.random() < 0.65
            code = C.BR_YELLOW if bright else C.YELLOW
            sys.stdout.write(color(plain, code) + "\r"); sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write(color(plain, C.BR_YELLOW) + "\n"); sys.stdout.flush()

    else:
        sys.stdout.write(base + "\n"); sys.stdout.flush()

# ========= ASCII Art (centered) =========
def campfire_art(width: int) -> List[str]:
    art = [
        "   (  )   ",
        "   )  (   ",
        "  (    )  ",
        "   )  (   ",
        "  /____\\  ",
        "   \\__/   ",
        "    ||    ",
        "    ||    ",
    ]
    return [center_line(line, width - 2) for line in art]

def moon_art(width: int) -> List[str]:
    art = [
        "      _.._       ",
        "    .`    `.     ",
        "   /  .--.  \\    ",
        "  |  (____)  |   ",
        "   \\        /    ",
        "    `.__..`      ",
    ]
    return [center_line(line, width - 2) for line in art]

# ========= Rest Screens =========
def village_rest_screen(healed: int, received_potion: bool, width: int = 90):
    clear_screen()

    # Calm header
    header = [
        center_line(color("You rest at the village.", C.BR_WHITE), width - 2),
        center_line(color(f"HP restored: +{healed}", C.BR_GREEN), width - 2),
        center_line(color(
            "The healer gifts you a potion." if received_potion else "You wake renewed.",
            C.BR_YELLOW if received_potion else C.GRAY
        ), width - 2),
    ]
    print_block(draw_panel("Rest", header, width, title_color=(C.BOLD, C.BR_GREEN)))

    # Moon + campfire vibe
    print_block(draw_panel("Night Sky", moon_art(width), width, title_color=(C.BOLD, C.BR_GREEN)))
    # Flicker campfire for ambience
    camp = draw_panel("Hearth", [*campfire_art(width)], width, title_color=(C.BOLD, C.BR_GREEN))
    for ln in camp:
        # flicker each line slightly
        bright = random.random() < 0.7
        code = C.BR_YELLOW if bright else C.YELLOW
        sys.stdout.write(color(ln, code) + "\n")
        sys.stdout.flush()
        time.sleep(0.03)

    # Gentle messages
    animate("Zzz...", style="pulse", color_code=C.GRAY, speed=0.08, loops=3, width=width)
    animate("Body and spirit mended.", style="typewriter", color_code=C.BR_GREEN, speed=0.02)
    if received_potion:
        animate("+1 Potion added to your satchel.", style="typewriter", color_code=C.BR_YELLOW, speed=0.02)

def wild_rest_screen(healed: int, width: int = 90):
    clear_screen()

    header = [
        center_line(color("You rest cautiously.", C.BR_WHITE), width - 2),
        center_line(color(f"HP restored: +{healed}", C.BR_GREEN), width - 2),
        center_line(color("The wild is quiet... for now.", C.GRAY), width - 2),
    ]
    print_block(draw_panel("Rest (Wilderness)", header, width, title_color=(C.BOLD, C.BR_GREEN)))

    # Low-key campfire flicker
    flicker_text = center_line("A small fire crackles softly.", width - 2)
    animate(flicker_text, style="flicker", color_code=C.YELLOW, speed=0.05, loops=15, width=width)

    animate("Zzz...", style="pulse", color_code=C.GRAY, speed=0.08, loops=2, width=width)
    animate("You rise alert and recovered.", style="typewriter", color_code=C.BR_WHITE, speed=0.02)

def rest_interrupted_screen(enemy_name: str, width: int = 90):
    clear_screen()

    # Sudden red alert
    print_block(draw_panel("Alert", [
        center_line(color("AMBUSH!", C.BOLD, C.BR_RED), width - 2),
        center_line(color(f"{enemy_name} attacks while you sleep!", C.BR_WHITE), width - 2),
    ], width, title_color=(C.BOLD, C.BR_RED)))

    animate("Armor scrambles on. Weapons drawn.", style="typewriter", color_code=C.BR_YELLOW, speed=0.02)
    animate(">>> Entering combat... <<<", style="reveal_box", color_code=C.BR_RED, speed=0.03, width=width)
    # hand control back to your combat intro / loop

# ========= Dispatcher from your REST events =========
def show_rest_event(payload: dict, width: int = 90):
    """
    Handles RESTED payloads like:
      Village: {"healed": int, "received_potion": bool, "type": "village_rest"}
      Wild:    {"healed": int, "type": "wild_rest"}

    And REST_INTERRUPTED payloads like:
      {"position": (x,y), "enemy_name": "Wolf"}
    """
    t = payload.get("type")
    if t == "village_rest":
        healed = int(payload.get("healed", 0))
        received = bool(payload.get("received_potion", False))
        village_rest_screen(healed, received, width=width)
    elif t == "wild_rest":
        healed = int(payload.get("healed", 0))
        wild_rest_screen(healed, width=width)
    else:
        # REST_INTERRUPTED (no 'type' in your snippet)
        enemy = payload.get("enemy_name", "Unknown")
        rest_interrupted_screen(enemy, width=width)

# ========= Optional: simple key wait =========
def wait_keypress(prompt: str = "", color_code: Optional[str] = C.BR_WHITE):
    if prompt:
        animate(prompt, style="typewriter", color_code=code, speed=0.02)
    try:
        input()
    except KeyboardInterrupt:
        pass

# ========= Demo (run directly) =========
if __name__ == "__main__":
    village = {"healed": 18, "received_potion": True, "type": "village_rest"}
    wild    = {"healed": 9, "type": "wild_rest"}
    ambush  = {"enemy_name": "Night Stalker"}  # REST_INTERRUPTED

    show_rest_event(village, width=90); time.sleep(0.5)
    show_rest_event(wild, width=90);    time.sleep(0.5)
    show_rest_event(ambush, width=90);  time.sleep(0.5)
