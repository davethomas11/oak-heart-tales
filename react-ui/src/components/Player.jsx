import React from "react";
import styles from "./Player.module.scss";

function Player({ player }) {
    if (!player) return null;
    return (
        <div className={styles.statsSection}>
            <h3>Player</h3>
            <img
                src={`/artwork/player/player.jpg`}
                alt="Player"
                style={{ maxWidth: 100 }}
            />
            <ul>
                <li>Name: {player.name}</li>
                <li>Level: {player.level}</li>
                <li className={styles.hp}>
                    HP: {player.hp} / {player.max_hp}
                    <div className={styles.barContainer}>
                        <div
                            className={styles.hpBar}
                            style={{
                                width: `${(player.hp / player.max_hp) * 100}%`
                            }}
                        />
                    </div>
                </li>
                <li className={styles.mp}>
                    MP: {player.mp} / {player.max_mp}
                    <div className={styles.barContainer}>
                        <div
                            className={styles.mpBar}
                            style={{
                                width: `${(player.mp / player.max_mp) * 100}%`
                            }}
                        />
                    </div>
                </li>
                <li>XP: {player.xp}</li>
                <li className={styles.gold}>Gold: {player.gold}</li>
                <li>Weapon: {player.weapon ? player.weapon.name : "None"}</li>
                <li>Armor: {player.armor ? player.armor.name : "None"}</li>
                <li>Potions: {player.potions}</li>
                <li>Attack: {player.attack}</li>
                <li>Defense: {player.defense}</li>
            </ul>
        </div>
    );
}

export default Player;
