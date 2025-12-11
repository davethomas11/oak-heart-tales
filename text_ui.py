from engine.game.player import xp_to_next_level

import re

# --- ANSI helpers (robust and minimal) ---
ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')  # matches CSI ... final letter

def strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences."""
    return ANSI_RE.sub('', s or '')

def visible_len(s: str) -> int:
    """Display width ignoring ANSI sequences (ASCII-safe)."""
    return len(strip_ansi(s or ''))

def pad_line_vis(s: str, w: int) -> str:
    """
    Pad/truncate a possibly-colored string to visible width w.
    Preserves ANSI sequences; never cuts them mid-sequence.
    """
    if s is None:
        s = ""
    out = []
    vis = 0
    i = 0
    while i < len(s) and vis < w:
        if s[i] == "\x1b":
            # copy full ANSI sequence
            m = ANSI_RE.match(s, i)
            if m:
                out.append(m.group(0))
                i = m.end()
                continue
        # normal char
        out.append(s[i])
        vis += 1
        i += 1
    if vis < w:
        out.append(" " * (w - vis))
    return "".join(out)

def pad_line(s, w):
    """Compatibility shim using ANSI-aware padding/truncation."""
    return pad_line_vis(s, w)

def center_line(s, w):
    """Center a possibly-colored string to visible width w."""
    slen = visible_len(s)
    if slen >= w:
        return pad_line(s, w)
    left = (w - slen) // 2
    right = w - slen - left
    return " " * left + s + " " * right


def print_game_ui(
        get_room_ascii,
        player,
        state,
        width=90,
        height=40,
        use_color=False
):
    """
    Render a text-based game UI to the terminal.

    Parameters
    ----------
    get_room_ascii : callable
        A function that returns the current room as ASCII art.
        It may return:
          - a single string with newlines, or
          - a list of strings (each line).
        The art should represent a square or near-square grid.
    player : dict
        Player stats, e.g.:
          {
            "name": "Hero",
            "hp": 32, "hp_max": 40,
            "mp": 10, "mp_max": 15,
            "lvl": 3, "xp": 120, "xp_next": 200,
            "gold": 57,
            "status": ["Poisoned", "Inspired"],
            "weapon": "Shortsword",
            "armor": "Leather"
          }
        Any missing keys will be handled gracefully.
    state : dict
        Overall game state, e.g.:
          {
            "in_combat": True / False,
            "enemies": [
                {"name":"Goblin", "hp": 12, "hp_max": 20, "status": ["Bleeding"]},
                {"name":"Shaman", "hp": 8, "hp_max": 8, "status": []}
            ],
            "combat_log": ["You strike the goblin for 6", "Goblin hits you for 3"],
            "available_actions": ["[A]ttack", "[D]efend", "[I]tem", "[R]un"],
            "messages": ["You enter a damp cavern...", "There is a faint humming."],
            "question": {
                "prompt": "Pull the lever?",
                "options": ["Yes", "No"],
                "selected_index": 0  # optional: highlight
            }
          }
    width : int
        Total terminal width to target (characters).
    height : int
        Total terminal height to target (lines).
    use_color : bool
        If True, uses ANSI colors. If False, plain text.

    Notes
    -----
    - This function prints directly; it does not return a string.
    - It is layout-aware and will clamp/pad panels to fit requested width/height.
    """

    # ------------- Helpers -------------
    # Colors (ANSI)
    class C:
        RESET = "\033[0m"
        DIM = "\033[2m"
        BOLD = "\033[1m"
        BLUE = "\033[34m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        MAGENTA = "\033[35m"
        GRAY = "\033[90m"

    def color(s, code):
        return f"{code}{s}{C.RESET}" if use_color else s

    def clamp(n, lo, hi):
        return max(lo, min(hi, n))

    def wrap_text(text, w):
        """Simple greedy wrapper; returns list of lines."""
        if not text:
            return []
        import textwrap
        return textwrap.wrap(text, w) or [""]

    def safe_lines(block, w, h):
        """Normalize block into a list of lines of size <= h and each padded to w."""
        if isinstance(block, str):
            lines = block.splitlines()
        elif isinstance(block, list):
            lines = [str(x) for x in block]
        else:
            lines = [str(block)]
        if not lines:
            lines = [""]
        lines = [pad_line(l, w) for l in lines]
        # Clamp height
        if len(lines) > h:
            lines = lines[:h]
        else:
            lines.extend([" " * w] * (h - len(lines)))
        return lines

    def hbar(label, cur, mx, bar_w=20, good=True):
        """Render a horizontal bar, e.g., HP or MP."""
        cur = clamp(cur or 0, 0, mx or 1)
        filled = int((cur / (mx or 1)) * bar_w)
        empty = bar_w - filled
        fill_char = "█" if use_color else "#"
        empty_char = "░" if use_color else "-"
        bar = (color(fill_char * filled, C.GREEN if good else C.RED) +
               color(empty_char * empty, C.GRAY))
        text = f"{label}: {cur}/{mx}"
        return f"{pad_line(text, 12)} {bar}"

    def draw_panel(title, lines, w, subtitle=None):
        """Return list of strings representing a bordered panel."""
        title_str = f" {title} "
        if use_color:
            title_str = color(title_str, C.BOLD + C.YELLOW)
        if subtitle:
            if use_color:
                subtitle = color(subtitle, C.BOLD + C.GREEN)
            title_str += f"{subtitle} "

        border_color = C.CYAN if use_color else ""
        border_reset = C.RESET if use_color else ""
        top = f"{border_color}┌{pad_line(title_str + border_color + '─' * (w - visible_len(title_str) - 2), w - 2)}┐{border_reset}"
        body = [f"{border_color}│{border_reset}{pad_line(line, w - 2)}{border_color}│{border_reset}" for line in lines]
        bottom = f"{border_color}└{'─' * (w - 2)}┘{border_reset}"

        return [top] + body + [bottom]

    def join_columns(left_lines, right_lines):
        """Horizontally join two lists of equal-height lines."""
        return [l + r for l, r in zip(left_lines, right_lines)]

    # ------------- Layout decisions -------------
    # We’ll split the screen into:
    #   Top: Room panel (left ~55%) + Player/Combat panel (right ~45%)
    #   Bottom: Question (if any) and Message Log
    room_w = int(width * 0.55)
    side_w = width - room_w
    # Height allocation
    top_h = int(height * 0.75)
    bottom_h = height - top_h

    # ------------- Room Panel -------------
    room_art_raw = state.get("room_art") or get_room_ascii()
    # Normalize room art to lines
    if isinstance(room_art_raw, str):
        # Ensure squarish formatting: strip and split
        room_lines_raw = [l.rstrip("\n") for l in room_art_raw.splitlines()]
    elif isinstance(room_art_raw, list):
        room_lines_raw = [str(l) for l in room_art_raw]
    else:
        room_lines_raw = ["[room]"]

    if state["game_state"] == "SHOP":
        shop_banner = color("=== Shop ===", C.BOLD + C.YELLOW) if use_color else "=== Shop ==="
        room_lines_raw.insert(0, shop_banner)
        room_lines_raw.insert(1, "")
        flat_room_lines = []
        for l in room_lines_raw:
            wrapped_lines = wrap_text(l, room_w - 2)
            flat_room_lines.extend(wrapped_lines)
    else:
        # Wrap each room line if it exceeds room_w - 2
        # Center each room line if it is shorter than room_w - 2
        flat_room_lines = []
        for l in room_lines_raw:
            if isinstance(l, str):
                centered_lines = [center_line(line, room_w - 2) for line in l.splitlines()]
                flat_room_lines.extend(centered_lines)
            else:
                flat_room_lines.append(center_line(str(l), room_w - 2))

    room_lines_raw = flat_room_lines
    room_lines_raw.insert(0, "")
    # Fit the room into a panel height (top_h - 3 border lines for panel)
    room_inner_h = max(3, top_h - 3)
    # Choose a target art height that respects aspect (square-ish)
    # We'll just clamp and pad as needed.
    room_lines = safe_lines(room_lines_raw, w=room_w - 2, h=room_inner_h)
    room_panel = draw_panel("Area:", room_lines, w=room_w, subtitle=state['room'])

    # ------------- Player / Combat Panel -------------
    stats_lines = []
    stats_lines.append(pad_line(color(f"Name: {player.get('name', 'Unknown')}", C.BOLD), side_w - 2))
    stats_lines.append(hbar("HP", player.get("hp", 0), player.get("max_hp", 1), bar_w=20, good=True))
    stats_lines.append(hbar("MP", player.get("mp", 0), player.get("max_mp", 1), bar_w=20, good=True))
    lvl = player.get("level")
    xp = player.get("xp")
    xp_next = xp_to_next_level(lvl)
    stats_lines.append(pad_line(
        f"Lvl: {lvl if lvl is not None else '?'}  XP: {xp if xp is not None else '?'} / {xp_next if xp_next is not None else '?'}",
        side_w - 2))
    stats_lines.append(pad_line(f"Gold: {player.get('gold', 0)}", side_w - 2))
    weapon = player.get("weapon")
    armor = player.get("armor")
    if weapon:
        stats_lines.append(pad_line(f"Weapon: {weapon}", side_w - 2))
    if armor:
        stats_lines.append(pad_line(f"Armor:  {armor}", side_w - 2))
    statuses = player.get("status", [])
    if statuses:
        stats_lines.append(pad_line("Status: " + ", ".join(statuses), side_w - 2))

    map_lines = []
    # If combat, render combat info below stats
    combat_lines = []
    if state.get("in_combat"):
        combat_lines.append(pad_line(color("=== Combat ===", C.BOLD + C.RED), side_w - 2))
        enemies = state.get("enemies", [])
        for e in enemies:
            name = e.get("name", "Unknown")
            cur = e.get("hp", 0)
            mx = e.get("max_hp", 1)
            status = ", ".join(e.get("status", [])) if e.get("status") else ""
            line_name = pad_line(f"Enemy: {name}", side_w - 2)
            line_hp = hbar("HP", cur, mx, bar_w=20, good=False)
            combat_lines.append(line_name)
            combat_lines.append(line_hp)
            if status:
                combat_lines.append(pad_line(f"Status: {status}", side_w - 2))
        # Recent combat log (up to 4)
        clog = state.get("combat_log", [])
        if clog:
            combat_lines.append(pad_line("Log:", side_w - 2))
            for ln in clog[-4:]:
                for wrapped_ln in wrap_text(" - " + ln, side_w - 2):
                    combat_lines.append(pad_line(wrapped_ln, side_w - 2))
    else:
        combat_lines.append(pad_line(color("=== Exploration ===", C.BOLD + C.CYAN), side_w - 2))
        map_lines_raw = state.get("map", ["(no map)"]).splitlines()

        # Wrap each map line to fit, then center
        wrapped_map_lines = []
        for l in map_lines_raw:
            for wl in wrap_text(str(l), side_w - 2):
                centered = wl.center(side_w - 2)
                wrapped_map_lines.append(centered)
        combat_lines = safe_lines(wrapped_map_lines, w=side_w - 2, h=14)
        combat_lines.append("")

        # Add weather and tile description
        tile_desc = state.get("room_description", "Unknown area.")
        area_tile = color("Area Info:", C.MAGENTA) if use_color else "Area Info:"
        combat_lines.append(pad_line(area_tile, side_w - 2))
        for l in wrap_text(tile_desc, side_w - 2):
            combat_lines.append(pad_line(l, side_w - 2))
        weather = state.get("weather", "Unknown")
        weather_title = color("Weather:", C.MAGENTA) if use_color else "Weather:"
        combat_lines.append(pad_line(f"{weather_title}: {weather}", side_w - 2))


    # Combine stats + combat
    side_inner_h = max(3, top_h - 3)
    side_block = stats_lines + ([""] if stats_lines and combat_lines else []) + combat_lines
    side_block = safe_lines(side_block, w=side_w - 2, h=side_inner_h)
    side_panel = draw_panel("Status", side_block, w=side_w)

    # ------------- Top Row Join -------------
    top_lines = join_columns(room_panel, side_panel)

    # ------------- Bottom: Question + Messages -------------
    bottom_lines = []

    # Question prompt panel if present
    question = state.get("question")
    if question:
        q_w = width
        q_inner_h = 3  # fixed height for Q panel
        prompt = str(question.get("prompt", ""))
        q_lines = []
        for l in wrap_text(prompt, q_w - 2):
            q_lines.append(l)
        q_lines = safe_lines(q_lines, w=q_w - 2, h=q_inner_h)
        bottom_lines.extend(draw_panel("Question", q_lines, w=q_w))
    else:
        # Actions panel
        actions = state.get("available_actions", ["[A]ttack", "[D]efend", "[I]tem", "[R]un"])
        action_lines = []
        for i in range(0, len(actions), 3):
            wrapped = wrap_text("  ".join(actions[i:i+3]), width - 2)
            action_lines.extend(wrapped)
        action_inner_h = 4
        action_lines = safe_lines(action_lines, w=width - 2, h=action_inner_h)
        bottom_lines.extend(draw_panel("Actions", action_lines, w=width))

    # Message log panel
    msgs = state.get("messages", [])
    msg_panel_h = bottom_h - (len(bottom_lines))  # remaining lines
    msg_panel_h = clamp(msg_panel_h, 5, bottom_h)  # at least some space
    # Inner height accounts for panel borders (3 lines)
    msg_inner_h = max(3, msg_panel_h - 3)
    # Take last N messages and wrap each
    wrapped_msgs = []
    for m in msgs[-20:]:  # cap total messages considered
        wrapped_msgs.extend(wrap_text(m, width - 2))
    if not wrapped_msgs:
        wrapped_msgs = ["(no messages)"]
    wrapped_msgs = safe_lines(wrapped_msgs, w=width - 2, h=msg_inner_h)
    bottom_lines.extend(draw_panel("Messages", wrapped_msgs, w=width))

    # ------------- Final Compose & Print -------------
    # Ensure total lines equal desired height
    all_lines = top_lines + bottom_lines
    if len(all_lines) > height:
        all_lines = all_lines[:height]
    elif len(all_lines) < height:
        all_lines.extend([" " * width] * (height - len(all_lines)))

    # Optional clear screen (simple)
    print("\033[2J\033[H", end="")  # clear + home (most terminals)

    for ln in all_lines:
        print(ln)
