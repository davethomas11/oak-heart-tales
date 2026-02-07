import json
import time
import threading
import sys
import os

# Cross-platform keypress detection
def getch():
    try:
        import termios
        import tty
        import select
        def _unix_getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                rlist, _, _ = select.select([fd], [], [], 0.1)
                if rlist:
                    ch = sys.stdin.read(1)
                    return ch
                return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return _unix_getch
    except ImportError:
        # Windows
        import msvcrt
        def _win_getch():
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8')
            return None
        return _win_getch
getch = getch()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_enemies(path):
    with open(path, 'r') as f:
        data = json.load(f)
    # Remove any trailing non-dict entries (e.g. the '4' at the end)
    return [e for e in data if isinstance(e, dict) and 'name' in e]

def find_enemy(enemies, name):
    for e in enemies:
        if e['name'].lower() == name.lower():
            return e
    return None

def print_enemy(enemy, left=False, padding: int = 0):
    """Prints the enemy art and stats, allowing for horizontal padding."""
    art_key = 'ascii_left' if left else 'ascii'
    art = enemy.get(art_key, " (?) ").split('\n')

    # Print the padded art
    for line in art:
        # Ensure padding doesn't push the text off-screen if art is wide
        print(f"{' ' * padding}{line}")

    # Print stats below the art
    print("-" * 20)
    print(f"Name: {enemy['name']}")
    print(f"HP: {enemy['base_hp']}  ATK: {enemy['base_attack']}  DEF: {enemy['base_defense']}")
    print(f"XP: {enemy['xp_reward']}  Gold: {enemy['gold_reward']}")
    print("(Press any key to stop)")

def walk_animation(enemy):
    """Animates the enemy moving back and forth across the screen."""
    MAX_PADDING = 40  # Maximum horizontal distance to cover
    ANIMATION_DELAY = 0.05

    padding = 0
    direction = 1 # 1 for right, -1 for left
    left_frame = False # Controls which ASCII art is used

    while not walk_animation.stop:
        clear() # Clear screen at start of frame draw

        # 1. Update position
        padding += direction
        if padding >= MAX_PADDING:
            direction = -1
            padding = MAX_PADDING
        elif padding <= 0:
            direction = 1
            padding = 0

        # 2. Update frame for walking look (switch frame every step)
        left_frame = not left_frame

        # 3. Render
        # Pass the calculated padding to print_enemy
        print_enemy(enemy, left=left_frame, padding=padding)

        # 4. Delay
        time.sleep(ANIMATION_DELAY)

walk_animation.stop = False

def wait_for_keypress():
    while not walk_animation.stop:
        if getch():
            walk_animation.stop = True
            break
        time.sleep(0.05)

def main():
    # Assuming 'data/enemies.json' exists in the expected location for this demo
    try:
        enemies = load_enemies(os.path.join(os.path.dirname(__file__), 'data', 'enemies.json'))
    except FileNotFoundError:
        print("Error: Could not find 'data/enemies.json'.")
        return

    print("Available enemies:")
    for e in enemies:
        print(f"- {e['name']}")
    name = input("Enter enemy name: ").strip()
    enemy = find_enemy(enemies, name)
    if not enemy:
        print("Enemy not found.")
        return
    walk_animation.stop = False
    t = threading.Thread(target=walk_animation, args=(enemy,))
    t.daemon = True
    t.start()
    wait_for_keypress()
    # It's better to wait for the thread to finish cleanly
    t.join(timeout=0.1)
    clear()
    print(f"Demo ended for {enemy['name']}.")

if __name__ == "__main__":
    main()