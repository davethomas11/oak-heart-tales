
#!/usr/bin/env python3
"""
Oakheart Tales: Tkinter GUI Edition (Button-Based)
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import List
import sys
from json_loader import JsonLoader
from text_loader import TextLoader
from engine.game import Game
from persistence import save_game, load_game, SAVE_FILE


class MudGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Oakheart Tales")
        self.game = None
        self.choosing_map_size = False

        # Banner
        self.banner_label = tk.Label(root, text="Oakheart Tales", font=("Helvetica", 16))
        self.banner_label.pack(pady=10)

        # Output area
        self.output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=30, state=tk.DISABLED)
        self.output.pack(padx=10, pady=10)

        # Dynamic actions frame
        self.actions_frame = tk.Frame(root)
        self.actions_frame.pack(pady=10)

        # Control buttons
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        self.load_btn = tk.Button(control_frame, text="Load Game", command=self.load_game)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.quit_btn = tk.Button(control_frame, text="Close Window", command=self.root.quit)
        self.quit_btn.pack(side=tk.LEFT, padx=5)

        # Start menu
        self.start_menu()

    def start_menu(self):
        self.write("Welcome to Oakheart Tales!\nChoose an option:")
        self.render_actions([
            {"id": "new", "label": "New Game", "enabled": True}
        ])

    def write(self, text: str):
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state=tk.DISABLED)

    def get_color_for_category(self, cat):
        colors = {
            "general": "#4CAF50",     # green
            "combat": "#F44336",      # red
            "game_over": "#616161",   # dark gray
            "shop": "#FF9800",        # orange
            "start_menu": "#3F51B5",  # indigo
            "question": "#9C27B0",    # purple
            "travel": "#2196F3",      # blue
            "info": "#009688",        # teal
            "camp": "#795548",        # brown
            "town": "#03A9F4",        # light blue
            "system": "#9E9E9E",      # gray
        }
        return colors.get(cat.lower(), "#4CAF50")  # default green


    def render_actions(self, actions):

        grouped = {}
        for a in actions:
            cat = a.get("category", "General")
            grouped.setdefault(cat, []).append(a)

        # Clear previous buttons
        for widget in self.actions_frame.winfo_children():
            widget.destroy()

        for cat, lst in grouped.items():
            group_frame = tk.LabelFrame(self.actions_frame, text=cat.capitalize(), padx=5, pady=5)
            group_frame.pack(fill="x", pady=5)

            max_per_row = 5
            for idx, a in enumerate(lst):
                row = idx // max_per_row
                col = idx % max_per_row
                btn = tk.Button(
                    group_frame,
                    text=a["label"],
                    fg=self.get_color_for_category(cat),
                    highlightthickness=0,
                    font=("Helvetica", 12),
                    state=tk.NORMAL if a.get("enabled", True) else tk.DISABLED,
                    command=lambda action_id=a["id"]: self.do_action(action_id)
                )
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                # btn.pack(side=tk.LEFT, padx=5, pady=5)

            # Make columns expand evenly
            for col in range(max_per_row):
                self.actions_frame.grid_columnconfigure(col, weight=1)

    def do_action(self, action_id: str):
        if self.choosing_map_size:
            size = int(action_id)
            self.choosing_map_size = False
            self.start_new_game(size)
            return

        if not self.game:
            # Handle start menu actions
            if action_id == "new":
                self.choose_map_size()
            elif action_id == "load":
                self.load_game()
            elif action_id == "quit":
                self.root.quit()
            return

        # Execute game action
        output = self.game.execute_action(action_id) or "Unknown action."
        self.write(output)

        if self.game.ended:
            self.render_actions([
                {"id": "load", "label": "Load Game", "enabled": True},
                {"id": "restart", "label": "Restart", "enabled": True},
                {"id": "quit", "label": "Quit", "enabled": True},
            ])
            self.game = None
            return

        # Refresh actions dynamically
        actions = self.game.available_actions()
        self.render_actions(actions)

    def choose_map_size(self):
        self.write("Choose map size:")
        self.choosing_map_size = True
        self.render_actions([
            {"id": "3", "label": "3x3", "enabled": True},
            {"id": "5", "label": "5x5", "enabled": True},
            {"id": "7", "label": "7x7", "enabled": True},
            {"id": "9", "label": "9x9", "enabled": True},
        ])

    def save_game(self):
        if self.game:
            save_game(self.game.to_dict(), SAVE_FILE)
            messagebox.showinfo("Save Game", "Game saved successfully!")
        else:
            messagebox.showwarning("Save Game", "No game in progress to save.")

    def load_game(self):
        loaded = load_game(SAVE_FILE)
        if loaded:
            self.game = Game.from_dict(loaded)
            self.write(self.game.look())
            self.render_actions(self.game.available_actions())
        else:
            messagebox.showerror("Load Game", "No save found or save file invalid.")
            self.start_menu()

    def start_new_game(self, size: int):
        data_loader = JsonLoader()
        tiles = data_loader.load("data/tileset.json")
        self.game = Game.new_random(size=size, tiles=tiles)
        self.game.data_loader = JsonLoader()
        self.game.load_configurations("data/enemies.json")
        self.game.ascii_loader = TextLoader("data/rooms")
        self.game.load_fn = load_game
        self.game.save_fn = save_game
        self.game.save_file = SAVE_FILE
        self.write(self.game.look())
        self.render_actions(self.game.available_actions())


def main(argv: List[str]) -> int:
    root = tk.Tk()
    app = MudGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
