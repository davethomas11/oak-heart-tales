class Controls:
    def __init__(self, mapping: dict, description: str):
        self.mapping = mapping
        self.description = description

default_controls = Controls(
    mapping={
        'a': 'left',
        'd': 'right',
        'w': 'jump',
        ' ': 'jump',
        'q': 'quit',
        '\x1b[D': 'left',  # Left arrow
        '\x1b[C': 'right',  # Right arrow
        '\x1b[A': 'jump',  # Up arrow
    },
    description="Controls: a/d or Arrows (Move), w/space or Up Arrow (Jump), q (Quit)"
)

class TerminalInputHandler:

    def __init__(self):
        self.controls = default_controls
        self.control_modifiers = set()
        import termios
        import sys
        self.ORIGINAL_TERMIOS_SETTINGS = termios.tcgetattr(sys.stdin)
        try:
            self.turn_on()
        except termios.error as e:
            print(f"Error setting terminal mode: {e}. Check if you are running in a restricted environment.")
            # Restore original settings before exit
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.ORIGINAL_TERMIOS_SETTINGS)
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.ORIGINAL_TERMIOS_SETTINGS)
            return

    def is_off(self):
        import termios
        import sys
        current_settings = termios.tcgetattr(sys.stdin)
        return current_settings == self.ORIGINAL_TERMIOS_SETTINGS

    def turn_on(self):
        import sys
        import tty
        tty.setcbreak(sys.stdin)

    def restore(self):
        import termios
        import sys
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.ORIGINAL_TERMIOS_SETTINGS)

    def get_single_key(self):
        import sys
        import select
        """Reads a single character from stdin instantly."""
        try:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1)
        except Exception:
            pass
        return None

    def get_input(self):
        import sys
        import select

        action = None
        key = self.get_single_key()

        if key is not None:
            # --- FIX: Restore Multi-character escape sequence (Arrow Keys) Logic ---
            # Check for the start of an escape sequence
            if key == '\x1b':
                # Read up to 2 more characters to get the full sequence (e.g., \x1b[D)
                if sys.stdin in select.select([sys.stdin], [], [], 0.01)[0]:
                    key += sys.stdin.read(1)
                    if sys.stdin in select.select([sys.stdin], [], [], 0.01)[0]:
                        key += sys.stdin.read(1)
            # --- END Arrow Key Logic ---

            if key in self.controls.mapping:
                action = self.controls.mapping[key]

            for modifier in self.control_modifiers:
                if key in modifier.mapping:
                    action = modifier.mapping[key]

        return action

    def add_modifier(self, controls: Controls):
        self.control_modifiers.add(controls)

    def clear_modifiers(self):
        self.control_modifiers.clear()

    def get_controls(self):
        return self.controls.description + ''.join(
            f" Others: {mod.description}" for mod in self.control_modifiers
        )

    def print_controls(self):
        print(self.get_controls())