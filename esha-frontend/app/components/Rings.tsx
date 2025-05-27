"use client";
import styles from './Rings.module.css';

export default function Rings() {
  return (
    <div className={styles.ringsContainer}>
      <div className={`${styles.ring} ${styles.ring1}`}></div>
      <div className={`${styles.ring} ${styles.ring2}`}></div>
      <div className={`${styles.ring} ${styles.ring3}`}></div>
      <div className={`${styles.ring} ${styles.ring4}`}></div>

      <div className={styles.centerText}>E.S.H.A</div>
    </div>
  );
}
