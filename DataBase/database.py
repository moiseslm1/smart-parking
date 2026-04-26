import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'quickspot.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:

        #Users
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username       TEXT    NOT NULL UNIQUE,
                password_hash  TEXT    NOT NULL,
                email_address  TEXT    NOT NULL UNIQUE
            )
        ''')

        #Parking lots
        conn.execute('''
            CREATE TABLE IF NOT EXISTS parking_lots (
                lot_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                lot_name     TEXT    NOT NULL,
                total_spots  INTEGER NOT NULL,
                lat          REAL    NOT NULL,
                lng          REAL    NOT NULL,
                zip          TEXT    NOT NULL,
                address      TEXT    NOT NULL,
                category     TEXT    NOT NULL DEFAULT 'other'
            )
        ''')

        try:
            conn.execute("ALTER TABLE parking_lots ADD COLUMN category TEXT NOT NULL DEFAULT 'other'")
        except Exception:
            pass

        #Parked spots
        conn.execute('''
            CREATE TABLE IF NOT EXISTS parked_spots (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL UNIQUE,
                lot_id     INTEGER NOT NULL,
                spot_id    INTEGER NOT NULL,
                parked_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        #Reservations (with spot_id)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                lot_id         INTEGER NOT NULL,
                spot_id        INTEGER NOT NULL,
                date           TEXT    NOT NULL,
                time           TEXT    NOT NULL,
                duration       INTEGER NOT NULL DEFAULT 60,
                created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (lot_id)  REFERENCES parking_lots(lot_id)
            )
        ''')
        try:
            conn.execute("ALTER TABLE reservations ADD COLUMN spot_id INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass

        # Seed lots only if table is empty
        count = conn.execute('SELECT COUNT(*) FROM parking_lots').fetchone()[0]
        if count == 0:
            seed_lots = [
                ("Cerritos Mall",       150, 33.8625, -118.0927, "90703", "239 Los Cerritos Center, Cerritos, CA",    "mall"),
                ("Stonewood Mall",       32, 33.9355, -118.1194, "90241", "251 Stonewood St, Downey, CA",              "mall"),
                ("EOS Fitness",          20, 33.8301, -118.0736, "90716", "12120 E Carson St, Hawaiian Gardens, CA",   "gym"),
                ("LA Fitness",           15, 33.9464, -118.1540, "90242", "8550 Florence Ave, Downey, CA",             "gym"),
                ("Olive Garden",         40, 33.8661, -118.0964, "90703", "450 Los Cerritos Center, Cerritos, CA",     "restaurant"),
                ("Chili's Grill & Bar",  35, 33.8541, -118.1354, "90712", "4931 Candlewood St, Lakewood, CA",          "restaurant"),
            ]
            conn.executemany('''
                INSERT INTO parking_lots (lot_name, total_spots, lat, lng, zip, address, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', seed_lots)

        conn.commit()


#Parking lot queries

def get_all_lots():
    with get_db() as conn:
        return conn.execute('SELECT * FROM parking_lots ORDER BY lot_id').fetchall()


def get_lots_by_category(category):
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM parking_lots WHERE category = ? ORDER BY lot_name',
            (category,)
        ).fetchall()


def get_lot_by_id(lot_id):
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM parking_lots WHERE lot_id = ?', (lot_id,)
        ).fetchone()


def add_lot(lot_name, total_spots, lat, lng, zip_code, address, category='other'):
    with get_db() as conn:
        cursor = conn.execute('''
            INSERT INTO parking_lots (lot_name, total_spots, lat, lng, zip, address, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (lot_name, total_spots, lat, lng, zip_code, address, category))
        conn.commit()
        return cursor.lastrowid


def delete_lot(lot_id):
    with get_db() as conn:
        cursor = conn.execute('SELECT lot_name FROM parking_lots WHERE lot_id = ?', (lot_id,))
        lot = cursor.fetchone()

        if not lot:
            print("Lot not found.")
            return

        print(f"Deleting: {lot[0]}")
        conn.execute('DELETE FROM parking_lots WHERE lot_id = ?', (lot_id,))
        conn.commit()


#Parked spot queries

def save_parked_spot(user_id, lot_id, spot_id):
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
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM parked_spots WHERE user_id = ?', (user_id,)
        ).fetchone()


def clear_parked_spot(user_id):
    with get_db() as conn:
        conn.execute('DELETE FROM parked_spots WHERE user_id = ?', (user_id,))
        conn.commit()


# ── Reservation queries

def create_reservation(user_id, lot_id, spot_id, date, time, duration):
    with get_db() as conn:
        cursor = conn.execute('''
            INSERT INTO reservations (user_id, lot_id, spot_id, date, time, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, lot_id, spot_id, date, time, duration))
        conn.commit()
        return cursor.lastrowid


def get_user_reservations(user_id):
    with get_db() as conn:
        return conn.execute('''
            SELECT r.*, p.lot_name, p.address, p.category
            FROM reservations r
            JOIN parking_lots p ON r.lot_id = p.lot_id
            WHERE r.user_id = ?
            ORDER BY r.date, r.time
        ''', (user_id,)).fetchall()


def get_lot_reservations(lot_id):
    """Return all upcoming reservations for a lot as a dict keyed by spot_id."""
    from datetime import date
    today = date.today().isoformat()
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM reservations WHERE lot_id = ? AND date >= ? ORDER BY date, time',
            (lot_id, today)
        ).fetchall()
    # Build a dict: spot_id -> reservation row
    return {row['spot_id']: dict(row) for row in rows}


def get_reserved_spot_ids(lot_id, user_id):
    """Return set of spot_ids this user has reserved in this lot (upcoming only)."""
    from datetime import date
    today = date.today().isoformat()
    with get_db() as conn:
        rows = conn.execute(
            'SELECT spot_id FROM reservations WHERE lot_id = ? AND user_id = ? AND date >= ?',
            (lot_id, user_id, today)
        ).fetchall()
    return {row['spot_id'] for row in rows}


def delete_reservation(reservation_id, user_id):
    with get_db() as conn:
        conn.execute(
            'DELETE FROM reservations WHERE reservation_id = ? AND user_id = ?',
            (reservation_id, user_id)
        )
        conn.commit()


#User queries

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