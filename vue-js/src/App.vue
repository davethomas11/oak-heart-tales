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
      <input v-model="userInput" @keyup.enter="handleInput" placeholder="Type command..."/>
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

import ActionButtons from "./ActionButtons.vue";
import { newGame, initializeGameModule, loadFromData } from "./gameUtil";

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
  components: {ActionButtons},
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
    async initGame() {
      this.game = await newGame(this.mapSize);
      this.game.save_fn = this.saveGame;
      this.game.load_fn = this.loadGame;
      this.screen = "game";
      this.renderGame();
    },
    saveGame() {
      if (this.game) {
        localStorage.setItem("savegame", JSON.stringify(this.game.to_dict()));
        alert("Game saved!");
      }
    },
    loadGame() {
      // Implement browser-based load logic
      const saved = localStorage.getItem("savegame");
      if (saved) {
        const gameData = JSON.parse(saved);
        this.game = loadFromData(gameData);
        initializeGameModule(this.game);
        this.game.save_fn = this.saveGame;
        this.game.load_fn = this.loadGame;
        this.screen = "game";
        this.renderGame();
      } else {
        alert("No saved game found.");
      }
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
      if (action.label === "Restart Game") {
        this.restartGame();
      } else if (action.label === "Save Game") {
        this.saveGame();
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
