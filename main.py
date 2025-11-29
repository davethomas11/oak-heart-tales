#!/usr/bin/env python3
"""
Text-based single-player MUD-like mini RPG

Now modularized with JSON-based world generation and save/load.

Run: python3 main.py
"""

import sys
from typing import List

from game import Game, GameState
from persistence import save_game, load_game, SAVE_FILE


def clear_screen() -> None:
    """Clear the terminal screen using ANSI escape codes (cross-platform in most modern terminals)."""
    # ANSI clear + move cursor home
    print("\033[2J\033[H", end="")


def ui_render(text: str) -> None:
    """Clear the screen and render the provided text."""
    clear_screen()
    print(text)


HELP_TEXT = (
    "Commands:\n"
    "  n,s,e,w           Move north/south/east/west\n"
    "  look              Describe your current location\n"
    "  map               Show map of explored areas\n"
    "  stats             Show your character sheet\n"
    "  rest              Rest to recover a bit of HP (unsafe outside village)\n"
    "  shop              Visit the merchant if present to buy spells\n"
    "  inv               Show inventory\n"
    "  save              Save game to save.json\n"
    "  load              Load game from save.json\n"
    "  help              Show this help\n"
    "  quit              Quit the game\n"
)


def banner() -> str:
    return (
        "=" * 50
        + "\n"
        + "Oakheart Tales: A Tiny Text MUD\n"
        + "Explore, fight, and grow stronger. Type 'help' to begin.\n"
        + "=" * 50
    )


def prompt_start_menu() -> str:
    clear_screen()
    print(banner())
    print("[N]ew Game  |  [L]oad Game  |  [Q]uit")
    while True:
        choice = input("> ").strip().lower()
        if choice in ("n", "new"):
            return "new"
        if choice in ("l", "load"):
            return "load"
        if choice in ("q", "quit"):
            return "quit"
        print("Please enter N, L, or Q.")


def prompt_map_size() -> int:
    clear_screen()
    print("Choose map size: 3, 5, 7, 9")
    while True:
        s = input("> ").strip()
        if s in ("3", "5", "7", "9"):
            return int(s)
        print("Invalid size. Choose 3, 5, 7 or 9.")


def game_loop(game: Game) -> None:
    """Main interactive loop. On death, allow Load or Restart instead of hard exit."""
    while True and game.ended is False:
        # Start or resume session
        ui_render(game.look())
        while game.player.is_alive():
            try:
                cmd = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                return

            # First, try the decoupled actions API so any interface can drive the game
            acted = game.execute_action(cmd)
            if game.ended:
                break  # exit to outer loop on game end
            if acted is not None:
                ui_render(acted)
                continue

            if cmd == "debug":
                ui_render(game.debug_pos())
            else:
                ui_render(game.look() + f"\n\nUnknown command [{cmd}]. Type 'help' for a list of commands.")

        # Player has died; offer options
        if not game.ended:
            ui_render("Game Over.\n[L]oad  |  [R]estart  |  [Q]uit")
        while True and game.ended is False:
            try:
                choice = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                return

            if choice in ("l", "load"):
                loaded = Game.from_dict(load_game(SAVE_FILE))
                if loaded:
                    game.copy_from(loaded)
                    break  # resume outer loop with loaded game
                else:
                    ui_render("No save found or save file invalid.\n[L]oad  |  [R]estart  |  [Q]uit")
                    continue
            if choice in ("r", "restart"):
                # Restart with a fresh world of the same size
                try:
                    size = max(game.world.width, game.world.height)
                except Exception:
                    size = 5
                fresh = Game.new_random(size=size)
                game.copy_from(fresh)
                break  # resume outer loop with fresh game
            if choice in ("q", "quit"):
                print("Farewell, adventurer.")
                return
            print("Please enter L, R, or Q.")


def main(argv: List[str]) -> int:
    choice = prompt_start_menu()
    if choice == "quit":
        print("Goodbye.")
        return 0
    if choice == "load":
        loaded = load_game(SAVE_FILE)
        if not loaded:
            print("No save found or save file invalid.")
            return 1
        game_loop(Game.from_dict(loaded))
        return 0

    # New game
    size = prompt_map_size()
    game = Game.new_random(size=size)
    game_loop(game)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
