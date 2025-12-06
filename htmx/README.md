# Installation steps for htmx

To install htmx in your project, follow these steps:

- Make sure venv is turned on in your project. 
- Make sure transcrypt is installed in your virtual environment. 
- transcrypt.sh runs the transcrypt compiler in a virtual environment.
- Make sure terser is installed globally. You can install it using npm.
- run transcrypt.sh to compile the htmx source code.
- run npm install to install the necessary dependencies.
- run npm run build to bundle and minify the compiled code.

The build creates a single HTML file called `game.html` 
that contains everything needed to run the game. 

You can open this file in a web browser to play the game.

`game.html` is also committed to the repository, 
so you can also just open that file directly.

It is the final compiled output of the build process.

# About the `htmx` Folder

This folder contains all the source code, build scripts, and resources needed to run the browser-based htmx version of the game.

## Structure

- `game.html`: The main compiled HTML file for the game. This is the entry point for playing the game in a browser.
- `game.js`, `game_server.js`, `game_setup.js`: JavaScript source files for game logic, server emulation, and setup.
- `inline-resources.js`: Script to inline static resources (like JSON or CSS) into the final HTML.
- `game.css`: Styles for the game UI.
- `index.htmx.html`: The main HTML template used during development.
- `build.sh`, `transcrypt.sh`: Shell scripts to automate building and compiling the project.
- `package.json`: NPM configuration for managing dependencies and build scripts.
- `browser/`, `js/`: Additional JavaScript modules and build outputs.

## Purpose

The `htmx` folder is designed to support a fully client-side, single-file version of the game. 
All necessary assets and logic are bundled into `game.html` for easy distribution and offline play.

## Development Workflow

1. Edit source files in this folder as needed.
2. Use `transcrypt.sh` to compile Python code (if any) to JavaScript.
3. Run `npm install` to install dependencies.
4. Run `npm run build` to bundle everything into `game.html`.
5. Open `game.html` in your browser to play or test.

## Notes

- The build process inlines resources (such as JSON data) so that no external files are needed at runtime.
- You can use the included scripts to automate the build and packaging process.
- For development, you may use `index.htmx.html` and the unbundled JS files for easier debugging.

See the rest of this README for installation and build instructions.
