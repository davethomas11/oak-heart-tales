#!/usr/bin/env python3
"""
Text-based single-player MUD-like mini RPG using asciimatics.

Run: python3 main_asciimatics.py
"""

import sys
from typing import List

from asciimatics.exceptions import ResizeScreenError

from engine.game import Game
from engine.game.event import GameEvent
from json_loader import JsonLoader
from persistence import load_game, save_game, SAVE_FILE
from text_loader import TextLoader
from asciimatics_renderers.game_view import GameView

from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import StopApplication

active_scene_ref = None # Global to hold the active scene for event handling

class MainScene(Scene):
    """The main game scene. Now simply holds the GameView Frame."""
    def __init__(self, screen, game):
        self._game_view = GameView(screen, game)
        # Pass the Frame object to the Scene constructor
        super().__init__([self._game_view], duration=-1, name="MainGameScene")
        self.game = game
        # Make the GameView instance accessible
        self.game_view = self._game_view

    # --- End Corrected Placeholder Code ---

    def process_event(self, event):
        # Important: Call the base class to handle global events (like ESC) or pass to next widget
        super().process_event(event)

# --- End Placeholder/Dummy Code ---


def asciimatics_render_loop(screen: Screen, game: Game) -> None:
    """
    Sets up and runs the asciimatics rendering loop.
    """

    # We define the scenes in the application
    scenes = [
        MainScene(screen, game)
    ]

    # Start the application, moving between scenes as needed.
    # The `render_updates` call drives the game loop logic.
    screen.play(scenes, stop_on_resize=True)


def prompt_start_menu(screen: Screen) -> str:
    """
    A simple, terminal-based menu, since asciimatics is overkill for a menu.
    """
    # The banner() and clear_screen() functions from the original file would be used here.
    # Since we don't have those, we'll use simple prints.

    # Temporarily restore normal terminal for non-asciimatics input
    screen.close()

    print("\n" * 50) # Simple clear
    print("=" * 70)
    print("OAK HEART TALES: A TINY TEXT ADVENTURE")
    print("=" * 70)
    print("\n[N]ew Game | [L]oad Game | [Q]uit")

    while True:
        choice = input("> ").strip().lower()
        if choice in ("n", "new"):
            return "new"
        if choice in ("l", "load"):
            return "load"
        if choice in ("q", "quit"):
            return "quit"
        print("Please enter N, L, or Q.")


def prompt_map_size(options=("3", "5", "7", "9")) -> int:
    print("\nChoose map size: " + ", ".join(options))
    while True:
        s = input("> ").strip()
        if s in options:
            return int(s)
        print("Invalid size. Choose " + ", ".join(options) + ".")


def main_loop(screen: Screen, game: Game) -> None:
    """
    The game loop handles setup and screen resizing.
    """
    global game_ref, active_scene_ref
    game_ref = game

    # Initialize game services
    game.data_loader = JsonLoader()
    game.ascii_loader = TextLoader("data/rooms")
    game.load_configurations("data/enemies.json")
    game.save_file = SAVE_FILE
    game.save_fn = save_game
    game.load_fn = load_game
    # Subscribe to events, handling combat/messages in the UI layer
    game.event_manager.subscribe(on_event)

    # Start the asciimatics rendering loop
    last_scene = None
    while True:
        try:
            current_scene = MainScene(screen, game)
            active_scene_ref = current_scene # Set the global reference
            screen.play([MainScene(screen, game)], stop_on_resize=True, start_scene=last_scene)
            sys.exit(0)
        except ResizeScreenError as e:
            # Handle resizing (common in terminal apps)
            last_scene = e.scene


def on_event(event) -> None:
    """Handles game events and triggers UI animations/updates."""
    global active_scene_ref

    # Standard event logging remains here (as per your original file)
    # The combat_renderer.trigger_animation(event_type) from the original file
    # should be part of the combat renderer update logic, which is now in GameView.update.

    # 1. Handle combat start/end and rest events by signaling the GameView
    if active_scene_ref and isinstance(active_scene_ref, MainScene):
        game_view = active_scene_ref.game_view

        if event.event_type == GameEvent.ENTERED_COMBAT:
            game_view.trigger_combat_start()
        elif event.event_type == GameEvent.EXITED_COMBAT:
            game_view.trigger_battle_result()
        elif event.event_type == GameEvent.RESTED:
            game_view.trigger_rest_event()

    # 2. Process log messages (still necessary for the log box)
    # This logic from your original on_event handler must be preserved here or moved to GameView.update.
    # We will assume simple message logging for now.

    # ... (rest of the message processing/log appending logic, assuming combat_log/game_messages are lists on the Game object)

def main(argv: List[str]) -> int:
    choice = Screen.wrapper(prompt_start_menu) # Use screen wrapper for menu just in case

    if choice == "quit":
        print("Goodbye.")
        return 0

    if choice == "load":
        loaded = load_game(SAVE_FILE)
        if not loaded:
            print("No save found or save file invalid.")
            return 1
        game = Game.from_dict(loaded)
    else:
        # New game
        tileset = JsonLoader().load("data/tileset.json")
        size = prompt_map_size()
        game = Game.new_random(size=size, tileset=tileset)

    # Start the main game loop, passing the Game object
    try:
        Screen.wrapper(main_loop, arguments=[game])
    except StopApplication:
        print("\nGoodbye, adventurer.")
        return 0

    return 0


game_ref: Game = None # Global reference for event handling

if __name__ == "__main__":
    sys.exit(main(sys.argv))