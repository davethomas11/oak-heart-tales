import styles from './Notification.module.scss';
import React, { useEffect, useState } from 'react';

function Notification({ message, onDone, startDelay = 0 }) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        const showTimer = setTimeout(() => setVisible(true), startDelay);
        let fadeTimer;
        if (startDelay >= 0) {
            fadeTimer = setTimeout(() => setVisible(false), startDelay + 2500);
        }
        return () => {
            clearTimeout(showTimer);
            clearTimeout(fadeTimer);
        };
    }, [startDelay]);

    useEffect(() => {
        if (visible === false && startDelay >= 0) {
            const removeTimer = setTimeout(onDone, 500); // Wait for fade-out
            return () => clearTimeout(removeTimer);
        }
    }, [visible, onDone, startDelay]);

    return (
        <div className={`${styles.notification} ${visible ? styles.show : styles.hide}`}>
            {message}
        </div>
    );
}

export default Notification;
