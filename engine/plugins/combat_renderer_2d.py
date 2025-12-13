import time
from typing import List, Any, Tuple
import random

from engine.game.event import GameEvent

# --- Configuration Constants (Can be moved to a settings file if desired) ---
# The user-requested dimensions (40x60)
DEFAULT_HEIGHT = 40
DEFAULT_WIDTH = 60
COMBAT_LOG_LINES = 6

# A simple animation for an "attack" effect
ATTACK_ANIMATION = ["-", "\\", "|", "/"]
# FIX: Increased duration from 0.3s to 0.6s for clear staggering between animations
ANIMATION_DURATION = 0.6  # Seconds for a single animation cycle (e.g., 4 steps * 0.15s/step)

# Death animation for player (simple blinking "X" or similar)
DEATH_ANIMATION = ["X", " ", "X", " "]
DEATH_MESSAGES = [
    "You have fallen in battle...",
    "The journey ends here.",
    "A hero's light fades away.",
    "Defeat claims another soul.",
    "Your story is written in silence."
]

# NEW: Victory animation for enemy death
VICTORY_MESSAGES = [
    "FATAL BLOW! The enemy falls.",
    "Victory is yours!",
    "The monster is defeated!",
    "You stand triumphant.",
    "Another foe vanquished."
]
VICTORY_ANIMATION_STATE = "VICTORY" # A unique state identifier for victory message animation
PLAYER_DEATH_ANIMATION_STATE = "PLAYER_DEATH_MESSAGE" # NEW: State for death message reveal

# Health bar character
HP_BAR_FILL_CHAR = '█'

# NEW: ANSI Color Codes for Health Bar
COLOR_GREEN = "\033[92m"    # Bright Green
COLOR_YELLOW = "\033[93m"   # Bright Yellow
COLOR_RED = "\033[91m"      # Bright Red
COLOR_RESET = "\033[0m"


class ASCIICombatRenderer:
    """
    A custom renderer for combat that uses ASCII text within a fixed frame.

    This class provides the 'combat_fn' to replace the room render when in
    Game.GameState.COMBAT. It also has an 'update' function to drive animations.
    """
    def __init__(self, height: int = DEFAULT_HEIGHT, width: int = DEFAULT_WIDTH):
        """
        Initializes the combat renderer with configurable dimensions.
        """
        self.height = height
        self.width = width

        # State variables for animation context
        self.animation_state: str = ""
        self.animation_timer: float = 0.0
        self.last_update_time: float = time.time()

        # Queue to hold incoming combat events (animations)
        self.animation_queue: List[str] = []

        # State tracking for enemy status
        self._enemy_was_alive: bool = False

        # Dedicated time trackers for message animations
        self._death_message_start_time: float = 0.0
        self._death_message_complete: bool = False
        self._victory_message_complete: bool = False

        # Variables for smooth health bar animation
        self._player_display_hp: float = 0.0
        self._enemy_display_hp: float = 0.0
        self._player_max_hp: int = 1
        self._enemy_max_hp: int = 1

    def update(self, game_ref: Any) -> None:
        """
        Updates the renderer state and manages animations.

        This method should be called regularly in the game loop to drive
        the animation timer and process the animation queue.
        """
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        enemy = getattr(game_ref, 'enemy', None)
        player = getattr(game_ref, 'player', None)
        enemy_is_alive = enemy and getattr(enemy, 'hp', 0) > 0
        player_is_dead = player and getattr(player, 'hp', 0) <= 0

        # --- Health Bar Smoothing ---
        SMOOTHING_FACTOR = 5.0 # How fast the displayed HP catches up (higher is faster)

        # Player HP Smoothing
        player_current_hp = getattr(player, 'hp', 0)
        player_max_hp = getattr(player, 'max_hp', 1)
        self._player_max_hp = player_max_hp # Store max HP

        if self._player_display_hp == 0.0 and player_current_hp > 0: # Initialize on first frame or first time seeing player
            self._player_display_hp = float(player_current_hp)

        # Smoothly move display HP towards actual HP
        diff = float(player_current_hp) - self._player_display_hp
        self._player_display_hp += diff * SMOOTHING_FACTOR * delta_time
        self._player_display_hp = max(0, min(self._player_display_hp, float(player_max_hp)))

        # Enemy HP Smoothing
        enemy_current_hp = getattr(enemy, 'hp', 0)
        enemy_max_hp = getattr(enemy, 'max_hp', 1)

        # Track max HP for the currently displayed enemy (important for post-death rendering)
        # If a new enemy comes up (max_hp changes) or if we just initialized, reset display HP.
        if self._enemy_max_hp != enemy_max_hp or (self._enemy_display_hp == 0.0 and enemy_current_hp > 0):
            self._enemy_display_hp = float(enemy_current_hp)
            self._enemy_max_hp = enemy_max_hp

        # Smoothly move display HP towards actual HP
        diff = float(enemy_current_hp) - self._enemy_display_hp
        self._enemy_display_hp += diff * SMOOTHING_FACTOR * delta_time
        self._enemy_display_hp = max(0, min(self._enemy_display_hp, float(enemy_max_hp)))

        # --- End Health Bar Smoothing ---

        # --- Check for Enemy Defeat and Trigger Victory Animation ---
        if self._enemy_was_alive and not enemy_is_alive:
            # Enemy just died (HP <= 0), trigger victory message animation
            if self.animation_state != VICTORY_ANIMATION_STATE:
                self.animation_state = VICTORY_ANIMATION_STATE
                self.animation_timer = 0.0 # Reset timer for new message reveal
                self._victory_message_complete = False # Start the animation

        # Update the state tracker for the next frame
        self._enemy_was_alive = enemy_is_alive

        # Update Animation Timer for the current animation
        if self.animation_state:
            self.animation_timer += delta_time
            if self.animation_state not in [VICTORY_ANIMATION_STATE, PLAYER_DEATH_ANIMATION_STATE] and \
                    self.animation_timer > ANIMATION_DURATION:
                # Current non-message animation finished
                self.animation_state = ""
                self.animation_timer = 0.0

            # Check if victory message finished
            if self.animation_state == VICTORY_ANIMATION_STATE and self._victory_message_complete:
                self.animation_state = ""
                self.animation_timer = 0.0
                self._victory_message_complete = False


        # Start the next animation if one is queued and the current one is finished
        if not self.animation_state and self.animation_queue:
            # Pop the next event from the queue (FIFO)
            self.animation_state = self.animation_queue.pop(0)
            self.animation_timer = 0.0

        # --- Handle Player Death Animations and Timers ---
        if player_is_dead:
            # 1. Player death blinking animation (uses self.animation_timer)
            self.animation_timer += delta_time

            # 2. Initialize dedicated death message timer if not started
            if self._death_message_start_time == 0.0:
                self._death_message_start_time = current_time
                self.animation_state = PLAYER_DEATH_ANIMATION_STATE # Force animation state
                self._death_message_complete = False

        else:
            # Reset death message tracker if player is alive
            self._death_message_start_time = 0.0
            self._death_message_complete = False


    def trigger_animation(self, event_type: str):
        """
        Queues an animation sequence based on a combat event type.
        This method should be called by the main game loop immediately after
        a combat action occurs.
        """
        if event_type in [GameEvent.ATTACKED, GameEvent.ENEMY_ATTACKED, GameEvent.CAST_SPELL]:
            # Add the event to the queue
            self.animation_queue.append(event_type)


    def is_animating(self) -> bool:
        """
        Returns True if an animation is currently playing or is queued up to play.
        This will now return True while a message is actively being revealed.
        """
        # Check general animation state AND queue
        if self.animation_state or self.animation_queue:
            # If it's a message state, check if the message is fully displayed.
            if self.animation_state == PLAYER_DEATH_ANIMATION_STATE:
                # Keep animating until message is complete.
                return not self._death_message_complete

            # Check if victory message is still revealing OR if the HP bar is still draining
            if self.animation_state == VICTORY_ANIMATION_STATE:
                # Keep animating until message is complete AND smoothed HP is at 0
                return not self._victory_message_complete or self._enemy_display_hp > 0.0

            return True

        # If all checks fail
        return False


    def _get_animation_frame(self, target_event: str, is_death: bool = False) -> str:
        """Calculates the current frame of the animation."""
        if is_death:
            # The blinking 'X' animation speed is controlled by the general timer
            frame_index = int((self.animation_timer / ANIMATION_DURATION) * len(DEATH_ANIMATION))
            return DEATH_ANIMATION[frame_index % len(DEATH_ANIMATION)]
        if self.animation_state == target_event:
            frame_index = int((self.animation_timer / ANIMATION_DURATION) * len(ATTACK_ANIMATION))
            return ATTACK_ANIMATION[frame_index % len(ATTACK_ANIMATION)]
        return ' '

    def _get_hp_color(self, health_ratio: float) -> str:
        """Returns the ANSI color code based on the health ratio."""
        if health_ratio > 0.5:
            return COLOR_GREEN
        elif health_ratio > 0.2:
            return COLOR_YELLOW
        else:
            return COLOR_RED

    def _get_animated_message_frame(self, message_list: List[str], state_attr: str) -> Tuple[str, bool]:
        """
        Animates a battle ending message (death or victory), typing it out.
        Returns the message frame and a boolean indicating if the message is complete.
        """
        import random
        message_key = f"_{state_attr}_message"

        # Determine which timer to use
        if state_attr == 'death':
            # Use the dedicated real-time start for death messages
            start_time = self._death_message_start_time
            elapsed = time.time() - start_time
            is_complete_attr = '_death_message_complete'
        else:
            # Use the animation_timer for victory messages
            start_time = 0.0
            elapsed = self.animation_timer
            is_complete_attr = '_victory_message_complete'

        # Select message only once
        if not hasattr(self, message_key):
            setattr(self, message_key, random.choice(message_list))

        message = getattr(self, message_key)

        # If the timer hasn't started, return early
        if start_time == 0.0 and state_attr == 'death':
            return ' ' * self.width, False

        # Animate typing: one char every 0.05s (20 chars per second)
        chars_per_sec = 20
        chars_to_show = min(int(elapsed * chars_per_sec), len(message))

        current_frame = message[:chars_to_show].ljust(self.width)

        # Check if the message is fully revealed
        is_complete = chars_to_show >= len(message)

        # Update the completion flag on the renderer instance
        setattr(self, is_complete_attr, is_complete)

        # The message is complete, but we still return the full message frame
        return current_frame, is_complete

    def _get_death_message_frame(self) -> str:
        """Helper to call the general animated message function for death."""
        frame, _ = self._get_animated_message_frame(DEATH_MESSAGES, 'death')
        return frame

    def _get_victory_message_frame(self) -> str:
        """Helper to call the general animated message function for victory."""
        frame, _ = self._get_animated_message_frame(VICTORY_MESSAGES, 'victory')
        return frame

    def _draw_player_info(self, player: Any) -> List[str]:
        """Renders the player's info block."""
        hp_bar_width = 15
        current_hp = getattr(player, 'hp', 0)

        # Use smoothed display HP and tracked max HP for bar calculation
        interp_hp = self._player_display_hp
        max_hp_for_bar = self._player_max_hp

        health_ratio = interp_hp / max_hp_for_bar if max_hp_for_bar > 0 else 0
        health_fill = int(health_ratio * hp_bar_width)

        # Determine color and apply to the bar content
        hp_color = self._get_hp_color(health_ratio)
        hp_bar_content = f"{HP_BAR_FILL_CHAR * health_fill}{'-' * (hp_bar_width - health_fill)}"
        hp_bar = f"[{hp_color}{hp_bar_content}{COLOR_RESET}]"

        # Death animation if player is dead
        is_dead = current_hp <= 0
        death_anim = self._get_animation_frame("", is_death=True) if is_dead else ""
        death_msg = f"\033[91m{self._get_death_message_frame()}\033[0m" if is_dead else ""

        # Note: Use the actual current_hp for the text display, but the smoothed interp_hp for the bar
        lines = [
            f" PLAYER: {getattr(player, 'name', 'Hero'):<{self.width - 12}} {death_anim}",
            f" LEVEL: {getattr(player, 'level', 1)}",
            f" HP: {current_hp}/{max_hp_for_bar} {hp_bar}",
            f" ATK: {getattr(player, 'attack', 10)} | DEF: {getattr(player, 'defense', 5)}",
        ]
        if is_dead:
            lines.append(death_msg)
        return [l.ljust(self.width) for l in lines]

    def _draw_enemy_info(self, enemy: Any) -> List[str]:
        """Renders the enemy's info block and ASCII art, handling victory state."""

        lines: List[str] = []
        # Check enemy HP directly
        is_enemy_alive = enemy and getattr(enemy, 'hp', 0) > 0
        is_victory_anim = self.animation_state == VICTORY_ANIMATION_STATE

        # Draw stats and bar if an enemy object exists AND either it's alive OR we're running the victory animation
        if enemy and (is_enemy_alive or is_victory_anim):

            # --- Enemy Stats and HP Bar ---
            # NOTE: current_hp will be 0 if the enemy is dead, but max_hp_for_bar keeps its old value
            current_hp = getattr(enemy, 'hp', 0)
            interp_hp = self._enemy_display_hp
            max_hp_for_bar = self._enemy_max_hp

            hp_bar_width = 15
            health_ratio = interp_hp / max_hp_for_bar if max_hp_for_bar > 0 else 0
            health_fill = int(health_ratio * hp_bar_width)

            # Determine color and apply to the bar content
            hp_color = self._get_hp_color(health_ratio)
            hp_bar_content = f"{HP_BAR_FILL_CHAR * health_fill}{'-' * (hp_bar_width - health_fill)}"
            hp_bar = f"[{hp_color}{hp_bar_content}{COLOR_RESET}]"

            lines.extend([
                f" ENEMY: {getattr(enemy, 'name', 'Monster'):<{self.width - 12}}",
                f" LEVEL: {getattr(enemy, 'level', 1)}",
                # Show actual HP/Max HP, but the bar shows the smooth drain (interp_hp)
                f" HP: {current_hp}/{max_hp_for_bar} {hp_bar}",
                f" ATK: {getattr(enemy, 'attack', 8)} | DEF: {getattr(enemy, 'defense', 3)}",
                "",
            ])

            # --- Enemy Art / Victory Message Area ---
            if is_victory_anim:
                # Victory Message (Trumps ASCII art)
                victory_msg = f"\033[92m{self._get_victory_message_frame()}\033[0m" # Green color for victory

                # Use fixed spacing to put the message in the "battle area"
                lines.extend([
                    f"{' ' * self.width}",
                    f"{' ' * self.width}",
                    f"{' ' * self.width}",
                    victory_msg,
                    f"{' ' * self.width}",
                    f"{' ' * self.width}",
                ])
                # Pad the rest of the lines
                while len(lines) < 8:
                    lines.append(' ' * self.width)

            else:
                # Enemy Art
                enemy_ascii_lines = getattr(enemy, 'ascii', " (?) ").split('\n')

                # The attack animation frame, placed next to the player/enemy
                player_attack_frame = self._get_animation_frame(GameEvent.ATTACKED)
                enemy_attack_frame = self._get_animation_frame(GameEvent.ENEMY_ATTACKED)

                for i, enemy_line in enumerate(enemy_ascii_lines):
                    # Add a small 'hit' animation on the first line when player attacks
                    anim_char = player_attack_frame if i == 0 else ' '

                    # Center the ASCII art in the remaining horizontal space
                    padding_left = (self.width - len(enemy_line) - 2) // 2

                    # Check for enemy attacking animation (e.g., for the 'mouth' or main body)
                    if i == 1:
                        anim_char = enemy_attack_frame

                    lines.append(f"{' ' * padding_left}{enemy_line} {anim_char}")

        # Fallback for when there is truly no enemy (and no victory animation)
        # We replace the removed [NO ENEMY] with blank space to maintain layout
        else:
            while len(lines) < 8:
                lines.append(' ' * self.width)

        return [l.ljust(self.width) for l in lines]


    def _draw_combat_log(self, log_source: list) -> List[str]:
        """Renders the combat log section with animated message reveal."""
        log_lines = [
            f"{'=' * self.width}",
            f" BATTLE LOG ".center(self.width, ' '),
            f"{'=' * self.width}",
        ]

        # Animate log: reveal one new message at a time
        if not hasattr(self, '_log_anim_index'):
            self._log_anim_index = 0
            self._log_anim_time = time.time()
        if len(log_source) > self._log_anim_index:
            if time.time() - self._log_anim_time > 0.5:  # 0.5s per message
                self._log_anim_index += 1
                self._log_anim_time = time.time()
        visible_log = log_source[-self._log_anim_index:] if self._log_anim_index > 0 else []

        # Only show up to COMBAT_LOG_LINES
        visible_log = visible_log[-COMBAT_LOG_LINES:]

        for line in visible_log:
            display_line = line[:self.width - 2]
            log_lines.append(f"> {display_line}".ljust(self.width))

        for _ in range(COMBAT_LOG_LINES - len(visible_log)):
            log_lines.append(' ' * self.width)

        log_lines.append(f"{'=' * self.width}")
        return log_lines

    def clear_animation_queue(self) -> None:
        """Clears any queued animations."""
        self.animation_queue.clear()
        self.animation_state = ""
        self.animation_timer = 0.0

    def combat_fn(self, game_ref: Any, combat_log: list) -> str:
        """
        The main rendering function, to be passed to the RenderPlugin.

        :param game_ref: The main Game object instance.
        :param combat_log: The list of combat messages.
        :return: A string representing the ASCII combat screen.
        """

        # Using the corrected attribute name from the user: 'enemy'
        player = getattr(game_ref, 'player', None)
        enemy = getattr(game_ref, 'enemy', None)

        frame: List[str] = []

        # Draw top border
        frame.append("#" * self.width)

        # Player Info (Left side of the screen)
        if player:
            player_info_lines = self._draw_player_info(player)
            frame.extend(player_info_lines)

        # Spacer
        frame.append("." * self.width)

        # Enemy Art and Info (Main battle area)
        enemy_art_and_info = self._draw_enemy_info(enemy)

        frame.extend(enemy_art_and_info)

        # Spacer
        frame.append("." * self.width)

        # Combat Log
        log_lines = self._draw_combat_log(combat_log)
        frame.extend(log_lines)

        # Pad with empty lines until the frame height is reached
        while len(frame) < self.height - 1:
            frame.append(' ' * self.width)

        # Draw bottom border
        frame.append("#" * self.width)

        return "\n".join(frame[:self.height])