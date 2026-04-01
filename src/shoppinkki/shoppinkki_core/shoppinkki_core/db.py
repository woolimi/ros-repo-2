"""Pi 5 local SQLite DB — schema init and CRUD stubs."""

import sqlite3
import os

_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pi.db')


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(_DB_PATH)), exist_ok=True)
    return sqlite3.connect(_DB_PATH)


def init_db() -> None:
    """Create all tables if they do not exist."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS SESSION (
            session_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id     INTEGER NOT NULL,
            user_id      TEXT NOT NULL,
            is_active    INTEGER NOT NULL DEFAULT 1,
            created_at   TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at   TEXT
            -- 유효 세션 판단: is_active=1 AND expires_at > datetime('now')
            -- is_active=0: 명시적 종료(로그아웃/강제종료)
            -- expires_at 초과: 자동 만료 — is_active=1이어도 무효
        );

        CREATE TABLE IF NOT EXISTS POSE_DATA (
            pose_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id       INTEGER NOT NULL REFERENCES SESSION(session_id),
            direction        TEXT NOT NULL,
            hsv_top_json     TEXT,
            hsv_bottom_json  TEXT
        );

        CREATE TABLE IF NOT EXISTS CART (
            cart_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id   INTEGER NOT NULL UNIQUE REFERENCES SESSION(session_id),
            created_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS CART_ITEM (
            item_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id      INTEGER NOT NULL REFERENCES CART(cart_id),
            product_name TEXT NOT NULL,
            price        INTEGER NOT NULL,
            added_at     TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


# --- Session CRUD stubs ---

def create_session(user_id: str, robot_id: int) -> int:
    """Create a new session and return session_id."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO SESSION (user_id, robot_id) VALUES (?, ?)",
        (user_id, robot_id),
    )
    session_id = cur.lastrowid
    cur.execute("INSERT INTO CART (session_id) VALUES (?)", (session_id,))
    conn.commit()
    conn.close()
    return session_id


def close_session(session_id: int) -> None:
    """Explicitly terminate session (is_active=0) and delete pose data."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE SESSION SET is_active=0 WHERE session_id=?", (session_id,))
    cur.execute("DELETE FROM POSE_DATA WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()


def is_valid_session(session_id: int) -> bool:
    """Return True if session is active AND not expired.

    Valid condition: is_active=1 AND (expires_at IS NULL OR expires_at > now()).
    is_active=0 → explicitly terminated (logout / force_terminate).
    expires_at exceeded → auto-expired (timeout), regardless of is_active.
    """
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM SESSION WHERE session_id=? AND is_active=1 "
        "AND (expires_at IS NULL OR expires_at > datetime('now'))",
        (session_id,),
    )
    result = cur.fetchone() is not None
    conn.close()
    return result


# --- Cart CRUD stubs ---

def add_cart_item(session_id: int, product_name: str, price: int) -> int:
    """Add item to cart. Returns item_id."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cart_id FROM CART WHERE session_id=?", (session_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise ValueError(f'No cart for session_id={session_id}')
    cart_id = row[0]
    cur.execute(
        "INSERT INTO CART_ITEM (cart_id, product_name, price) VALUES (?,?,?)",
        (cart_id, product_name, price),
    )
    item_id = cur.lastrowid
    conn.commit()
    conn.close()
    return item_id


def delete_cart_item(item_id: int) -> None:
    """Delete a cart item by item_id."""
    conn = _get_conn()
    conn.execute("DELETE FROM CART_ITEM WHERE item_id=?", (item_id,))
    conn.commit()
    conn.close()


def get_cart_items(session_id: int) -> list:
    """Return list of dicts for all cart items in session."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT ci.item_id, ci.product_name, ci.price
        FROM CART_ITEM ci
        JOIN CART c ON ci.cart_id = c.cart_id
        WHERE c.session_id = ?
    """, (session_id,))
    rows = cur.fetchall()
    conn.close()
    return [{'item_id': r[0], 'product_name': r[1], 'price': r[2]} for r in rows]
