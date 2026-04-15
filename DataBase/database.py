import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'quickspot.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:

        # ── Users ────────────────────────────────────────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username       TEXT    NOT NULL UNIQUE,
                password_hash  TEXT    NOT NULL,
                email_address  TEXT    NOT NULL UNIQUE
            )
        ''')

        # ── Parking lots ─────────────────────────────────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS parking_lots (
                lot_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                lot_name     TEXT    NOT NULL,
                total_spots  INTEGER NOT NULL,
                lat          REAL    NOT NULL,
                lng          REAL    NOT NULL,
                zip          TEXT    NOT NULL,
                address      TEXT    NOT NULL
            )
        ''')

        # ── Parked spots (one active spot per user) ──────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS parked_spots (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL UNIQUE,  -- one spot per user
                lot_id     INTEGER NOT NULL,
                spot_id    INTEGER NOT NULL,
                parked_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Seed lots only if table is empty
        count = conn.execute('SELECT COUNT(*) FROM parking_lots').fetchone()[0]
        if count == 0:
            seed_lots = [
                ("Cerritos Mall",  150, 33.8742, -118.0684, "90703", "239 Los Cerritos Center, Cerritos, CA"),
                ("EOS Fitness",     20, 33.8656, -118.0751, "90703", "12500 Centralia St, Lakewood, CA"),
                ("Stonewood Mall",  32, 33.9000, -118.1006, "90242", "251 Stonewood St, Downey, CA"),
                ("LA Fitness",      15, 33.8850, -118.0920, "90242", "8550 Florence Ave, Downey, CA"),
            ]
            conn.executemany('''
                INSERT INTO parking_lots (lot_name, total_spots, lat, lng, zip, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', seed_lots)

        conn.commit()


# ── Parking lot queries ───────────────────────────────────────────

def get_all_lots():
    with get_db() as conn:
        return conn.execute('SELECT * FROM parking_lots ORDER BY lot_id').fetchall()


def get_lot_by_id(lot_id):
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM parking_lots WHERE lot_id = ?', (lot_id,)
        ).fetchone()


def add_lot(lot_name, total_spots, lat, lng, zip_code, address):
    with get_db() as conn:
        cursor = conn.execute('''
            INSERT INTO parking_lots (lot_name, total_spots, lat, lng, zip, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (lot_name, total_spots, lat, lng, zip_code, address))
        conn.commit()
        return cursor.lastrowid


def delete_lot(lot_id):
    with get_db() as conn:
        conn.execute('DELETE FROM parking_lots WHERE lot_id = ?', (lot_id,))
        conn.commit()


# ── Parked spot queries ───────────────────────────────────────────

def save_parked_spot(user_id, lot_id, spot_id):
    """
    Save or update the user's active parked spot.
    A user can only have one active spot — this replaces any previous one.
    """
    with get_db() as conn:
        conn.execute('''
            INSERT INTO parked_spots (user_id, lot_id, spot_id)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                lot_id    = excluded.lot_id,
                spot_id   = excluded.spot_id,
                parked_at = CURRENT_TIMESTAMP
        ''', (user_id, lot_id, spot_id))
        conn.commit()


def get_parked_spot(user_id):
    """Return the user's current parked spot row, or None."""
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM parked_spots WHERE user_id = ?', (user_id,)
        ).fetchone()


def clear_parked_spot(user_id):
    """Remove the user's active parked spot (they've left)."""
    with get_db() as conn:
        conn.execute('DELETE FROM parked_spots WHERE user_id = ?', (user_id,))
        conn.commit()


# ── User queries ──────────────────────────────────────────────────

def create_user(username, password_hash, email_address):
    try:
        with get_db() as conn:
            cursor = conn.execute(
                'INSERT INTO users (username, password_hash, email_address) VALUES (?, ?, ?)',
                (username, password_hash, email_address)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None


def get_user_by_email(email_address):
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM users WHERE email_address = ?', (email_address,)
        ).fetchone()


def get_user_by_id(user_id):
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,)
        ).fetchone()


def get_user_by_username(username):
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()