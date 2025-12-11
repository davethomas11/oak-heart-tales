import time
from typing import List, Any

from engine.game.event import GameEvent

# --- Configuration Constants (Can be moved to a settings file if desired) ---
# The user-requested dimensions (40x60)
DEFAULT_HEIGHT = 40
DEFAULT_WIDTH = 60
COMBAT_LOG_LINES = 6

# A simple animation for an "attack" effect
ATTACK_ANIMATION = ["-", "\\", "|", "/"]
ANIMATION_DURATION = 0.3  # Seconds for a single animation cycle (e.g., 4 steps * 0.075s/step)


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

        # NEW: Queue to hold incoming combat events (animations)
        self.animation_queue: List[str] = []

        # NOTE: Combat log processing is assumed to be handled externally,
        # and the log list is accessible via game_ref.combat_log

    def update(self, game_ref: Any) -> None:
        """
        Updates the renderer state and manages animations.

        This method should be called regularly in the game loop to drive
        the animation timer and process the animation queue.
        """
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        # Update Animation Timer for the current animation
        if self.animation_state:
            self.animation_timer += delta_time
            if self.animation_timer > ANIMATION_DURATION:
                # Current animation finished
                self.animation_state = ""
                self.animation_timer = 0.0

        # NEW: Start the next animation if one is queued and the current one is finished
        if not self.animation_state and self.animation_queue:
            # Pop the next event from the queue (FIFO)
            self.animation_state = self.animation_queue.pop(0)
            self.animation_timer = 0.0


    def trigger_animation(self, event_type: str):
        """
        Queues an animation sequence based on a combat event type.
        This method should be called by the main game loop immediately after
        a combat action occurs.
        """
        if event_type in [GameEvent.ATTACKED, GameEvent.ENEMY_ATTACKED, GameEvent.CAST_SPELL]:
            # NEW: Add the event to the queue
            self.animation_queue.append(event_type)


    def is_animating(self) -> bool:
        """
        Returns True if an animation is currently playing or is queued up to play.
        This can be used by the main game loop to pause user input.
        """
        # NEW: Check both the currently playing animation AND the queue
        return bool(self.animation_state or self.animation_queue)


    def _get_animation_frame(self, target_event: str) -> str:
        """Calculates the current frame of the animation."""
        if self.animation_state == target_event:
            # Determine which frame of the animation to show
            frame_index = int((self.animation_timer / ANIMATION_DURATION) * len(ATTACK_ANIMATION))
            return ATTACK_ANIMATION[frame_index % len(ATTACK_ANIMATION)]
        return ' '

    def _draw_player_info(self, player: Any) -> List[str]:
        """Renders the player's info block."""

        # Assuming Player object has name, max_hp, and hp attributes.
        hp_bar_width = 15
        current_hp = getattr(player, 'hp', 0)
        max_hp = getattr(player, 'max_hp', 1)

        health_ratio = current_hp / max_hp if max_hp > 0 else 0
        health_fill = int(health_ratio * hp_bar_width)
        hp_bar = f"[{'#' * health_fill}{'-' * (hp_bar_width - health_fill)}]"

        lines = [
            f" PLAYER: {getattr(player, 'name', 'Hero'):<{self.width - 12}}",
            f" LEVEL: {getattr(player, 'level', 1)}",
            f" HP: {current_hp}/{max_hp} {hp_bar}",
            f" ATK: {getattr(player, 'attack', 10)} | DEF: {getattr(player, 'defense', 5)}",
        ]
        return [l.ljust(self.width) for l in lines]

    def _draw_enemy_info(self, enemy: Any) -> List[str]:
        """Renders the enemy's info block and ASCII art."""

        lines: List[str] = []
        if enemy and getattr(enemy, 'is_alive', lambda: False)():

            # Draw enemy stats
            current_hp = getattr(enemy, 'hp', 0)
            max_hp = getattr(enemy, 'max_hp', 1)
            hp_bar_width = 15
            health_ratio = current_hp / max_hp if max_hp > 0 else 0
            health_fill = int(health_ratio * hp_bar_width)
            hp_bar = f"[{'#' * health_fill}{'-' * (hp_bar_width - health_fill)}]"

            lines.extend([
                f" ENEMY: {getattr(enemy, 'name', 'Monster'):<{self.width - 12}}",
                f" LEVEL: {getattr(enemy, 'level', 1)}",
                f" HP: {current_hp}/{max_hp} {hp_bar}",
                f" ATK: {getattr(enemy, 'attack', 8)} | DEF: {getattr(enemy, 'defense', 3)}",
                "",
            ])

            # Draw ASCII art (Enemy art is assumed to be a multi-line string in enemy.ascii)
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
        else:
            lines.append(f"{' ' * ((self.width - 10) // 2)}[ NO ENEMY ]")

        return [l.ljust(self.width) for l in lines]


    def _draw_combat_log(self, log_source: list) -> List[str]:
        """Renders the combat log section."""

        log_lines = [
            f"{'=' * self.width}",
            f" BATTLE LOG ".center(self.width, ' '),
            f"{'=' * self.width}",
        ]

        # Display the last COMBAT_LOG_LINES messages
        visible_log = log_source[-COMBAT_LOG_LINES:]

        # Add messages, padding empty lines
        for line in visible_log:
            # Truncate long lines to fit within the width
            display_line = line[:self.width - 2]
            log_lines.append(f"> {display_line}".ljust(self.width))

        # Pad remaining lines if the log is too short
        for _ in range(COMBAT_LOG_LINES - len(visible_log)):
            log_lines.append(' ' * self.width)

        log_lines.append(f"{'=' * self.width}")
        return log_lines


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