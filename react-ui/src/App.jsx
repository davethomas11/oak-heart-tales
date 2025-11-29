import React, {useEffect, useState} from "react";
import styles from "./App.module.scss";

function App() {
    const [output, setOutput] = useState("");
    const [actions, setActions] = useState([]);
    const [player, setPlayer] = useState(null);
    const [enemy, setEnemy] = useState(null);
    const [tile, setTile] = useState(null);
    const [sid, setSid] = useState(localStorage.getItem("sid") || "");
    const [gameQuit, setGameQuit] = useState(false);
    // Fetch game state/output
    const fetchState = async () => {
        const res = await fetch(`/api/state?sid=${encodeURIComponent(sid)}`);
        const data = await res.json();
        setOutput(data.output);
        setActions(data.actions);
        setPlayer(data.player);
        setEnemy(data.enemy);
        setTile(data.tile);
        if (data.sid && !sid) {
            setSid(data.sid);
            localStorage.setItem("sid", data.sid);
        }
    };

    // Send action to backend
    const doAction = async (actionId) => {
        const res = await fetch(`/api/play?cmd=${encodeURIComponent(actionId)}&sid=${encodeURIComponent(sid)}`);
        const data = await res.json();
        setOutput(data.output);
        setActions(data.actions);
        setPlayer(data.player);
        setEnemy(data.enemy);
        setTile(data.tile);
        if (data.ended) {
            setGameQuit(true);
        }
    };

    const newGame = async () => {
        const res = await fetch("/api/new_game", { method: "POST" });
        const data = await res.json();
        setSid(data.sid);
        localStorage.setItem("sid", data.sid);
        setOutput(data.output);
        setActions(data.actions);
        setPlayer(data.player);
        setEnemy(data.enemy);
        setTile(data.tile);
        setGameQuit(false);
    }

    // Save to browser
    const saveGame = async () => {
        const res = await fetch(`/api/game_state?sid=${encodeURIComponent(sid)}`);
        const lastState = await res.json();
        if (lastState) {
            localStorage.setItem("savedGame", JSON.stringify(lastState));
            alert("Game saved!");
        }
    };

    // Load from browser
    const loadGame = async () => {
        const saved = localStorage.getItem("savedGame");
        if (saved) {
            const res = await fetch("/api/load", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: saved
            });
            const data = await res.json();
            setSid(data.sid);
            localStorage.setItem("sid", data.sid);
            setOutput(data.output);
            setActions(data.actions);
            setPlayer(data.player);
            setEnemy(data.enemy);
            setTile(data.tile);
            setGameQuit(false);
            alert("Game loaded!");
        } else {
            alert("No saved game found.");
        }
    };

    useEffect(() => {
        fetchState();
        // eslint-disable-next-line
    }, []);

    if (gameQuit) {
        return (
            <div className={styles.container}>
                <h1>Oakheart Tales</h1>
                <div>
                    <pre style={{background: "#222", color: "#eee", padding: "1rem", minHeight: "200px"}}>{output}</pre>
                </div>
                <div className={styles.actions}>
                    <button onClick={newGame}>New Game</button>
                    <button onClick={loadGame}>Load Game</button>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>

            <h1>Oakheart Tales</h1>
            <div style={{marginBottom: "1rem"}} className={styles.actions}>
                <button onClick={saveGame}>Save</button>
                <button onClick={loadGame}>Load</button>
            </div>
            <div style={{display: "flex", gap: "2rem", alignItems: "flex-start"}}>
                <div className={styles.gameOutput}>
                    {tile && (
                        <div>
                            <h3>Current Tile: {tile.name}</h3>
                            <img src={`/artwork/tiles/${tile.ascii.replace('.txt', '.jpg')}`} alt={tile.name}
                                 style={{maxWidth: 200}}/>
                            <p>{tile.description}</p>
                        </div>
                    )}
                    <pre style={{background: "#222", color: "#eee", padding: "1rem", minHeight: "200px"}}>{output}</pre>
                </div>
                <div>
                    {player && (
                        <div style={styles.statsSection}>
                            <h3>Player</h3>
                            <img src={`/artwork/player/player.jpg`} alt="Player" style={{maxWidth: 100}}/>
                            <ul>
                                <li>Name: {player.name}</li>
                                <li>Level: {player.level}</li>
                                <li className={styles.hp}>HP: {player.hp} / {player.max_hp}</li>
                                <li className={styles.mp}>MP: {player.mp} / {player.max_mp}</li>
                                <li>XP: {player.xp}</li>
                                <li className={styles.gold}>Gold: {player.gold}</li>
                                <li>Weapon: {player.weapon}</li>
                                <li>Armor: {player.armor}</li>
                                <li>Potions: {player.potions}</li>
                                <li>Attack: {player.attack}</li>
                                <li>Defense: {player.defense}</li>
                            </ul>
                        </div>
                    )}
                    {enemy && (
                        <div style={styles.statsSection}>
                            <h3>Enemy</h3>
                            <img src={`/artwork/enemies/${enemy.name
                                .toLowerCase()
                                .replace(/ \(lv [\d]+\)/g, "")
                                .replace(/ /g, "_")}.jpg`
                            }
                                 alt={enemy.name}
                                 style={{maxWidth: 100}}
                            />
                            <ul>
                                <li>Name: {enemy.name}</li>
                                <li>HP: {enemy.hp}</li>
                                <li>Attack: {enemy.attack}</li>
                                <li>Defense: {enemy.defense}</li>
                            </ul>
                        </div>
                    )}
                </div>
            </div>
            <div className={styles.actions}>
                {actions
                    .filter(a => a.id !== "save" && a.id !== "load")
                    .map(a => (
                        <button
                            key={a.id}
                            disabled={!a.enabled}
                            title={a.reason || ""}
                            style={{margin: "0.25rem"}}
                            onClick={() => {
                                if (a.label === "Save Game") {
                                    saveGame();
                                } else if (a.label === "Load Game") {
                                    loadGame();
                                } else {
                                    doAction(a.id)
                                }
                            }}
                        >
                            {a.label}
                        </button>
                    ))}
            </div>
            <audio src="/music/background.mp3" autoPlay loop controls style={{marginBottom: "1rem"}} />
        </div>
    );
}

export default App;
