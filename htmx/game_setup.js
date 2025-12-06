var playerModule = require("player");
var worldModule = require("world");
var gameModule = require("game");

window.mapSize = 20;

function restartGame() {
    window.game = newGame();
    const gameText = document.getElementById("game-text");
    gameText.innerHTML = game.look();
}

function newGame() {
    const tileset = JSON.parse(window.game_data_files["../data/tileset.json"]);
    const player = new playerModule.Player("Hero", 1, 25, 25, 5, 5, 2, 1, 3, [], 0, null, null);
    const grid = generateRandomTilesetGrid(mapSize, tileset);
    const world = new worldModule.World(mapSize, mapSize, grid, getSeedFromGeneratedGrid(grid));
    const game = new gameModule.Game(world, player, Math.floor(mapSize / 2), Math.floor(mapSize / 2));
    initializeGameModule(game);
    return game
}

function getSeedFromGeneratedGrid(grid) {
    const str = grid.flat().map(tile => tile.name || tile.py_name).join("-");
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0;
    }
    return Math.abs(hash);
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
    const center = Math.floor(size / 2);
    grid[center][center] = new worldModule.Tile(
        village.name, village.description, village.danger,
        village.safe, village.ascii, village.shop
    );
    return grid;
}

function initializeGameModule(game) {
    game.data_loader = {
        load: (loadJsonFile) => {
            return JSON.parse(window.game_data_files[loadJsonFile]);
        }
    }
    game.ascii_loader = {
        load: (loadTextFile) => {
            return window.game_data_files["../data/rooms/" + loadTextFile];
        }
    }
    game.load_configurations("../data/enemies.json");
}