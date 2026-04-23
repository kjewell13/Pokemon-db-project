import sqlite3

def create_database():
    conn = sqlite3.connect("database/pokemon_tracker.db")
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sets (
        set_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tcgdex_set_id TEXT NOT NULL UNIQUE,
        set_name TEXT NOT NULL,
        release_date TEXT,
        series TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        card_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tcgdex_card_id TEXT NOT NULL UNIQUE,
        card_name TEXT NOT NULL,
        card_number TEXT,
        rarity TEXT,
        type TEXT,
        set_id INTEGER,
        image_url TEXT,
        FOREIGN KEY (set_id) REFERENCES sets(set_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        price_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        price_value REAL NOT NULL,
        price_type TEXT,
        source TEXT,
        recorded_at TEXT NOT NULL,
        FOREIGN KEY (card_id) REFERENCES cards(card_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (
        watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        card_id INTEGER NOT NULL,
        target_price REAL,
        alert_direction TEXT,
        date_added TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (card_id) REFERENCES cards(card_id),
        UNIQUE(user_id, card_id)
    );
    """)

    conn.commit()
    conn.close()
    print("Database created successfully.")

if __name__ == "__main__":
    create_database()