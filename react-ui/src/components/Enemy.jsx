import styles from "./Enemy.module.scss";
import React from "react";

function Enemy({enemy}) {
    if (!enemy) return null;
    return (<div style={styles.statsSection}>
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
    </div>)
}

export default Enemy;