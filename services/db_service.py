from db import get_db
from datetime import datetime


def create_user(username, email, password_hash):
    db = get_db()
    db.execute("""
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    """, (username, email, password_hash, datetime.now().isoformat()))
    db.commit()


def get_watchlist(user_id):
    db = get_db()

    return db.execute("""
        SELECT watchlist.watchlist_id,
               users.username,
               cards.card_name,
               cards.rarity,
               watchlist.target_price,
               watchlist.alert_direction
        FROM watchlist
        JOIN users ON watchlist.user_id = users.user_id
        JOIN cards ON watchlist.card_id = cards.card_id
        WHERE users.user_id = ?
    """, (user_id,)).fetchall()



def insert_set_to_db(tcgdex_set_id, set_name, release_date, series):
    db = get_db()
    db.execute("""
               INSERT OR IGNORE INTO sets (tcgdex_set_id, set_name, release_date, series)
               VALUES (?, ?, ?, ?)""", (tcgdex_set_id, set_name, release_date, series))
    
    db.commit()


def get_all_sets_from_db():
    db = get_db()
    return db.execute("""
        SELECT set_id, tcgdex_set_id, set_name
        FROM sets
        ORDER BY set_name
    """).fetchall()

def insert_card(tcgdex_card_id, card_name, card_number, rarity, card_type, set_id, image_url):
    db = get_db()
    db.execute("""
        INSERT OR IGNORE INTO cards
        (tcgdex_card_id, card_name, card_number, rarity, type, set_id, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (tcgdex_card_id, card_name, card_number, rarity, card_type, set_id, image_url))
    db.commit()




    