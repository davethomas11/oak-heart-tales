import React from "react";
import styles from "./GameOverAnimation.module.scss";

function GameOverAnimation({ onRestart, onLoad }) {
    return (
        <div className={styles.overlay}>
            <div className={styles.text}>
                <span className={styles.glow}>Game Over</span>
                <div className={styles.buttonRow}>
                    <button className={styles.button} onClick={onRestart}>Restart</button>
                    <button className={styles.button} onClick={onLoad}>Load</button>
                </div>
            </div>
        </div>
    );
}

export default GameOverAnimation;
