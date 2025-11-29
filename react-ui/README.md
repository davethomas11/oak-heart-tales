# Oakheart Tales: React UI

This is the browser-based interface for **Oakheart Tales**, a Python-powered text adventure game.  
The React UI provides a modern, interactive way to play the game in your browser, with enhanced visuals and usability.

## Features

- **Web-based gameplay:** Play Oakheart Tales directly in your browser.
- **Rich artwork:** Enemy, player, and tile images for immersive experience.
- **Music:** Background soundtrack for atmosphere.
- **Save/Load:** Save your progress in the browser and reload it later.
- **Responsive UI:** Fast, interactive controls for game actions.

## Getting Started

1. **Install dependencies and build the React UI:**
    ```bash
    cd react-ui
    npm install
    npm run build
    ```

2. **Start the Python backend:**
    ```bash
    cd ..
    python3 react.py
    ```

3. **Open your browser:**
    ```
    http://127.0.0.1:3000/
    ```

## Save and Load

- Use the **Save** button to store your game progress in your browser.
- Use the **Load** button to restore your saved game.

## Project Structure

- `src/` — React source code and styles
- `public/artwork/` — Game images
- `public/music/` — Background music
- `build/` — Production build output

## Scripts

- `npm start` — Run in development mode
- `npm run build` — Build for production
- `npm test` — Run tests

## About Oakheart Tales

Oakheart Tales is a fantasy adventure game written in Python, featuring exploration, combat, and story-driven gameplay.  
This React UI adds a modern web interface, artwork, and browser-based save/load to the classic text adventure.

For backend details, see the main project README in the parent directory.
