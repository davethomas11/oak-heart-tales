import random
from typing import List, Any

# --- Configuration Constants (Copied from main renderer for consistency) ---
DEFAULT_WIDTH = 30

# NEW: Question Renderer Constants
QUESTION_BOX_HEIGHT = 8 # Height of the question art box (excluding borders)
QUESTION_WEAPONS = [
    # Simple ASCII Sword
    [
        " /|\\ ",
        "  |  ",
        "  |  ",
        "  |  "
    ],
    # Simple ASCII Axe
    [
        " ( ) ",
        " /|  ",
        "  |  ",
        "  |  "
    ]
]
BIG_QUESTION_MARK = [
    " $$$ ",
    "  $$ ",
    "   @ ",
    "     ",
    "   @ "
]


class ASCIIQuestionRenderer:


    """
    A renderer dedicated to generating the ASCII art header for player prompts.
    This art is intended to be displayed immediately before the question text.
    """
    def __init__(self, question_type: str = "weapon_find", width: int = DEFAULT_WIDTH):
        self.question_type = question_type
        self.width = width

    def _draw_question_art(self) -> List[str]:
        """Renders random ASCII art for the question screen."""
        lines: List[str] = ['=' * self.width]

        # QUESTION_BOX_HEIGHT lines of space or art elements
        art_lines = [' ' * self.width] * QUESTION_BOX_HEIGHT

        # 1. Place a random weapon on the left
        weapon = random.choice(QUESTION_WEAPONS)
        w_start = 2 # Start column for weapon
        w_line_start = 1 # Start line for weapon

        for i, w_line in enumerate(weapon):
            # Only draw if within bounds
            if w_line_start + i < QUESTION_BOX_HEIGHT - 1:
                # Replace a segment of the blank line with the weapon art
                current_line = list(art_lines[w_line_start + i])
                current_line[w_start:w_start + len(w_line)] = list(w_line)
                art_lines[w_line_start + i] = "".join(current_line)

        # 2. Place a large question mark in the center
        qm_start = (self.width - len(BIG_QUESTION_MARK[0])) // 2
        qm_line_start = 1

        for i, qm_line in enumerate(BIG_QUESTION_MARK):
            if qm_line_start + i < QUESTION_BOX_HEIGHT - 1:
                current_line = list(art_lines[qm_line_start + i])
                current_line[qm_start:qm_start + len(qm_line)] = list(qm_line)
                art_lines[qm_line_start + i] = "".join(current_line)


        lines.extend([l.ljust(self.width) for l in art_lines])
        lines.append('=' * self.width)

        # Add a clear separator for the prompt itself
        lines.append(f" QUESTION ".center(self.width, '-'))
        lines.append('-\n' * self.width)

        if self.question_type == "weapon_find":
            prompt = "You have found a new weapon!\n What will you do?"
        else:
            prompt = "You have a question to answer! What will you do?"
        lines.append(prompt.center(self.width))
        lines.append('-' * self.width)

        return lines

    def question_fn(self) -> str:
        """
        The main rendering function for the question screen art.
        Returns a string of ASCII art for the header box.
        """
        frame: List[str] = self._draw_question_art()
        return "\n".join(frame)