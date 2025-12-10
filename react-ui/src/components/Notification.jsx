import styles from './Notification.module.scss';
import React, { useEffect, useState, useRef } from 'react';

function Notification({ message, onDone, startDelay = 0 }) {
    const [visible, setVisible] = useState(false);
    const hasBeenShown = useRef(false);

    useEffect(() => {
        if (hasBeenShown.current) {
            return;
        }
        const showTimer = setTimeout(() => {
            hasBeenShown.current = true;
            setVisible(true)
        }, startDelay);
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
        if (visible === false) {
            const removeTimer = setTimeout(onDone, 500); // Wait for fade-out
            return () => clearTimeout(removeTimer);
        }
    }, [visible, onDone]);

    return (
        <div className={`${styles.notification} ${visible ? styles.show : styles.hide}`}>
            {message}
        </div>
    );
}

export default Notification;
