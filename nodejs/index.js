// Import the transpiled game module
import * as gameModule from "../engine/game/__target__/game.js";
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

function startUp() {
    const choice = promptStartMenu();
    if (choice === 'new') {
        const size = promptMapSize();
        const tileset = loadJsonFile("../data/tileset.json")
        game = gameModule.Game.new_random(size, tileset, Math.floor(Math.random() * 10000) + 1);
        console.log(game);
        runGame();
    } else if (choice === 'load') {
        const data = loadGame("nodejs_savegame.json");
        game.copy_from(data);
        runGame();
    } else if (choice === 'quit') {
        console.log("Goodbye!");
        process.exit(0);
    }
}

function runGame() {
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
    gameLoop();
}

function gameLoop() {
    while (!game.ended) {
        uiRender(game.look())
        while(game.player.is_alive()) {
            const input = prompt('> ').trim();
            const acted = game.execute_action(input);
            if (game.ended) {
                break;
            }
            if (acted) {
                ui_render(acted);
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
            const input = require('prompt-sync')()('> ').trim().toLowerCase();
            if (input[0] === 'l') {
                const data = loadGame("nodejs_savegame.json");
                game.copy_from(data);
                break;
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