# asciimatics_renderers/game_view.py

from asciimatics.widgets import Frame, Layout, Label, TextBox, ListBox, Widget
from asciimatics.screen import Screen
from asciimatics.exceptions import StopApplication
from asciimatics.event import KeyboardEvent
from engine.game.game_state import GameState
from engine.game.ascii_renderer import render_room

# NEW IMPORT: Combat Renderer from the original file's structure
from engine.plugins.combat_renderer_2d import ASCIICombatRenderer #
from asciimatics.widgets import Frame, Layout, Label, TextBox, ListBox, Widget, PopUpDialog

class GameView(Frame):
    """
    The main game UI frame, holding all components:
    Room Art, Stats, Log, and Actions.
    """
    def __init__(self, screen: Screen, game):
        # ... (Frame initialization remains the same)
        height = screen.height
        width = screen.width

        super().__init__(screen,
                         height,
                         width,
                         hover_focus=True,
                         title="ASCII MUD RPG",
                         has_border=False)

        self._game = game
        self._screen = screen
        # NEW: Instantiate the combat renderer instance
        self._combat_renderer = ASCIICombatRenderer() #

        # NEW: State variables to track pop-up events
        self._show_combat_start = True # Flag to show dialog on entering COMBAT state
        self._show_rest_event = False
        self._show_battle_result = False

        # 1. Define the Layouts for the screen
        main_content_height = height * 3 // 4
        log_height = height - main_content_height

        main_layout = Layout([70, 30], fill_frame=False)
        self.add_layout(main_layout)

        # --- LEFT COLUMN (70%): Room Art & Description ---
        art_height = main_content_height * 2 // 3

        # Room Art Box (Does NOT wrap, as_string=True)
        self._room_art_box = TextBox(height=art_height,
                                     name="room_art",
                                     label="",
                                     as_string=True,
                                     line_wrap=False,
                                     readonly=True)
        main_layout.add_widget(self._room_art_box, 0)

        # Room Description/Weather Box (Wraps, allows full text)
        self._description_box = TextBox(height=main_content_height - art_height,
                                        name="room_description",
                                        label="",
                                        as_string=True,
                                        line_wrap=True,
                                        readonly=True)
        main_layout.add_widget(self._description_box, 0)

        # --- RIGHT COLUMN (30%): Player Info, Stats, Actions ---
        self._stats_label = Label("Stats: HP / MP / Gold")
        main_layout.add_widget(self._stats_label, 1)

        self._action_list = ListBox(height=main_content_height - 5,
                                    options=[],
                                    name="actions",
                                    label="Available Actions:")
        main_layout.add_widget(self._action_list, 1)

        # 2. Define the bottom layout for the Game Message/Combat Log
        log_layout = Layout([100], fill_frame=True)
        self.add_layout(log_layout)

        self._log_box = TextBox(height=log_height - 1,
                                name="log",
                                label="Log:",
                                as_string=True,
                                line_wrap=True,
                                readonly=True)
        log_layout.add_widget(self._log_box)

        # 3. Finalize the layout
        self.fix()

    def _check_and_show_popups(self, frame_no):
        """Checks game state and displays appropriate PopUpDialogs."""

        # 1. Combat Start Event
        if self._game.state == GameState.COMBAT and self._show_combat_start:
            self._show_combat_start = False # Reset flag immediately
            enemy_name = self._game.enemy.name if self._game.enemy else "an enemy"

            self._scene.add_effect(
                PopUpDialog(self._screen,
                            f"A wild {enemy_name.upper()} has appeared!\nPrepare for combat!",
                            ["FIGHT!"], # Button to dismiss the dialog
                            on_close=self._reset_focus_and_flags)
            )
            return True # Dialog shown

        # 2. Rest Event (Occurs right after an action)
        if self._show_rest_event:
            self._show_rest_event = False
            rest_message = "You rest for a moment...\nHP/MP regenerated."

            self._scene.add_effect(
                PopUpDialog(self._screen,
                            rest_message,
                            ["Continue"],
                            on_close=self._reset_focus_and_flags)
            )
            return True # Dialog shown

        # 3. Battle Result Event (Occurs when combat ends)
        if self._show_battle_result:
            self._show_battle_result = False

            # Use game state to determine win/loss
            if self._game.state == GameState.EXPLORING:
                # Assuming EXPLORING means the player won and moved on
                result_message = f"VICTORY! You defeated the enemy.\nYou gained {self._game.last_combat_rewards.get('exp', 0)} XP and {self._game.last_combat_rewards.get('gold', 0)} Gold!"
            elif self._game.state == GameState.GAME_OVER:
                result_message = "DEFEAT! Your journey has ended."
            else:
                result_message = "Combat ended."

            self._scene.add_effect(
                PopUpDialog(self._screen,
                            result_message,
                            ["Acknowledge"],
                            on_close=self._reset_focus_and_flags)
            )
            return True # Dialog shown

        return False # No dialog shown

    def _reset_focus_and_flags(self, selected_button):
        """Helper to re-focus the frame after a dialog closes."""
        # Ensure focus returns to the main frame after the pop-up
        self.switch_focus(self)
        # Any other global flags can be reset here if needed

    def update(self, frame_no):
        """Called every frame to update the content of the widgets."""

        # If a pop-up is displayed, skip the rest of the rendering/logic update
        if self._check_and_show_popups(frame_no):
            return

        # 0. Update combat renderer if in combat (Replicating game2d_loop logic)
        if self._game.state == GameState.COMBAT: #
            self._combat_renderer.update(self._game) #

        # 1. Determine Art and Description based on GameState
        description_lines = []

        # Room Art Rendering
        if self._game.state == GameState.COMBAT: #
            # --- COMBAT INTEGRATION ---
            # Safely get combat log (which was global in the original main_event_ui.py)
            combat_log = getattr(self._game, 'combat_log', [])

            # Call the combat rendering function
            room_art = self._combat_renderer.combat_fn(self._game, combat_log) #
            room_art_lines = room_art.splitlines()

            # Build Description Text
            description_lines.append("Engaged in deadly combat!")
            enemy = self._game.enemy.to_dict() if self._game.enemy else {}
            description_lines.append(f"Enemy: {enemy.get('name', 'Unknown')}")
            description_lines.append(f"HP: {enemy.get('hp', '??')}/{enemy.get('max_hp', '??')}")

        elif self._game.state == GameState.SHOP:
            room_art_lines = self._game.look().splitlines()
            description_lines.append(f"You entered the shop: {self._game.current_tile().name}.")
            description_lines.append("What would you like to buy?")
        elif self._game.state == GameState.EXPLORING:
            room_art = render_room(self._game.current_tile(), self._game.ascii_loader)
            room_art_lines = room_art.splitlines()

            # Build Description Text
            description_lines.append(f"Area: {self._game.current_tile().name}")
            description_lines.append(f"Weather: {self._game.current_tile().weather.describe()}")
            description_lines.append(self._game.current_tile().description)
            if self._game.room_has_shop():
                description_lines.append("You see a merchant here (type shop to enter).")
        else:
            room_art_lines = self._game.look().splitlines()

            state_name = getattr(self._game.state, 'name', str(self._game.state)).upper()
            description_lines.append(f"Current State: {state_name}")

            if self._game.state == GameState.GAME_OVER:
                description_lines.append("Your journey ends here. Check the log for options.")
            elif self._game.state == GameState.ASKING_QUESTION:
                description_lines.append(self._game.question or "A question is pending.")

        self._room_art_box.value = "\n".join(room_art_lines)
        self._description_box.value = "\n".join(description_lines)

        # 2. Update Stats
        stats = self._game.player.to_dict()
        stats_text = (
            f"Lvl: {stats['level']} | Gold: {stats['gold']}\n"
            f"HP: {stats['hp']}/{stats['max_hp']}\n"
            f"MP: {stats.get('current_mp', 'N/A')}/{stats.get('max_mp', 'N/A')}"
        )
        self._stats_label.text = stats_text

        # 3. Update Actions
        actions = self._game.available_actions() #
        action_options = []
        for action in actions:
            if action['enabled']:
                hotkeys = action.get('hotkeys', [])
                # Find the first hotkey that is a single character
                key_str = ""
                for hk in hotkeys:
                    if isinstance(hk, str) and len(hk) == 1:
                        key_str = f"[{hk.upper()}]"
                        break

                label = f"{key_str} {action['label']}"
                action_options.append((label, action['id']))

        self._action_list.options = action_options

        # 4. Update Log
        # Use getattr for safe access to combat_log or game_messages (which were global in original)
        if self._game.state == GameState.COMBAT: #
            log_content = getattr(self._game, 'combat_log', ["Log: Combat log not available."])
        else:
            log_content = getattr(self._game, 'game_messages', ["Log: Game messages not available."])

        self._log_box.value = self._result_desc if hasattr(self, '_result_desc') else "\n".join(log_content)

        super().update(frame_no)

    def process_event(self, event):
        """Handle keyboard events for action hotkeys and quitting."""
        # ... (Input handling remains the same)
        if isinstance(event, KeyboardEvent):
            if event.key_code in (ord('q'), ord('Q')):
                raise StopApplication("User quit")

            try:
                char = chr(event.key_code).lower()
            except ValueError:
                char = ''

            self._result_desc = self._game.execute_action(char)

        # Check if a dialog is active; if so, pass event to parent for dialog handling
        if self._scene and self._scene.effects:
            # Check if the top-most effect is a dialog. If so, let it handle input.
            if isinstance(self._scene.effects[-1], PopUpDialog):
                return super().process_event(event)

        return super().process_event(event)

    # NEW: Setter methods to be called by the event handler (on_event in main_asciimatics.py)
    def trigger_rest_event(self):
        self._show_rest_event = True

    def trigger_battle_result(self):
        self._show_battle_result = True

    def trigger_combat_start(self):
        # This will be called on entering the COMBAT state.
        self._show_combat_start = True