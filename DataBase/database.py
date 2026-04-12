import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'quickspot.db')


def get_db():
    """Open a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables and seed lot data if the table is empty."""
    with get_db() as conn:

        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username       TEXT    NOT NULL UNIQUE,
                password_hash  TEXT    NOT NULL,
                email_address  TEXT    NOT NULL UNIQUE
            )
        ''')

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


def get_all_lots():
    """Return all parking lots as a list of Row objects."""
    with get_db() as conn:
        return conn.execute('SELECT * FROM parking_lots ORDER BY lot_id').fetchall()


def get_lot_by_id(lot_id):
    """Return a single lot by primary key."""
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM parking_lots WHERE lot_id = ?', (lot_id,)
        ).fetchone()


def add_lot(lot_name, total_spots, lat, lng, zip_code, address):
    """
    Insert a new parking lot. Returns the new lot_id.
    Call this whenever you want to add a new lot — no need to touch app.py.
    """
    with get_db() as conn:
        cursor = conn.execute('''
            INSERT INTO parking_lots (lot_name, total_spots, lat, lng, zip, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (lot_name, total_spots, lat, lng, zip_code, address))
        conn.commit()
        return cursor.lastrowid


def update_lot(lot_id, lot_name=None, total_spots=None, lat=None, lng=None, zip_code=None, address=None):
    """Update individual fields on an existing lot."""
    fields, values = [], []
    if lot_name    is not None: fields.append('lot_name = ?');    values.append(lot_name)
    if total_spots is not None: fields.append('total_spots = ?'); values.append(total_spots)
    if lat         is not None: fields.append('lat = ?');         values.append(lat)
    if lng         is not None: fields.append('lng = ?');         values.append(lng)
    if zip_code    is not None: fields.append('zip = ?');         values.append(zip_code)
    if address     is not None: fields.append('address = ?');     values.append(address)
    if not fields:
        return
    values.append(lot_id)
    with get_db() as conn:
        conn.execute(f'UPDATE parking_lots SET {", ".join(fields)} WHERE lot_id = ?', values)
        conn.commit()


def delete_lot(lot_id):
    """Remove a lot from the database."""
    with get_db() as conn:
        conn.execute('DELETE FROM parking_lots WHERE lot_id = ?', (lot_id,))
        conn.commit()



def create_user(username, password_hash, email_address):
    """Insert a new user. Returns the new user_id, or None on duplicate."""
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