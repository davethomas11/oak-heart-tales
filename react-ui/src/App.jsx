import React, {useEffect, useState, useRef} from "react";
import styles from "./App.module.scss";
import Notification from "./components/Notification";
import GameOverAnimation from "./components/GameOverAnimation";
import CombatStartAnimation from "./components/CombatStartAnimation";
import BattleVictoryAnimation from "./components/BattleVictoryAnimation";
import Player from "./components/Player";
import Enemy from "./components/Enemy";

function App() {
    const [output, setOutput] = useState("");
    const [actions, setActions] = useState([]);
    const [player, setPlayer] = useState(null);
    const [enemy, setEnemy] = useState(null);
    const [tile, setTile] = useState(null);
    const [sid, setSid] = useState(localStorage.getItem("sid") || "");
    const [gameQuit, setGameQuit] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const sseRef = useRef(null);
    const [showCombatStart, setShowCombatStart] = useState(false);
    const [showCombatVictory, setShowCombatVictory] = useState(false);
    const prevEnemyRef = useRef(null);
    const combatVictoryDataRef = useRef({gold: 0, xp: 0, leveledUp: false});

    useEffect(() => {
        if (enemy && (!prevEnemyRef.current || prevEnemyRef.current.name !== enemy.name)) {
            setShowCombatStart(true);
        }
        prevEnemyRef.current = enemy;
    }, [enemy]);

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
        const res = await fetch("/api/new_game", {method: "POST"});
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

    const [sseConnected, setSseConnected] = useState(false);
    const [ssePulse, setSsePulse] = useState(false);
    const ssePulseTimeout = useRef(null);

    const disconnectSSE = () => {
        if (sseRef.current) {
            sseRef.current.close();
            sseRef.current = null;
            setSsePulse(false);
            setSseConnected(false);
            if (ssePulseTimeout.current) {
                clearInterval(ssePulseTimeout.current);
                ssePulseTimeout.current = null;
            }

        }
    };

    const reconnectSSE = () => {
        disconnectSSE();
        connectSSE();
    };

    const connectSSE = () => {
        if (sseRef.current) {
            sseRef.current.close();
            sseRef.current = null;
        }
        const sse = new EventSource(`/api/events?sid=${encodeURIComponent(sid)}`);
        setSseConnected(true);
        setSsePulse(true);
        // Start pulse interval
        ssePulseTimeout.current = setInterval(() => {
            setSsePulse(pulse => !pulse);
        }, 600);
        sse.onerror = () => {
            setSseConnected(false);
            if (ssePulseTimeout.current) {
                clearInterval(ssePulseTimeout.current);
                setSsePulse(false);
            }
            sse.close();
        };
        sse.onmessage = (e) => {
            console.log("SSE Event", e.data);
            try {
                const data = JSON.parse(e.data);

                if (data && data.payload.message) {
                    const id = Date.now() + Math.random();
                    setNotifications((current) => [
                        ...current,
                        {id, message: data.payload.message}
                    ]);

                    if (data.type === "exited_combat" && data.payload.victory) {
                        combatVictoryDataRef.current.gold = data.payload.gold_looted || 0;
                        combatVictoryDataRef.current.xp = data.payload.xp_gained || 0;
                        combatVictoryDataRef.current.leveledUp = data.payload.leveled_up || false;
                        setShowCombatVictory(true);
                    }
                }
            } catch (error) {
                console.error("Error parsing SSE message:", error);
            }
        };
        sseRef.current = sse;
    };

    useEffect(() => {
        connectSSE();

        const handleVisibility = () => {
            if (document.visibilityState === "visible" && !sseRef.current) {
                connectSSE();
            } else {
                disconnectSSE();
            }
        };
        document.addEventListener("visibilitychange", handleVisibility);

        return () => {
            if (sseRef.current) {
                sseRef.current.close();
            }
            if (ssePulseTimeout.current) {
                clearInterval(ssePulseTimeout.current);
                setSsePulse(false);
            }
        };
        // eslint-disable-next-line
    }, [sid]);

    if (gameQuit) {
        return (
            <div className={styles.container}>
                <h1>Oak-heart Tales</h1>
                <div>
                    <pre className={styles.gameOutput}>{output}</pre>
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
            {player && player.hp <= 0 ? <GameOverAnimation onLoad={loadGame} onRestart={newGame}/> : null}
            <div style={{display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1rem"}}>
                <div
                    style={{
                        width: 16,
                        height: 16,
                        borderRadius: "50%",
                        background: sseConnected ? (ssePulse ? "#4caf50" : "#81c784") : "#f44336",
                        boxShadow: ssePulse && sseConnected ? "0 0 8px 2px #4caf50" : "none",
                        transition: "background 0.2s, box-shadow 0.2s"
                    }}
                    title={sseConnected ? "SSE Connected" : "SSE Disconnected"}
                />
                <button onClick={sseConnected ? disconnectSSE : reconnectSSE}>
                    {sseConnected ? "Disconnect SSE" : "Reconnect SSE"}
                </button>
                <small><i>This controls server sent notifications</i></small>
            </div>
            <div style={{marginBottom: "1rem"}} className={styles.actions}>
                <button onClick={saveGame}>Save</button>
                <button onClick={loadGame}>Load</button>
            </div>
            <div className={styles.notificationsContainer}>
                {notifications.map((notification, index) => (
                    <Notification
                        key={notification.id}
                        message={notification.message}
                        startDelay={index * 400}
                        onDone={() => {
                            setNotifications((prev) => prev.filter((x) => x.id !== notification.id));
                        }}
                    />
                ))}
            </div>
            <div style={{display: "flex", gap: "2rem", alignItems: "flex-start"}}>
                <div className={styles.gameOutput}>
                    {tile && (
                        <div>
                            <h3>Current Tile: {tile.name}</h3>
                            {!enemy && (<div>
                                <img src={`/artwork/tiles/${tile.ascii.replace('.txt', '.jpg')}`} alt={tile.name}
                                     style={{maxWidth: 200}}/>
                                <p>{tile.description}</p>
                            </div>)}
                        </div>
                    )}
                    {enemy && <Enemy enemy={enemy}/>}
                    <pre className={styles.consoleOutput}>{output}</pre>
                </div>
                <div>
                    {player && (
                        <Player player={player} key={player.name}/>
                    )}
                    {showCombatVictory && (
                        <BattleVictoryAnimation
                            gold={combatVictoryDataRef.current.gold}
                            xp={combatVictoryDataRef.current.xp}
                            leveledUp={combatVictoryDataRef.current.leveledUp}
                            onDone={() => setShowCombatVictory(false)}
                        />
                    )}Z
                    {showCombatStart && enemy && (
                        <CombatStartAnimation
                            enemy={enemy}
                            onDone={() => setShowCombatStart(false)}
                        />
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
            <audio src="/music/background.mp3" loop controls style={{marginBottom: "1rem"}}/>
        </div>
    );
}

export default App;
