# Oakheart Tales — Tiny Text (Single Player)

**Now available as UI version 6 — Vue.js fully front-end version!**  
Launch: [https://davethomas11.github.io/oak-heart-tales/](https://davethomas11.github.io/oak-heart-tales/)

A minimal text-based single-player MUD-like RPG playable in the terminal or browser.

---

## Features

- Randomized world from JSON tilesets (selectable size)
- Exploration (north/south/east/west)
- Random encounters and turn-based combat
- XP, level-up, and stat increases
- Simple inventory (healing potions) and gold
- Save/Load: player and world state to JSON

---

## Requirements

- Python 3.8+ (tested with Python 3.11)

---

## UI Versions

### 1. Terminal Version

**Run:**
- macOS/Linux:
  ```bash
  python3 main.py
  ```
- Windows:
  ```bash
  py -3 main.py
  ```

---

### 2. Simple Browser-Based Version

**Run:**
```bash
python3 web.py
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

### 3. React Web Interface

**Build and run:**
```bash
cd react-ui
npm install
npm run build
cd ..
python3 react.py
```
Open [http://127.0.0.1:3000/](http://127.0.0.1:3000/)

---

### 4. TKinter GUI Version

**Run:**
```bash
python3 simple_tk_window.py
```
See `install.sh` for dependencies and installing tkinter on macOS.

---

### 5. Node.js Console Version

**Build:**
```bash
cd nodejs
sh transcrypt.sh
```
**Run:**
```bash
cd nodejs
node index.js
```

---

### 6. Vue.js Fully Front-End Version

**Transcrypt and serve:**
```bash
cd vue-ui
pnpm run build-python-game
pnpm install
pnpm run serve
```

---

### 7. HTMX Fully Front-End Single File Version

**Build:**
```bash
source venv/bin/activate
pip install transcrypt
cd htmx
sh build.sh
```
Or open the committed `game.html` directly in your browser.

---

### 8. Paneled Terminal Text UI Version with Animations for Events!!
**Run:**
```
python3 main_event_ui.py
```

---
## Game Instructions

### Start Menu

- **N**: New game (choose map size: 3x3, 5x5, or 7x7)
- **L**: Load game (reads `save.json`)

### Gameplay Commands

- `n`, `s`, `e`, `w`: Move north/south/east/west
- `look`: Describe your current location
- `stats`: Show your character sheet
- `rest`: Recover HP (safe in village; risky elsewhere)
- `inv`: Show inventory
- `save`: Save game to `save.json`
- `load`: Load game from `save.json`
- `help`: Show commands
- `quit`: Quit the game

### Tips

- Start at the central village (safe). Rest there to recover and sometimes find a potion.
- Venture outward for tougher enemies and better rewards.
- Leveling up restores HP and improves stats.

---

## Notes

- Code is modular for easy renderer swapping.
- Minimal WSGI web UI in `web.py` (zero external dependencies).