Oakheart Tales — Tiny Text (Single Player)

A minimal text-based single-player MUD-like RPG you can run in a terminal.

Features
- Randomized world generated from JSON tilesets (size selectable on new game)
- Exploration (north/south/east/west)
- Random encounters while exploring and when resting in dangerous areas
- Turn-based combat (attack, defend, potion, flee)
- XP and level-up system with stat increases
- Simple inventory (healing potions) and gold
- Save/Load: saves the player and the entire world state to JSON

Requirements
- Python 3.8+ (tested conceptually with Python 3.11)

### UI One - Terminal Version

Run
- macOS/Linux:
  - python3 main.py
- Windows (depending on install):
  - py -3 main.py

---

## UI Two - Simple Browser-Based Version

Web Interface (Play in your Browser)
- Start the built-in web server:
  - python3 web.py
- Then open http://127.0.0.1:8000/ in your browser.
- Use the New Game or Load Game buttons. Move with the on-screen buttons or Arrow keys/WASD.
- The web UI uses the same save file (save.json).


---

### UI Three - Web Interface (React Version)

1\. **Install dependencies and build the React UI:**
```bash
cd react-ui
npm install
npm run build
```

2\. **Start the Python server:**
```bash
cd ..
python3 react.py
```

3\. **Open your browser and go to:**
```
http://127.0.0.1:3000/
```

You can now play the game in your browser using the React interface.

---

### UI Four - TKinter GUI Version (Experimental)

```bash
python3 simple_tk_window.py
```

Check install.sh for dependencies and installing tkinter on OSX. 
If you get errors about tkinter not being found, you may need to install it separately.
AI can help you install tkinter for you specific OS if needed.

---

Some Game Instructions

Start Menu
- N: New game (choose map size 3x3, 5x5, or 7x7)
- L: Load game (reads save.json)

Gameplay Commands
- n,s,e,w: Move north/south/east/west
- look: Describe your current location
- stats: Show your character sheet
- rest: Recover some HP (safe in village; risky elsewhere)
- inv: Show inventory
- save: Save the current game to save.json
- load: Load game from save.json (in-session)
- help: Show commands
- quit: Quit the game

Tips
- You start at a central village (safe). Rest there to recover and sometimes find a potion.
- Venture outward for tougher enemies and better rewards.
- Leveling up restores your HP and improves your stats.

Notes
- The code is split into modules to make it easier to swap the renderer later.
 - A minimal WSGI web UI is provided in web.py with zero external dependencies.