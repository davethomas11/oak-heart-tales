import React, { useEffect, useState } from "react";
import styles from "./CombatStartAnimation.module.scss";

function CombatStartAnimation({ enemy, onDone }) {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => setVisible(false), 1200);
        const doneTimer = setTimeout(() => onDone && onDone(), 1800);
        return () => {
            clearTimeout(timer);
            clearTimeout(doneTimer);
        };
    }, [onDone]);

    if (!visible) return null;

    return (
        <div className={styles.overlay}>
            <div className={styles.box}>
                <div className={styles.title}>Battle Start!</div>
                <div className={styles.enemySection}>
                    <img
                        src={`/artwork/enemies/${enemy.name
                            .toLowerCase()
                            .replace(/ \(lv [\d]+\)/g, "")
                            .replace(/ /g, "_")}.jpg`}
                        alt={enemy.name}
                        className={styles.enemyImg}
                    />
                    <ul>
                        <li>Name: {enemy.name}</li>
                        <li>HP: {enemy.hp}</li>
                        <li>Attack: {enemy.attack}</li>
                        <li>Defense: {enemy.defense}</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default CombatStartAnimation;
