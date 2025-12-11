#!/usr/bin/env python3
"""
Text-based single-player MUD-like mini RPG

Now modularized with JSON-based world generation and save/load.

Run: python3 main.py
"""

import sys
import time
from typing import List

from animated_combat_start import show_combat_start_event
from animated_rest import show_rest_event
from animated_screens import show_battle_result, wait_keypress
from engine.game import Game
from engine.game.ascii_renderer import render_room
from engine.game.event import GameEvent
from engine.game.game_state import GameState
from json_loader import JsonLoader
from persistence import load_game, save_game, SAVE_FILE
from text_loader import TextLoader
from text_ui import print_game_ui
from engine.plugins.game2d import Game2DPlugin, render_room as render_room_2d, TerminalInputHandler, EVENT_ROOM_ENTERED, \
    EVENT_ENTER_COMBAT

last_event: GameEvent = None
game_messages = []
error_messages = ""
combat_log = []


class RenderPlugin:
    def __init__(self, render_fn: callable, actions_fn: callable = None):
        self.render_fn = render_fn
        self.actions_fn = actions_fn


def clear_screen() -> None:
    """Clear the terminal screen using ANSI escape codes (cross-platform in most modern terminals)."""
    # ANSI clear + move cursor home
    print("\033[2J\033[H", end="")


def available_actions_str(game: Game) -> list:
    actions = game.available_actions()
    lines = []
    for action in actions:
        if action['enabled'] and action['label'] not in ['Look', 'Stats', 'Map', 'Help']:
            lines.append(f"{action['label']} ({', '.join(action['hotkeys'])})")
    return lines


def ui_render(game: Game, renderPlugin: RenderPlugin = None) -> None:
    """Clear the screen and render the provided text."""
    room_art = game.look() if game.state == GameState.SHOP else render_room(game.current_tile(), game.ascii_loader)
    actions = available_actions_str(game)
    if renderPlugin is not None:
        room_art = renderPlugin.render_fn()
        actions = renderPlugin.actions_fn() if renderPlugin.actions_fn is not None else actions
    if len(error_messages) > 0:
        room_art = error_messages
    clear_screen()
    print_game_ui(lambda: room_art,
                  game.player.to_dict(), {
                      'in_combat': game.state == GameState.COMBAT,
                      'game_state': game.state,
                      'room': game.current_tile().name,
                      'room_art': room_art,
                      'room_description': game.current_tile().description,
                      'weather': game.current_tile().weather.describe(),
                      'map': game.map(),
                      'messages': game_messages,
                      'enemies': [game.enemy.to_dict() if game.enemy else None],
                      'combat_log': combat_log,
                      'available_actions': actions,
                      'question': {
                          'prompt': game.question,
                          'options': ["Yes", "No"]
                      } if game.state == GameState.ASKING_QUESTION else None
                  }, 90, 40, True)


banner_title = """
   ___   _   _  __  _  _ ___   _   ___ _____   _____ _   _    ___ ___ 
  / _ \ /_\ | |/ / | || | __| /_\ | _ \_   _| |_   _/_\ | |  | __/ __|
 | (_) / _ \| ' <  | __ | _| / _ \|   / | |     | |/ _ \| |__| _|\__ \\
  \___/_/ \_\_|\_\ |_||_|___/_/ \_\_|_\ |_|     |_/_/ \_\____|___|___/
                                                                                
"""
banner_sub = """
                    ▄▖  ▄▖▘      ▄▖    ▗      ▌      ▗       
                    ▌▌  ▐ ▌▛▌▌▌  ▐ █▌▚▘▜▘  ▀▌▛▌▌▌█▌▛▌▜▘▌▌▛▘█▌
                    ▛▌  ▐ ▌▌▌▙▌  ▐ ▙▖▞▖▐▖  █▌▙▌▚▘▙▖▌▌▐▖▙▌▌ ▙▖
                             ▄▌                              
"""


def banner() -> str:
    return (
            "=" * 70
            + "\n"
            + banner_title
            + banner_sub
            + "\n"
            + "-~-" * 24
            + "\nExplore, fight, and grow stronger.\n"
            + "=" * 70
    )


def prompt_start_menu() -> str:
    clear_screen()
    print(banner())
    print("\n")
    print("[N]ew Game  |  [2]d New Game  |  [L]oad Game  |  [Q]uit")
    while True:
        choice = input("> ").strip().lower()
        if choice in ("n", "new"):
            return "new"
        if choice in ("2", "2d", "2d new"):
            return "2d"
        if choice in ("l", "load"):
            return "load"
        if choice in ("q", "quit"):
            return "quit"
        print("Please enter N, L, or Q.")


def prompt_map_size(options=("3", "5", "7", "9")) -> int:
    clear_screen()
    print("Choose map size: " + ", ".join(options))
    while True:
        s = input("> ").strip()
        if s in options:
            return int(s)
        print("Invalid size. Choose " + ", ".join(options) + ".")


def game2d_loop(game: Game, game2d: Game2DPlugin) -> None:
    global game_messages
    global last_event
    global error_messages

    terminal_input = TerminalInputHandler()
    render_plugin = RenderPlugin(
        render_fn=lambda: render_room_2d(game2d.get_current_room(), game2d.player),
        actions_fn=lambda: [terminal_input.get_controls()]
    )

    while game.ended is False:
        # 1. Process Input (Non-blocking check)
        action = terminal_input.get_input()

        # Handle quit immediately
        if action == 'quit':
            break

        # 2. Update Game State (Applies physics/gravity)
        game2d.update()

        # TODO: Sync game2d state back to main game if needed
        if game2d.state == "combat":
            game2d.state = "exploring"

        # 3. Handle Discrete Actions (Movement, Jump, Transitions)
        if action in ('left', 'right', 'jump'):
            # In tap-based input, we handle the movement directly here.
            game2d.handle_input(action)

        # 4. Render
        ui_render(game, render_plugin)

        # 5. Control Frame Rate
        time.sleep(0.05)


def game_loop(game: Game) -> None:
    global game_messages
    global last_event
    global error_messages

    """Main interactive loop. On death, allow Load or Restart instead of hard exit."""
    while True and game.ended is False:
        # Start or resume session
        game.available_actions()
        ui_render(game)
        while game.player.is_alive():
            try:
                cmd = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                return

            # First, try the decoupled actions API so any interface can drive the game
            error_messages = ""
            acted = game.execute_action(cmd)
            if "failed" in (acted or "").lower() and "Traceback (most recent call last):" in (acted or ""):
                error_messages = acted  # capture traceback lines
                game_messages = ["An error occurred during that action."]

            if "Inventory:" in (acted or ""):
                game_messages.append((acted or "").replace("\n", " "))

            if "Stats for" in (acted or ""):
                game_messages.append((acted or "").replace("\n", " "))

            if "Spells:" in (acted or ""):
                game_messages.append((acted or "").replace("\n", " "))

            if len(game_messages) > 3:
                game_messages = game_messages[-3:]

            animated_events()

            if game.ended:
                break  # exit to outer loop on game end
            if acted is not None:
                ui_render(game)
                continue

            if cmd == "debug":
                game_messages = ["Debug position show: " + game.debug_pos()]
                ui_render(game)
            else:
                game_messages = [f"Unknown command [{cmd}]."]
                ui_render(game)

        animated_events()
        # Player has died; offer options
        if not game.ended:
            clear_screen()
            print("Game Over.\n[L]oad  |  [R]estart  |  [Q]uit")
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
                    game_messages = []
                    break  # resume outer loop with loaded game
                else:
                    print("No save found or save file invalid.\n[L]oad  |  [R]estart  |  [Q]uit")
                    continue
            if choice in ("r", "restart"):
                # Restart with a fresh world of the same size
                try:
                    size = max(game.world.width, game.world.height)
                except Exception:
                    size = 5
                tileset = JsonLoader().load("data/tileset.json")
                fresh = Game.new_random(size=size, tileset=tileset)
                game.copy_from(fresh)
                game_messages = []
                break  # resume outer loop with fresh game
            if choice in ("q", "quit"):
                print("Farewell, adventurer.")
                return
            print("Please enter L, R, or Q.")


def animated_events() -> None:
    global last_event
    if last_event is not None:
        if last_event.event_type == GameEvent.EXITED_COMBAT:
            # Show animated end of combat summary
            clear_screen()
            show_battle_result(last_event.payload, game_ref.player.level)
            wait_keypress("Press any key to continue...")
            last_event = None  # reset after showing

    if last_event is not None:
        if (last_event.event_type == GameEvent.RESTED or
                last_event.event_type == GameEvent.REST_INTERRUPTED):
            show_rest_event(last_event.payload, width=90)
            wait_keypress("Press any key to continue...")
            last_event = None  # reset after showing

    if last_event is not None:
        if (last_event.event_type == GameEvent.ENTERED_COMBAT):
            clear_screen()
            show_combat_start_event(last_event.payload)
            wait_keypress("Press any key to continue...")
            last_event = None  # reset after showing


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
        return run_game(Game.from_dict(loaded))

    tileset = JsonLoader().load("data/tileset.json")

    if choice == "2d":
        size = prompt_map_size(("5", "10", "15", "20"))
        game_2d = Game2DPlugin(size, 10, 6)
        game = Game.new_random(size=size, tileset=tileset, flat=True)
        return run_game(game, game_2d)
    else:
        # New game
        size = prompt_map_size()

    return run_game(Game.new_random(size=size, tileset=tileset))


game_ref: Game = None


def run_game(game: Game, game2d: Game2DPlugin = None) -> int:
    global game_ref
    game.data_loader = JsonLoader()
    game.ascii_loader = TextLoader("data/rooms")
    game.load_configurations("data/enemies.json")
    game.save_file = SAVE_FILE
    game.save_fn = save_game
    game.load_fn = load_game
    game.event_manager.subscribe(on_event)
    game_ref = game
    if game2d is not None:
        game2d.event_manager.subscribe(on_2d_event)
        game2d_loop(game, game2d)
    else:
        game_loop(game)
    return 0


def on_2d_event(event: GameEvent) -> None:
    global game_ref
    if event.event_type == EVENT_ROOM_ENTERED:
        game_ref.warp_to_tile(event.payload['index'], 0, "moved")
    pass


def on_event(event: GameEvent) -> None:
    global last_event
    global game_messages
    event_type = event.event_type
    data = event.payload
    last_event = event
    if event_type == GameEvent.ATTACKED:
        game_message = f"You attacked the {data.get('enemy_name')} for {data.get('damage')} damage!"
    elif event_type == GameEvent.ATTEMPT_MOVE:
        game_message = f"You try to move from {data.get('from')} by {data.get('delta')}."
    elif event_type == GameEvent.CANT_MOVE:
        reason = data.get('reason', 'unknown')
        if reason == "edge_of_world":
            game_message = "You can't go that way."
        elif reason == "stuck_weather":
            game_message = "You are stuck due to the weather and can't move!"
        elif reason == "move_declined":
            game_message = "You decide not to proceed there."
        else:
            game_message = "Movement failed."
    elif event_type == GameEvent.MOVED:
        game_message = f"You moved to {data.get('to')}: {data.get('tile_name')}."
    elif event_type == GameEvent.WEATHER_CHANGED:
        game_message = f"Weather changed at {data.get('position')}: {data.get('weather')}."
    elif event_type == GameEvent.DANGER_WARNING:
        game_message = f"Warning: {data.get('tile_name')} is dangerous (danger {data.get('danger'):.2f})."
    elif event_type == GameEvent.FOUND_SHOP:
        game_message = f"You found a shop at {data.get('position')}."
    elif event_type == GameEvent.ENTERED_SHOP:
        game_message = f"You entered the shop: {data.get('tile_name')}."
    elif event_type == GameEvent.EXITED_SHOP:
        game_message = "You left the shop."
    elif event_type == GameEvent.SHOP_EMPTY:
        game_message = "The merchant has nothing left to teach you."
    elif event_type == GameEvent.SHOP_ITEM_NOT_FOUND:
        game_message = f"Shop does not have '{data.get('selection')}'."
    elif event_type == GameEvent.SHOP_NOT_ENOUGH_GOLD:
        game_message = f"Not enough gold for {data.get('selection')} ({data.get('price')}g)."
    elif event_type == GameEvent.BOUGHT_ITEM:
        game_message = f"You bought the spell {data.get('spell')} for {data.get('price')} gold."
    elif event_type == GameEvent.RESTED:
        if data.get('received_potion'):
            game_message = f"You rest and heal {data.get('healed')} HP. You receive a potion."
        else:
            game_message = f"You rest and heal {data.get('healed')} HP."
    elif event_type == GameEvent.REST_INTERRUPTED:
        game_message = f"You are ambushed by {data.get('enemy_name')} during rest!"
    elif event_type == GameEvent.FOUND_WEAPON:
        weapon = data.get('weapon')
        if weapon:
            game_message = f"You found a weapon: {weapon.name} (ATK +{weapon.attack_bonus})."
        else:
            game_message = "You found a weapon."
    elif event_type == GameEvent.PICKED_UP_WEAPON:
        weapon = data.get('weapon')
        game_message = f"You picked up the {weapon.name}."
    elif event_type == GameEvent.LEFT_WEAPON:
        weapon = data.get('weapon')
        game_message = f"You left the {weapon.name} behind."
    elif event_type == GameEvent.ENTERED_COMBAT:
        game_message = f"Combat started with {data.get('enemy_name')}!"
    elif event_type == GameEvent.EXITED_COMBAT:
        if data.get('victory'):
            game_message = (f"You defeated {data.get('enemy_name')} and "
                            f"gained {data.get('gold_looted', 0)} gold and {data.get('xp_gained')} XP.")
        elif data.get('fled'):
            game_message = f"You fled from {data.get('enemy_name')}."
        else:
            game_messages = []
            game_message = "You were defeated in combat."
    elif event_type == GameEvent.ENEMY_ATTACKED:
        game_message = f"{data.get('enemy_name')} attacked you for {data.get('damage')} damage."
    elif event_type == GameEvent.ENEMY_STUNNED:
        game_message = f"{data.get('enemy_name')} is stunned for {data.get('turns_left')} turns."
    elif event_type == GameEvent.ENEMY_RECOVERED:
        game_message = f"{data.get('enemy_name')}'s defenses recovered."
    elif event_type == GameEvent.CAST_SPELL:
        spell_type = data.get('type')
        if spell_type == "heal":
            game_message = f"You cast Heal and restore {data.get('healed')} HP."
        elif spell_type == "regen":
            game_message = f"You cast Regen. {data.get('regen_amount')} HP for {data.get('regen_turns')} turns."
        elif spell_type == "debuff":
            game_message = "You cast Guard Break! Enemy defenses down."
        elif spell_type == "damage":
            game_message = f"You cast {data.get('spell')} for {data.get('damage')} damage."
        else:
            game_message = f"You cast {data.get('spell')}."
    elif event_type == GameEvent.OOM:
        game_message = "Not enough MP to cast the spell."
    elif event_type == GameEvent.REGEN:
        game_message = f"Regen restores {data.get('healed')} HP. Turns left: {data.get('turns_left')}."
    elif event_type == GameEvent.USED_POTION:
        if data.get('used_in_combat'):
            game_message = f"You used a potion and healed {data.get('healed')} HP."
        else:
            reason = data.get('reason')
            if reason == "no_potions":
                game_message = "You have no potions left."
            elif reason == "not_in_combat":
                game_message = "You don't need a potion now."
            else:
                game_message = "Potion use failed."
    elif event_type == GameEvent.FAILED_FLEE:
        game_message = "You failed to flee from combat."
    else:
        game_message = data.get("message") if hasattr(data, "message") else f"Event: {event_type}"
    if game_ref.state == GameState.COMBAT:
        combat_log.append(game_message)
        if len(combat_log) > 5:
            combat_log.pop(0)
    else:
        if len(game_messages) >= 3:
            game_messages.pop(0)
        game_messages.append(game_message)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
