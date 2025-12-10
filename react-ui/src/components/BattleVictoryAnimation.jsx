import React, { useEffect, useState } from "react";
import styles from "./BattleVictoryAnimation.module.scss";

function BattleVictoryAnimation({ gold = 0, xp = 0, leveledUp = false, onDone }) {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => setVisible(false), leveledUp ? 1800 : 1200);
        const doneTimer = setTimeout(() => onDone && onDone(), leveledUp ? 2200 : 1600);
        return () => {
            clearTimeout(timer);
            clearTimeout(doneTimer);
        };
    }, [leveledUp, onDone]);

    if (!visible) return null;

    return (
        <div className={styles.overlay}>
            <div className={styles.box}>
                <div className={styles.title}>Victory!</div>
                <div className={styles.loot}>
                    <span>+{gold} Gold</span>
                    <span>+{xp} XP</span>
                </div>
                {leveledUp && (
                    <div className={styles.levelUp}>Level Up!</div>
                )}
            </div>
        </div>
    );
}

export default BattleVictoryAnimation;
