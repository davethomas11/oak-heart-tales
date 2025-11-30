// Import the transpiled game module
import * as gameModule from "../engine/game/__target__/game.js";
import * as playerModule from "../engine/game/__target__/player.js";
import * as worldModule from "../engine/game/__target__/world.js";

import create from 'prompt-sync';
import fs from 'fs';

const prompt = create();

// Initialize the game (assuming Game class exists)
let game;
console.log("Game engine started.");


function clearConsole() {
    process.stdout.write('\x1Bc');
}

function uiRender(text) {
    clearConsole();
    console.log(text);
}

function banner() {
    return (
        "=".repeat(50) +
        "\n" +
        "Oakheart Tales: A Tiny Text Adventure\n" +
        "Explore, fight, and grow stronger. Type 'help' to begin.\n" +
        "=".repeat(50)
    );
}

function promptStartMenu() {
    clearConsole();
    console.log(banner());
    console.log("[N]ew Game  |  [L]oad Game  |  [Q]uit");
    while (true) {
        const input = prompt('> ').trim().toLowerCase();
        if (input[0] === 'n') {
            return 'new';
        } else if (input[0] === 'l') {
            return 'load';
        } else if (input[0] === 'q') {
            return 'quit';
        } else {
            console.log("Invalid option. Please enter N, L, or Q.");
        }
    }
}

function promptMapSize() {
    clearConsole();
    console.log("Select Map Size:");
    console.log("[S]mall  |  [M]edium  |  [L]arge");
    while (true) {
        const input = prompt('> ').trim().toLowerCase();
        if (input === 's') {
            return 5;
        } else if (input === 'm') {
            return 7;
        } else if (input === 'l') {
            return 9;
        } else {
            console.log("Invalid option. Please enter S, M, or L.");
        }
    }
}

function loadJsonFile(filePath) {
    if (fs.existsSync(filePath)) {
        const data = fs.readFileSync(filePath, 'utf8');
        return JSON.parse(data);
    } else {
        return null;
    }
}

function loadTextFile(filePath) {
    filePath = "../data/rooms/" + filePath;
    if (fs.existsSync(filePath)) {
        return fs.readFileSync(filePath, 'utf8');
    } else {
        return null;
    }
}

const saveGame = (data, filename) => {
    fs.writeFileSync(filename, JSON.stringify(data), 'utf8');
}

const loadGame = (filename) => {
    if (fs.existsSync(filename)) {
        const fileData = fs.readFileSync(filename, 'utf8');
        return JSON.parse(fileData);
    }
}

function generateRandomTilesetGrid(size, tilesetData) {
    const village = tilesetData["village"];
    const tileset = tilesetData["tiles"];
    const grid = [];
    for (let y = 0; y < size; y++) {
        const row = [];
        for (let x = 0; x < size; x++) {
            const tileKeys = Object.keys(tileset);
            const randomKey = tileKeys[Math.floor(Math.random() * tileKeys.length)];
            const tileData = tileset[randomKey];
            const tile = new worldModule.Tile(tileData.name, tileData.description, tileData.danger, tileData.safe, tileData.ascii);
            row.push(tile);
        }
        grid.push(row);
    }
    // Place village in the center
    const center = Math.floor(size / 2);
    const villageTile = new worldModule.Tile(village.name, village.description, village.danger, village.safe, village.ascii, village.shop);
    grid[center][center] = villageTile;
    return grid;
}

function getSeedFromGeneratedGrid(grid) {
    // Generate a numeric seed by hashing tile names
    const str = grid.flat().map(tile => tile.name || tile.py_name).join("-");
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0; // Convert to 32bit integer
    }
    return Math.abs(hash);
}

function startUp() {
    const choice = promptStartMenu();
    if (choice === 'new') {
        const size = promptMapSize();
        const tileset = loadJsonFile("../data/tileset.json");
        const player = new playerModule.Player("Hero", 1, 25, 25, 5, 5, 2, 1, 3, [], 0, null, null);
        const grid = generateRandomTilesetGrid(size, tileset);
        const world = new worldModule.World(size, size, grid, getSeedFromGeneratedGrid(grid));
        const game = new gameModule.Game(world, player, Math.floor(size / 2), Math.floor(size / 2));
        runGame(game);
    } else if (choice === 'load') {
        const data = loadGame("nodejs_savegame.json");
        if (data !== null) {
            console.log("Loaded saved game.");
        } else {
            console.log("No saved game found.");
            prompt("Press Enter to return to main menu...");
            startUp();
            return;
        }
        runGame(loadFromData(data));
    } else if (choice === 'quit') {
        console.log("Goodbye!");
        process.exit(0);
    }
}

function loadFromData(data) {
    const loadedPlayer = data.player;
    const player = new playerModule.Player(loadedPlayer.name, loadedPlayer.level,
        loadedPlayer.max_hp, loadedPlayer.hp, loadedPlayer.max_mp,
        loadedPlayer.mp, loadedPlayer.attack, loadedPlayer.defence, loadedPlayer.potions,
        loadedPlayer.known_spells || [], loadedPlayer.xp, loadedPlayer.weapon, loadedPlayer.armor);
    const loadedWorld = data.world;
    const grid = [];
    for (let y = 0; y < loadedWorld.height; y++) {
        const row = [];
        for (let x = 0; x < loadedWorld.width; x++) {
            const tileData = loadedWorld.grid[y][x];
            const tile = new worldModule.Tile(
                tileData.name, tileData.description, tileData.danger,
                tileData.safe, tileData.ascii, tileData.shop);
            row.push(tile);
        }
        grid.push(row);
    }
    const world = new worldModule.World(loadedWorld.width, loadedWorld.height, grid, loadedWorld.seed);
    const game = new gameModule.Game(world, player, data.pos.x, data.pos.y);
    game.ended = false;
    game.state = data.state;
    for (const coords of data.explored) {
        game._mark_explored(coords.x, coords.y);
    }
    return game;
}

function runGame(game) {
    game.data_loader = {
        load: loadJsonFile
    }
    game.ascii_loader = {
        load: loadTextFile
    }
    game.load_configurations("../data/enemies.json");
    game.save_file = "nodejs_savegame.json";
    game.save_fn = saveGame;
    game.load_fn = loadGame;
    gameLoop(game);
}

function gameLoop(game) {
    while (!game.ended) {
        game.actions.available();
        uiRender(game.look())
        while (game.player.is_alive()) {
            const input = prompt('> ').trim();
            const acted = game.execute_action(input);
            if (game.ended) {
                break;
            }
            if (acted) {
                uiRender(acted);
            } else if (input == "debug") {
                uiRender(game.debug_pos());
            } else {
                uiRender(game.look() + "\n\nUnknown command: " + input);
            }
        }

        if (!game.ended) {
            uiRender("Game Over.\n[L]oad  |  [R]estart  |  [Q]uit")
        }
        while (!game.ended) {
            const input = prompt('> ').trim().toLowerCase();
            if (input[0] === 'l') {
                const data = loadGame("nodejs_savegame.json");
                if (!data) {
                    console.log("No saved game found.");
                    continue;
                } else {
                    game = loadFromData(data);
                    break;
                }
            } else if (input[0] === 'r') {
                startUp();
                return;
            } else if (input[0] === 'q') {
                console.log("Goodbye!");
                process.exit(0);
            } else {
                console.log("Invalid option. Please enter L, R, or Q.");
            }
        }
    }
}

startUp();