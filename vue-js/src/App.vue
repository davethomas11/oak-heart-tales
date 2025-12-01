<template>
  <div id="app">
    <div v-if="screen === 'menu'">
      <pre>{{ banner }}</pre>
      <button @click="startNewGame">New Game</button>
      <button @click="loadGame">Load Game</button>
      <button @click="quitGame">Quit</button>
    </div>
    <div v-else-if="screen === 'mapSize'">
      <h2>Select Map Size:</h2>
      <button @click="selectMapSize(5)">Small</button>
      <button @click="selectMapSize(7)">Medium</button>
      <button @click="selectMapSize(9)">Large</button>
    </div>
    <div v-else-if="screen === 'game'">
      <pre>{{ gameText }}</pre>
      <input v-model="userInput" @keyup.enter="handleInput" placeholder="Type command..." />
      <button @click="handleInput">Send</button>
      <ActionButtons
          v-if="actions.length"
          :actions="actions"
          @action="handleAction"
      />
    </div>
    <div v-else-if="screen === 'gameOver'">
      <pre>Game Over.</pre>
      <button @click="loadGame">Load</button>
      <button @click="restartGame">Restart</button>
      <button @click="quitGame">Quit</button>
    </div>
  </div>
</template>

<script>
import * as gameModule from "./game/game.js";
import * as playerModule from "./game/player.js";
import * as worldModule from "./game/world.js";

import ActionButtons from "./ActionButtons.vue";

export default {
  name: "App",
  data() {
    return {
      screen: "menu",
      banner: "=".repeat(50) + "\nOakheart Tales: A Tiny Text Adventure\nExplore, fight, and grow stronger. Type 'help' to begin.\n" + "=".repeat(50),
      game: null,
      gameText: "",
      userInput: "",
      mapSize: null,
    };
  },
  components: { ActionButtons },
  computed: {
    actions() {
      if (this.game && this.game.actions && typeof this.game.actions.available === "function") {
        return this.game.actions.available();
      }
      return [];
    }
  },
  methods: {
    startNewGame() {
      this.screen = "mapSize";
    },
    selectMapSize(size) {
      this.mapSize = size;
      this.initGame();
    },
    initializeGameModule(game){
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
      game.save_file = "nodejs_savegame.json";
      game.save_fn = undefined;
      game.load_fn = undefined;
    },
    async initGame() {
      // Replace with AJAX/fetch for browser
      const tileset = await fetch("/data/tileset.json").then(r => r.json());
      const player = new playerModule.Player("Hero", 1, 25, 25, 5, 5, 2, 1, 3, [], 0, null, null);
      const grid = this.generateRandomTilesetGrid(this.mapSize, tileset);
      const world = new worldModule.World(this.mapSize, this.mapSize, grid, this.getSeedFromGeneratedGrid(grid));
      this.game = new gameModule.Game(world, player, Math.floor(this.mapSize / 2), Math.floor(this.mapSize / 2));
      this.initializeGameModule(this.game);
      this.screen = "game";
      this.renderGame();
    },
    loadGame() {
      // Implement browser-based load logic
      alert("Load game not implemented in browser yet.");
    },
    quitGame() {
      this.screen = "menu";
      this.game = null;
      this.gameText = "";
      this.userInput = "";
    },
    restartGame() {
      this.screen = "menu";
      this.game = null;
      this.gameText = "";
      this.userInput = "";
    },
    renderGame() {
      if (this.game) {
        this.gameText = this.game.look();
      }
    },
    handleAction(action) {
      if (action.label === "Save Game") {
        alert("Save Game not implemented.");
      } else if (action.label === "Load Game") {
        this.loadGame();
      } else {
        const acted = this.game.execute_action(action.id);
        this.actions = this.game.actions.available();
        if (this.game.ended) {
          this.screen = "gameOver";
        } else if (acted) {
          this.gameText = acted;
        } else {
          this.gameText = this.game.look() + "\n\nUnknown command: " + action.label;
        }
      }
    },
    handleInput() {
      if (!this.game || !this.userInput) return;
      this.actions = this.game.actions.available();
      const input = this.userInput.trim();
      const acted = this.game.execute_action(input);
      this.actions = this.game.actions.available();
      if (this.game.ended) {
        this.screen = "gameOver";
      } else if (acted) {
        this.gameText = acted;
      } else {
        this.gameText = this.game.look() + "\n\nUnknown command: " + input;
      }
      this.userInput = "";
    },
    generateRandomTilesetGrid(size, tilesetData) {
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
      const villageTile = new worldModule.Tile(village.name, village.description, village.danger, village.safe, village.ascii, village.shop);
      grid[center][center] = villageTile;
      return grid;
    },
    getSeedFromGeneratedGrid(grid) {
      const str = grid.flat().map(tile => tile.name || tile.py_name).join("-");
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0;
      }
      return Math.abs(hash);
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
input {
  margin-top: 10px;
  padding: 5px;
  width: 300px;
}
button {
  margin: 5px;
  padding: 10px 20px;
}
</style>
