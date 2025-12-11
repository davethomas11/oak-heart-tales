# engine/plugins/game2d.py

import random
import time

try:
    from engine.game.enemy import Enemy as EnemyModel
    from engine.game.event import EventManager, GameEvent
except ImportError:
    class EnemyModel:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def to_dict(self):
            return self.__dict__


    class GameEvent:
        def __init__(self, event_type, data=None):
            self.event_type = event_type
            self.data = data or {}


    class EventManager:
        def __init__(self):
            pass

        def emit(self, event: GameEvent):
            pass

# --- Global Input State Buffer ---
# Not used in the tap-based model, but kept for clarity.
LAST_MOVEMENT_ACTION = None

EVENT_ROOM_ENTERED = "room_entered"
EVENT_ENTER_COMBAT = "enter_combat"


# --- Utility Function ---
def is_passable(grid, x, y):
    """Check if a coordinate is within bounds and is a space ('.') or a door ('D')."""
    height = len(grid)
    width = len(grid[0])
    if 0 <= y < height and 0 <= x < width:
        return grid[y][x] in (".", "D")
    return False


# --- Core Game Classes ---

class Room2D:
    def __init__(self, room_id, width=15, height=8, has_door_up=False, has_door_down=False, has_door_left=True,
                 has_door_right=True, enemies=None):
        self.room_id = room_id
        self.width = width
        self.height = height
        # Doors now define connection points, not just top/bottom
        self.has_door_up = has_door_up
        self.has_door_down = has_door_down
        self.has_door_left = has_door_left
        self.has_door_right = has_door_right

        self.grid = [["." for _ in range(width)] for _ in range(height)]
        self.platforms = set()  # Use a set for faster lookup
        self.doors = {}  # Store door type and position: {'up': (x, y), ...}
        self.enemies = enemies or []
        self.player_start_x = 1
        self.player_start_y = height - 2  # Start just above the ground/platform

        self.generate_room()

    def generate_room(self):
        # Reset grid and platforms
        self.grid = [["." for _ in range(self.width)] for _ in range(self.height)]
        self.platforms = set()

        # 1. Place ground platform
        for x in range(self.width):
            self.grid[self.height - 1][x] = "P"
            self.platforms.add((x, self.height - 1))

        # 2. Place random floating platforms (Using previous, more robust logic)
        last_platform_x = self.width // 2
        last_platform_y = self.height - 1

        for _ in range(random.randint(1, 3)):
            x_offset = random.choice([random.randint(2, 4), random.randint(-4, -2)])
            new_x_start = last_platform_x + x_offset

            max_y = min(last_platform_y - 1, self.height - 2)
            min_y = max(1, last_platform_y - 3)

            if min_y > max_y:
                break

            new_y = random.randint(min_y, max_y)

            new_x_start = max(1, min(new_x_start, self.width - 4))
            length = random.randint(2, 4)

            for x in range(new_x_start, min(new_x_start + length, self.width - 1)):
                if self.grid[new_y][x] == ".":
                    self.grid[new_y][x] = "P"
                    self.platforms.add((x, new_y))

            last_platform_x = new_x_start + length // 2
            last_platform_y = new_y

        # 3. Place doors (Doors placed in walls/boundaries)
        self.doors = {}
        # Left Door
        if self.has_door_left:
            y = self.height // 2
            self.grid[y][0] = "<"  # Left door symbol
            self.doors['left'] = (0, y)
        # Right Door
        if self.has_door_right:
            y = self.height // 2
            self.grid[y][self.width - 1] = ">"  # Right door symbol
            self.doors['right'] = (self.width - 1, y)
        # Up/Down Doors (Unused in linear room movement, but kept for future)
        if self.has_door_up:
            self.grid[0][self.width // 2] = "D"
            self.doors['up'] = (self.width // 2, 0)
        if self.has_door_down:
            self.grid[self.height - 1][self.width // 2] = "D"
            self.doors['down'] = (self.width // 2, self.height - 1)

        # 4. Place enemies (Called after grid generation)
        self.place_enemies()

    def place_enemies(self):
        """Places enemies onto empty spots in the grid."""
        for enemy in self.enemies:
            # Find a random valid spawn spot
            tries = 0
            while tries < 100:
                x = random.randint(1, self.width - 2)
                y = random.randint(self.height - 4, self.height - 2)
                # Ensure spot is clear and has a platform/ground below it
                if self.grid[y][x] == "." and (x, y + 1) in self.platforms:
                    # Enemy symbol 'E' is drawn by render_room, not stored in grid
                    enemy.x = x
                    enemy.y = y
                    break
                tries += 1
            if tries == 100:
                # Fallback placement if no good spot is found
                enemy.x = random.randint(1, self.width - 2)
                enemy.y = self.height - 2

    def spawn_enemies(self, enemy_archetypes, player_level, max_enemies=2):
        """Creates new enemies for the room."""
        self.enemies = []
        for _ in range(random.randint(1, max_enemies)):
            enemy = random.choice(enemy_archetypes)
            self.enemies.append(
                EnemyModel(
                    name=enemy["name"],
                    ascii=enemy.get("ascii", " _ \n( E)\n ~ \n / \\"),
                    ascii_left=enemy.get("ascii_left", "(E )\n ~ \n / \\"),
                    level=player_level,
                    max_hp=enemy.get("base_hp", 10) + player_level * 2,
                    hp=enemy.get("base_hp", 10)+ player_level * 2,
                    attack=enemy.get("base_attack", 1) + player_level,
                    defense=enemy.get("base_defense", 1) + player_level // 2,
                    xp_reward=enemy.get("xp_reward", 10) * player_level // 2,
                    gold_reward=enemy.get("gold_reward", 25) + player_level,
                    direction=random.choice([-1, 1])  # Added direction for enemy movement
                )
            )
        self.place_enemies()  # Only place enemies, don't regenerate entire room


class Player2D:
    def __init__(self, x, y):
        self.x = float(x)  # Store as float for physics
        self.y = float(y)  # Store as float for physics
        self.dx = 0.0  # Horizontal velocity (not used in tap-based model)
        self.dy = 0.0  # Vertical velocity
        self.speed = 1.0
        self.is_jumping = False
        self.direction = 1


class Game2DPlugin:
    def __init__(self, num_rooms=3, room_width=15, room_height=8, enemy_archetypes=None, player_level=1,
                 gravity_pull=0.20, terminal_velocity=3.0):
        self.rooms = []
        self.safe_rooms = [False] * num_rooms
        self.num_rooms = num_rooms
        self.current_room_idx = 0
        self.enemy_archetypes = enemy_archetypes or [{"name": "Goblin"}]
        self.player_level = player_level

        # Physics properties
        self.gravity_pull = gravity_pull
        self.terminal_velocity = terminal_velocity
        self.jump_velocity = 2.0  # Fixed jump speed
        self.enemy_speed_divider = 7
        self.enemy_move_counter = 0
        self.ignore_combat = False
        self._generate_rooms(num_rooms, room_width, room_height)

        # Player starts in the first room's designated start position
        start_room = self.rooms[0]
        self.player = Player2D(start_room.player_start_x, start_room.player_start_y)
        self.state = "exploring"  # 'exploring', 'combat', 'game_over', 'win'
        self.combat_enemy = None
        self.event_manager = EventManager()

    def _generate_rooms(self, num_rooms, width, height):
        for i in range(num_rooms):
            # Connect rooms linearly
            has_door_left = i > 0
            has_door_right = i < num_rooms - 1

            room = Room2D(
                i,
                width,
                height,
                has_door_left=has_door_left,
                has_door_right=has_door_right,
                has_door_up=False,
                has_door_down=False
            )
            room.spawn_enemies(self.enemy_archetypes, self.player_level)
            self.rooms.append(room)

    def make_room_safe(self, room_idx):
        """Removes all enemies from the specified room."""
        if 0 <= room_idx < self.num_rooms:
            self.safe_rooms[room_idx] = True
            self.rooms[room_idx].enemies = []

    def remove_battle_enemy(self):
        """Removes the current combat enemy from the room after combat ends."""
        room = self.get_current_room()
        if self.combat_enemy in room.enemies:
            room.enemies.remove(self.combat_enemy)
        self.combat_enemy = None

    def explore(self):
        """Sets the game state back to exploring."""
        self.state = "exploring"

    def get_current_room(self):
        return self.rooms[self.current_room_idx]

    def move_player(self, action):
        room = self.get_current_room()
        # Initial positions for checks like jumping
        player_x_int_old = round(self.player.x)
        player_y_int = round(self.player.y)

        # --- Handle Jumping ---
        if action == "jump":
            # Check if player is on a platform/ground before jumping
            if (player_x_int_old, player_y_int + 1) in room.platforms:
                self.player.dy = -self.jump_velocity  # Set upward velocity
                self.player.is_jumping = True
                return

        # --- Handle Horizontal Movement (Single discrete step) ---
        new_x_float = self.player.x
        if action == "left":
            self.player.direction = -1
            new_x_float = self.player.x - 1.0
        elif action == "right":
            self.player.direction = 1
            new_x_float = self.player.x + 1.0

        new_x_int = round(new_x_float)

        # Check boundary and platform collision
        if 0 <= new_x_int < room.width:
            if (new_x_int, player_y_int) not in room.platforms:
                self.player.x = new_x_float

        # --- Check for Room Transition (Doors) ---
        player_x_int_for_door_check = round(new_x_int)

        if player_x_int_for_door_check is not None:
            # Left door check
            door_x_left, door_y_left = room.doors.get('left', (None, None))
            if door_x_left is not None and player_x_int_for_door_check < door_x_left and self.current_room_idx > 0:
                self.current_room_idx -= 1
                new_room = self.get_current_room()
                self.event_manager.emit(GameEvent(EVENT_ROOM_ENTERED, {"room_id": new_room.room_id, "index": self.current_room_idx}))
                # Set player start position in the new room at the entry door
                self.player.x = float(new_room.width - 1)
                self.on_player_enter_room(self.current_room_idx)

            # Right door check
            door_x_right, door_y_right = room.doors.get('right', (None, None))
            if door_x_right is not None and player_x_int_for_door_check > door_x_right and self.current_room_idx < self.num_rooms - 1:
                self.current_room_idx += 1
                new_room = self.get_current_room()
                self.event_manager.emit(GameEvent(EVENT_ROOM_ENTERED, {"room_id": new_room.room_id, "index": self.current_room_idx}))
                # Set player start position in the new room at the entry door
                self.player.x = 0.0
                self.on_player_enter_room(self.current_room_idx)

    def on_player_enter_room(self, room_idx):
        """Event handler for when the player enters a new room."""
        if self.safe_rooms[room_idx]:
            return  # No enemies to spawn in safe rooms

        if 0 <= room_idx < self.num_rooms:
            room = self.rooms[room_idx]
            room.spawn_enemies(self.enemy_archetypes, self.player_level)

    def update(self, action=None):
        """Main update loop handling movement, physics, and state transitions."""
        room = self.get_current_room()
        player_x_int = round(self.player.x)

        if self.state != "exploring":
            return self.get_state()

        # If an action is present, the discrete movement (tap, jump) is handled by main() calling handle_input()

        # --- Physics Update (Gravity and Jump) ---

        # 1. Apply gravity/jump velocity to Y position
        if self.player.dy < self.terminal_velocity:
            self.player.dy += self.gravity_pull  # Gravity pulls player down

        new_y = self.player.y + self.player.dy
        y_start = round(self.player.y)
        y_end = round(new_y)

        # 2. Check for Vertical Collision (Falling/Landing)
        next_platform_y = -1
        # Check all cells between current Y and new Y for platforms
        for y_check in range(y_start + 1, min(y_end + 2, room.height)):
            if (player_x_int, y_check) in room.platforms:
                next_platform_y = y_check
                break

        if next_platform_y != -1:
            # Landed on a platform
            self.player.y = float(next_platform_y - 1)  # Place player just above the platform
            self.player.dy = 0.0
            self.player.is_jumping = False
        elif new_y >= room.height - 1:
            # Hit the ground
            self.player.y = float(room.height - 2)  # Place player just above the ground block
            self.player.dy = 0.0
            self.player.is_jumping = False
        else:
            # No collision, allow vertical movement
            self.player.y = new_y

        # 3. Enemy Movement (Simple left/right patrol)
        self.enemy_move_counter = (self.enemy_move_counter + 1) % self.enemy_speed_divider

        if self.enemy_move_counter == 0:
            for enemy in room.enemies:
                if hasattr(enemy, "x") and hasattr(enemy, "y") and hasattr(enemy, "direction"):

                    next_x = enemy.x + enemy.direction

                    is_blocked = next_x <= 0 or next_x >= room.width - 1 or (next_x, enemy.y) in room.platforms
                    is_dropoff = (next_x, enemy.y + 1) not in room.platforms

                    if is_blocked or is_dropoff:
                        enemy.direction *= -1

                    next_x_after_check = enemy.x + enemy.direction
                    if 0 < next_x_after_check < room.width - 1 and (next_x_after_check, enemy.y + 1) in room.platforms:
                        enemy.x = next_x_after_check

        # --- Combat Check ---
        if not self.ignore_combat:
            for enemy in room.enemies:
                # Collision detected: Player and enemy occupy the same space
                if player_x_int == enemy.x and round(self.player.y) == enemy.y:
                    self.state = "combat"
                    self.combat_enemy = enemy
                    self.event_manager.emit(GameEvent(EVENT_ENTER_COMBAT, {"enemy": enemy.to_dict()}))
                    break

        return self.get_state()

    def handle_input(self, action):
        """Exposed function for user input."""
        return self.move_player(action)

    def get_state(self):
        room = self.get_current_room()
        return {
            "room_id": room.room_id,
            "player": {"x": round(self.player.x), "y": round(self.player.y)},
            "enemies": [{"name": e.name, "hp": e.hp, "x": e.x, "y": e.y} for e in room.enemies],
            "state": self.state
        }


# --- 4x4 Character Definitions (Pixel Art Maps) ---
CHAR_MAP = {
    # Empty Space (Air) - Mostly clear
    ".": [
        "    ",
        "    ",
        "    ",
        "    "
    ],
    # Platform (Ground) - Solid block
    "P": [
        "████",
        "████",
        "████",
        "████"
    ],
    # Player (@) - Simple 4x4 character sprite
    "@": [
        "  . ",
        " /@\\",
        " /\\/",
        " || "
    ],
    "@L": [
        " .  ",
        "/@\\ ",
        "\\/\\ ",
        " || "
    ],
    # Enemy (E) - Simple 4x4 sprite
    "E": [
        " /\\ ",
        " E  ",
        "||\\ ",
        "\\/  "
    ],
    # Door Up/Down (D) - Vertical boundary symbol
    "D": [
        "||||",
        "|  |",
        "|__|",
        "|  |"
    ],
    # Door Left (<) - Entry/Exit point
    "<": [
        " /  ",
        "< > ",
        " \\  ",
        "    "
    ],
    # Door Right (>) - Entry/Exit point
    ">": [
        "  \\ ",
        "< > ",
        "  / ",
        "    "
    ]
}
# Fallback map for unknown characters
FALLBACK_MAP = [
    "????",
    "?  ?",
    "?  ?",
    "????"
]


# Ascii rendering function
def render_room(room, player):
    """
    Render the room as high-resolution ASCII art using 4x4 blocks per grid cell.
    Enemies are rendered using their own ascii art, centered horizontally
    and aligned to the bottom (floor) of their cell.
    """
    # 1. Create the base grid
    display_grid = [row[:] for row in room.grid]

    # Use rounded position for display
    player_x = round(player.x)
    player_y = round(player.y)
    player_pos = (player_x, player_y)

    # 2. Build a map of enemy positions, their ascii art, AND required cell width
    enemy_ascii_map = {}
    cell_width_map = {}

    # Initialize all cell widths to 4
    for y in range(room.height):
        for x in range(room.width):
            cell_width_map[(x, y)] = 4

    # Determine enemy art and update cell widths
    for enemy in room.enemies:
        x, y = round(enemy.x), round(enemy.y)
        if 0 <= y < room.height and 0 <= x < room.width:
            ascii_art = getattr(enemy, "ascii", None)
            ascii_art_left = getattr(enemy, "ascii_left", None)
            # Choose left or right facing art based on direction
            if hasattr(enemy, "direction") and enemy.direction < 0 and ascii_art_left:
                ascii_art = ascii_art_left
            if ascii_art and isinstance(ascii_art, str):
                ascii_art = ascii_art.splitlines()

            if ascii_art and isinstance(ascii_art, list) and ascii_art:
                enemy_ascii_map[(x, y)] = ascii_art
                # The cell width must be at least 4, or the width of the widest line
                max_enemy_width = max(len(line) for line in ascii_art)
                cell_width_map[(x, y)] = max(4, max_enemy_width)
            else:
                # Use a default 4x4 map if no custom art is provided or if it's invalid
                enemy_ascii_map[(x, y)] = CHAR_MAP.get("E", FALLBACK_MAP)
                cell_width_map[(x, y)] = 4

    # Player position required width is 4 (or more if standing on an oversized enemy cell)
    if player_pos not in cell_width_map:
        cell_width_map[player_pos] = 4

    # 3. Render the room line by line
    rendered_output = []
    for y in range(room.height):
        # Determine the max height for this *grid* row
        max_cell_height = 4 # Minimum height is 4
        if player_pos[1] == y:
            max_cell_height = max(max_cell_height, 4)

        for x in range(room.width):
            if (x, y) in enemy_ascii_map:
                max_cell_height = max(max_cell_height, len(enemy_ascii_map[(x, y)]))

        # Iterate over the sub-rows (i) determined by max_cell_height
        for i in range(max_cell_height):
            line_parts = []
            for x in range(room.width):
                # Get the required width for this specific cell
                cell_width = cell_width_map.get((x, y), 4)

                # Player takes precedence
                if (x, y) == player_pos:
                    char_map = CHAR_MAP.get("@", FALLBACK_MAP)
                    if player.direction < 0:
                        char_map = CHAR_MAP.get("@L", FALLBACK_MAP)
                    player_art_line = char_map[i] if i < len(char_map) else " " * 4
                    player_art_width = 4

                    # Calculate padding to center the 4-wide player art
                    pad = max(0, cell_width - player_art_width)
                    left_pad = pad // 2
                    right_pad = pad - left_pad

                    line = " " * left_pad + player_art_line + " " * right_pad
                    line_parts.append(line[:cell_width])

                elif (x, y) in enemy_ascii_map:
                    ascii_art = enemy_ascii_map[(x, y)]
                    enemy_art_height = len(ascii_art)

                    # --- FIX FOR BOTTOM ALIGNMENT ---
                    # Calculate the index of the enemy's ASCII line to use for the current sub-row (i).
                    # This offset determines how many blank lines to render at the top.

                    # `i` is the current sub-row index (0 to max_cell_height - 1)
                    # `enemy_line_index` is the index into the enemy's art (0 to enemy_art_height - 1)

                    # If max_cell_height is 4 and enemy_art_height is 3:
                    # Row i=0: index = 0 - 1 = -1 (Blank space)
                    # Row i=1: index = 1 - 1 = 0 (Enemy line 0)
                    # Row i=2: index = 2 - 1 = 1 (Enemy line 1)
                    # Row i=3: index = 3 - 1 = 2 (Enemy line 2)

                    # If max_cell_height is 5 and enemy_art_height is 3:
                    # Row i=0: index = 0 - 2 = -2 (Blank space)
                    # Row i=1: index = 1 - 2 = -1 (Blank space)
                    # Row i=2: index = 2 - 2 = 0 (Enemy line 0)
                    # ...

                    offset = max_cell_height - enemy_art_height
                    enemy_line_index = i - offset

                    if 0 <= enemy_line_index < enemy_art_height:
                        # Render the actual enemy line, centered horizontally
                        enemy_art_line = ascii_art[enemy_line_index]

                        # Calculate padding to center the enemy art in the cell_width
                        pad = max(0, cell_width - len(enemy_art_line))
                        left_pad = pad // 2
                        right_pad = pad - left_pad

                        line = " " * left_pad + enemy_art_line + " " * right_pad
                        line_parts.append(line[:cell_width])
                    else:
                        # Render blank space for rows above the enemy art
                        line_parts.append(" " * cell_width)

                else:
                    # Regular room content (Platform, Door, Empty)
                    char = display_grid[y][x]
                    char_map = CHAR_MAP.get(char, FALLBACK_MAP)

                    # Align regular 4x4 art to the bottom by checking the index against the height difference
                    regular_art_height = len(char_map) # Assume 4 for 4x4

                    # The content should only be drawn if the current sub-row index 'i'
                    # is within the range of the content's art lines, offset from the bottom.
                    offset = max_cell_height - regular_art_height
                    regular_line_index = i - offset

                    if 0 <= regular_line_index < regular_art_height:
                        regular_art_line = char_map[regular_line_index]
                        regular_art_width = 4

                        # Pad the 4-wide art to the cell_width (which is 4 here unless an oversized enemy
                        # expanded the column, in which case the 4x4 art is centered in the wider space).
                        pad = max(0, cell_width - regular_art_width)
                        left_pad = pad // 2
                        right_pad = pad - left_pad

                        line = " " * left_pad + regular_art_line + " " * right_pad
                        line_parts.append(line[:cell_width])
                    else:
                        # Render blank space for rows above the 4x4 art
                        line_parts.append(" " * cell_width)

            rendered_output.append("".join(line_parts))

    return "\n".join(rendered_output)

    return "\n".join(rendered_output)

def print_details(room, player, state):
    print("-" * (room.width * 4))  # Separator line based on the rendered width
    print(f"Room: {room.room_id} | Player @ ({player.x}, {player.y}) | State: {state}")


def print_minimap(plugin):
    """
    Renders a simple linear minimap of the rooms.
    """
    map_parts = []
    # Use width to calculate padding for centering the map roughly
    room_width_chars = plugin.get_current_room().width * 4
    map_width = plugin.num_rooms * 3  # 3 characters per room: [, @, ]
    padding = max(0, (room_width_chars - map_width) // 2)

    for i in range(plugin.num_rooms):
        if i == plugin.current_room_idx:
            map_parts.append("[@]")
        else:
            map_parts.append("[ ]")

    print(" " * padding + "Minimap: " + "".join(map_parts))

# --- Main function using tty/termios for non-blocking input ---
def main():
    import os
    from terminal_input_handler import TerminalInputHandler
    terminal_input = TerminalInputHandler()

    # 1. Initialize the game
    plugin = Game2DPlugin(num_rooms=3, room_width=15, room_height=8)
    plugin.ignore_combat = True  # Disable combat for this demo
    clear_command = "cls" if os.name == "nt" else "clear"

    print("--- 2D Platformer Game (Terminal Raw Mode) ---")
    terminal_input.print_controls()

    try:
        while plugin.state not in ("game_over", "win"):
            # 1. Process Input (Non-blocking check)
            action = terminal_input.get_input()

            # Handle quit immediately
            if action == 'quit':
                break

            # 2. Update Game State (Applies physics/gravity)
            plugin.update()

            if plugin.state == "combat":
                plugin.state = "exploring"

            # 3. Handle Discrete Actions (Movement, Jump, Transitions)
            if action in ('left', 'right', 'jump'):
                # In tap-based input, we handle the movement directly here.
                plugin.handle_input(action)

            # 4. Render
            os.system(clear_command)
            current_state_data = plugin.get_state()
            current_room = plugin.get_current_room()

            print(render_room(current_room, plugin.player))
            print_details(current_room, plugin.player, current_state_data["state"])
            print_minimap(plugin)

            # 5. Control Frame Rate
            time.sleep(0.05)

    except Exception as e:
        print(f"\nAn error occurred during the game loop: {e}")
    finally:
        # 6. Restore Terminal Settings (CRITICAL)
        terminal_input.restore()

    # Final messages
    os.system(clear_command)

    # FIX: Correct arguments for final render call
    final_state = plugin.get_state()["state"]
    final_room = plugin.get_current_room()

    print(render_room(final_room, plugin.player))
    print_details(final_room, plugin.player, final_state)
    print_minimap(plugin)  # Render minimap one last time

    if final_state == "win":
        print("\n✨ YOU WIN! ✨")
    elif final_state == "combat":
        print("\n⚔️ COMBAT ENGAGED! ⚔️")
    else:
        print("\nGame Over!")


if __name__ == "__main__":
    # Ensure MockEnemy is defined if running standalone
    class MockEnemy:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


    try:
        from engine.game.enemy import Enemy as EnemyModel
    except ImportError:
        # Fallback to MockEnemy if external module isn't available
        EnemyModel = MockEnemy

    main()
