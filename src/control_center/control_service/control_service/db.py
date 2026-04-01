"""Central control_service SQLite DB — schema init and CRUD stubs."""

import sqlite3
import os
import threading

_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'control.db')
_lock = threading.Lock()


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(_DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create all tables if they do not exist."""
    with _lock:
        conn = _get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS USER (
                user_id       TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS CARD (
                card_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  TEXT NOT NULL REFERENCES USER(user_id),
                card_num TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ZONE (
                zone_id        INTEGER PRIMARY KEY,
                zone_name      TEXT NOT NULL,
                zone_type      TEXT NOT NULL DEFAULT 'product',
                waypoint_x     REAL,
                waypoint_y     REAL,
                waypoint_theta REAL
            );

            CREATE TABLE IF NOT EXISTS PRODUCT (
                product_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price        INTEGER NOT NULL DEFAULT 0,
                zone_id      INTEGER REFERENCES ZONE(zone_id)
            );

            CREATE TABLE IF NOT EXISTS BOUNDARY_CONFIG (
                config_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                x_min       REAL NOT NULL,
                x_max       REAL NOT NULL,
                y_min       REAL NOT NULL,
                y_max       REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ROBOT (
                robot_id       TEXT PRIMARY KEY,
                ip_address     TEXT,
                current_mode   TEXT NOT NULL DEFAULT 'OFFLINE',
                pos_x          REAL DEFAULT 0.0,
                pos_y          REAL DEFAULT 0.0,
                battery_level  INTEGER DEFAULT 100,
                last_seen      TEXT,
                active_user_id TEXT
            );

            CREATE TABLE IF NOT EXISTS ALARM_LOG (
                log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                robot_id    TEXT NOT NULL,
                user_id     TEXT,
                event_type  TEXT NOT NULL,
                occurred_at TEXT NOT NULL DEFAULT (datetime('now')),
                resolved_at TEXT
            );

            CREATE TABLE IF NOT EXISTS EVENT_LOG (
                event_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                robot_id     TEXT NOT NULL,
                user_id      TEXT,
                event_type   TEXT NOT NULL,
                event_detail TEXT,
                occurred_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
        conn.close()


def upsert_robot_status(robot_id: str, mode: str, pos_x: float, pos_y: float,
                        battery: int, last_seen: str) -> None:
    """Insert or update robot status row."""
    with _lock:
        conn = _get_conn()
        conn.execute("""
            INSERT INTO ROBOT (robot_id, current_mode, pos_x, pos_y, battery_level, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(robot_id) DO UPDATE SET
                current_mode=excluded.current_mode,
                pos_x=excluded.pos_x,
                pos_y=excluded.pos_y,
                battery_level=excluded.battery_level,
                last_seen=excluded.last_seen
        """, (robot_id, mode, pos_x, pos_y, battery, last_seen))
        conn.commit()
        conn.close()


def insert_alarm(robot_id: str, event_type: str, user_id: str = None) -> int:
    """Insert a new alarm log entry. Returns log_id."""
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            "INSERT INTO ALARM_LOG (robot_id, user_id, event_type) VALUES (?, ?, ?)",
            (robot_id, user_id, event_type),
        )
        log_id = cur.lastrowid
        conn.commit()
        conn.close()
    return log_id


def resolve_alarm(robot_id: str) -> None:
    """Resolve the latest unresolved alarm for robot_id."""
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            "SELECT log_id FROM ALARM_LOG WHERE robot_id=? AND resolved_at IS NULL "
            "ORDER BY occurred_at DESC LIMIT 1",
            (robot_id,),
        )
        row = cur.fetchone()
        if row:
            conn.execute(
                "UPDATE ALARM_LOG SET resolved_at=datetime('now') WHERE log_id=?",
                (row['log_id'],),
            )
            conn.commit()
        conn.close()


def log_event(robot_id: str, user_id: str, event_type: str, detail: str = '') -> None:
    """Insert an event into EVENT_LOG."""
    with _lock:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO EVENT_LOG (robot_id, user_id, event_type, event_detail) "
            "VALUES (?, ?, ?, ?)",
            (robot_id, user_id, event_type, detail),
        )
        conn.commit()
        conn.close()


def get_zone(zone_id: int) -> dict:
    """Return zone row as dict, or empty dict if not found."""
    with _lock:
        conn = _get_conn()
        cur = conn.execute("SELECT * FROM ZONE WHERE zone_id=?", (zone_id,))
        row = cur.fetchone()
        conn.close()
    return dict(row) if row else {}


def find_product(query: str) -> list:
    """Search products by name (LIKE). Returns list of dicts."""
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            "SELECT * FROM PRODUCT WHERE product_name LIKE ?",
            (f'%{query}%',),
        )
        rows = cur.fetchall()
        conn.close()
    return [dict(r) for r in rows]
