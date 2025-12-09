
# animated_screens.py
import sys
import time
import re
from typing import Iterable, Optional, Tuple, Callable, List

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
    out = []
    vis = 0
    i = 0
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
    UNDER   = "\033[4m"

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
def draw_panel(title: str, lines: List[str], width: int, title_color=(C.BOLD, C.BR_YELLOW)) -> List[str]:
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
    Render animated text in various styles.

    Styles:
      - typewriter : prints characters one-by-one
      - blink      : toggles visibility
      - marquee    : scrolls horizontally across width
      - slide_in   : slides from left into centered position
      - pulse      : brightness pulsing (bold/dim)
      - reveal_box : draws a box around text then reveals the text

    Args:
      text       : string to animate (ansi allowed)
      color_code : ANSI color to apply (None keeps original)
      speed      : base delay in seconds
      width      : required for marquee/centering; defaults to terminal guess
      loops      : for cyclical styles (blink/marquee/pulse)
      pad        : extra spaces surrounding text for marquee/slide
    """
    s = color(text, color_code) if color_code else text
    w = width or 80

    if style == "typewriter":
        for ch in s:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write("\n")
        sys.stdout.flush()

    elif style == "blink":
        for _ in range(clamp(loops, 1, 50)):
            sys.stdout.write(s + "\r")
            sys.stdout.flush()
            time.sleep(speed * 6)
            sys.stdout.write(" " * visible_len(s) + "\r")
            sys.stdout.flush()
            time.sleep(speed * 6)
        sys.stdout.write(s + "\n")
        sys.stdout.flush()

    elif style == "marquee":
        padding = " " * pad
        base = padding + strip_ansi(s) + padding
        span = base
        # we'll re-apply color to the visible slice
        for _ in range(clamp(loops, 1, 200)):
            for i in range(len(span)):
                vis = span[i:i + w]
                sys.stdout.write(color(pad_line_vis(vis, w), color_code) + "\r")
                sys.stdout.flush()
                time.sleep(speed)
        sys.stdout.write("\n")
        sys.stdout.flush()

    elif style == "slide_in":
        # slide from left into centered position
        target = center_line(strip_ansi(s), w)
        for i in range(w):
            frame = (" " * i) + strip_ansi(s)
            frame = pad_line_vis(frame, w)
            sys.stdout.write(color(frame, color_code) + "\r")
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write(color(target, color_code) + "\n")
        sys.stdout.flush()

    elif style == "pulse":
        for _ in range(clamp(loops, 1, 50)):
            sys.stdout.write(color(strip_ansi(s), C.DIM, color_code) + "\r")
            sys.stdout.flush()
            time.sleep(speed * 3)
            sys.stdout.write(color(strip_ansi(s), C.BOLD, color_code) + "\r")
            sys.stdout.flush()
            time.sleep(speed * 3)
        sys.stdout.write(color(strip_ansi(s), color_code) + "\n")
        sys.stdout.flush()

    elif style == "reveal_box":
        # draw a centered box around the text, then populate text
        content = strip_ansi(s)
        inner_w = max(10, visible_len(content) + 2)
        lines = [
            "┌" + "─" * inner_w + "┐",
            "│" + " " * inner_w + "│",
            "│" + pad_line_vis(center_line(content, inner_w), inner_w) + "│",
            "│" + " " * inner_w + "│",
            "└" + "─" * inner_w + "┘",
            ]
        left_pad = max(0, (w - (inner_w + 2)) // 2)
        for idx, ln in enumerate(lines):
            sys.stdout.write(" " * left_pad + color(ln, color_code) + "\n")
            sys.stdout.flush()
            time.sleep(speed * (1.5 if idx == 0 else 0.5))
    else:
        # default: just print
        sys.stdout.write(s + "\n")
        sys.stdout.flush()

# ========= High-level Screens =========
def victory_screen(enemy_name: str, gold: int, xp: int, width: int = 90):
    clear_screen()

    # Title panel
    title_lines = [
        center_line(color("VICTORY ACHIEVED", C.BOLD, C.BR_GREEN), width - 2),
        center_line(color(f"You defeated {enemy_name}!", C.BR_WHITE), width - 2),
    ]
    print_block(draw_panel("Battle End", title_lines, width))

    # Animated summary stats
    time.sleep(0.3)
    animate("Rewards:", style="typewriter", color_code=C.BR_YELLOW, speed=0.02)
    animate(f"Gold Looted: {gold}", style="typewriter", color_code=C.BR_GREEN, speed=0.02)
    animate(f"XP Gained: {xp}", style="typewriter", color_code=C.BR_CYAN, speed=0.02)

    # Flair: pulse and marquee line
    animate("Well fought, hero!", style="pulse", color_code=C.BR_WHITE, speed=0.05, loops=4)
    animate(">>> Press any key to continue <<<", style="marquee", color_code=C.BR_YELLOW, speed=0.01, width=width, loops=1, pad=10)

def level_up_screen(new_level: int, width: int = 90):
    clear_screen()

    # Explosion of stars using slide_in + pulse
    animate("★ ★ ★ ★ ★", style="slide_in", color_code=C.BR_YELLOW, speed=0.01, width=width)
    animate("LEVEL UP!", style="reveal_box", color_code=C.BR_GREEN, speed=0.03, width=width)
    animate(f"You are now Level {new_level}!", style="typewriter", color_code=C.BR_CYAN, speed=0.02)

    # Flavor text
    animate("Your power surges through you...", style="pulse", color_code=C.BR_WHITE, speed=0.05, loops=3)
    animate("New abilities unlocked!", style="typewriter", color_code=C.BR_MAGENTA, speed=0.02)

def game_over_screen(width: int = 90):
    clear_screen()

    # Dark themed panel + slow reveal
    top = [
        center_line(color("GAME OVER", C.BOLD, C.BR_RED), width - 2),
        center_line(color("Your tale ends here... for now.", C.GRAY), width - 2),
    ]
    print_block(draw_panel("Fate Sealed", top, width))

    # Animated lament
    animate("You fought bravely.", style="typewriter", color_code=C.BR_WHITE, speed=0.03)
    animate("But courage alone could not prevail.", style="typewriter", color_code=C.GRAY, speed=0.03)

# ========= Dispatcher from your event payload =========
def show_battle_result(event_payload: dict, player_new_level: Optional[int] = None, width: int = 90):
    """
    Expects payload like:
    {
        "position": (x, y),
        "location": "Oakheart Village",
        "victory": True,
        "fled": False,
        "enemy_name": "Goblin",
        "gold_looted": 12,
        "xp_gained": 8,
        "leveled_up": True/False
    }
    If leveled_up is True and player_new_level is provided, will show level up.
    """
    victory = bool(event_payload.get("victory"))
    fled = bool(event_payload.get("fled"))
    enemy_name = event_payload.get("enemy_name", "Unknown")
    gold = int(event_payload.get("gold_looted", 0))
    xp = int(event_payload.get("xp_gained", 0))
    leveled_up = bool(event_payload.get("leveled_up"))

    if victory and not fled:
        victory_screen(enemy_name, gold, xp, width=width)
        if leveled_up and player_new_level is not None:
            # brief pause before level up
            time.sleep(0.6)
            level_up_screen(player_new_level, width=width)
    elif fled:
        clear_screen()
        animate("You retreated to fight another day.", style="typewriter", color_code=C.BR_YELLOW, speed=0.03)

    else:
        game_over_screen(width=width)

# ========= Optional: non-blocking key wait (simple) =========
def wait_keypress(prompt: str = "", color_code: Optional[str] = C.BR_WHITE):
    if prompt:
        animate(prompt, style="typewriter", color_code=color_code, speed=0.02)
    try:
        # Basic fallback; replace with your input system if needed
        input()
    except KeyboardInterrupt:
        pass

# ========= Demo (run directly) =========
if __name__ == "__main__":
    # Simulated event (your payload shape)
    event = {
        "position": (10, 5),
        "location": "Oakheart Village",
        "victory": True,
        "fled": False,
        "enemy_name": "Goblin Shaman",
        "gold_looted": 37,
        "xp_gained": 25,
        "leveled_up": True
    }
    show_battle_result(event_payload=event, player_new_level=4, width=90)
    wait_keypress("Press Enter to exit...")
