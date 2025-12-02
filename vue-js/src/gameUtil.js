import * as worldModule from "@/game/world";
import * as playerModule from "@/game/player";
import * as gameModule from "@/game/game";

/**
 * Generates a random tileset grid of given size using the provided tileset data.
 *
 * @param size
 * @param tilesetData
 * @returns {*[]}
 */
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

/**
 * Generates a seed number from the provided grid of tiles.
 *
 * @param grid
 * @returns {number}
 */
function getSeedFromGeneratedGrid(grid) {
    const str = grid.flat().map(tile => tile.name || tile.py_name).join("-");
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0;
    }
    return Math.abs(hash);
}

/**
 * Loads a game from the provided data object.
 *
 * @param data
 * @returns {*}
 */
export function loadFromData(data) {
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

export function initializeGameModule(game) {
    game.data_loader = {
        load: (loadJsonFile) => {
            const xhr = new XMLHttpRequest();
            xhr.open("GET", loadJsonFile, false); // false for synchronous/blocking
            xhr.send(null);
            if (xhr.status === 200) {
                return JSON.parse(xhr.responseText);
            } else {
                throw new Error("Failed to load JSON file: " + loadJsonFile);
            }
        }
    }
    game.ascii_loader = {
        load: (loadTextFile) => {
            const xhr = new XMLHttpRequest();
            xhr.open("GET", "/data/rooms/" + loadTextFile, false); // false for synchronous/blocking
            xhr.send(null);
            if (xhr.status === 200) {
                return xhr.responseText;
            } else {
                throw new Error("Failed to load Text file: " + loadTextFile);
            }
        }
    }
    game.load_configurations("/data/enemies.json");
}

export async function newGame(mapSize) {
    // Replace with AJAX/fetch for browser
    const tileset = await fetch("/data/tileset.json").then(r => r.json());
    const player = new playerModule.Player("Hero", 1, 25, 25, 5, 5, 2, 1, 3, [], 0, null, null);
    const grid = generateRandomTilesetGrid(mapSize, tileset);
    const world = new worldModule.World(mapSize, mapSize, grid, getSeedFromGeneratedGrid(grid));
    const game = new gameModule.Game(world, player, Math.floor(mapSize / 2), Math.floor(mapSize / 2));
    initializeGameModule(game);
    return game
}