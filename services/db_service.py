from db import get_db
from datetime import datetime
from services.tcgdex_service import get_card_raw_by_tcgdex_id, extract_market_price_usd


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
        SELECT
            w.watchlist_id,
            w.user_id,
            w.card_id,
            w.target_price,
            w.alert_direction,
            w.date_added,
            c.card_name,
            c.card_number,
            c.rarity,
            c.type,
            c.image_url,
            s.set_name,
            p.price_value AS current_price,
            p.source AS price_source,
            p.recorded_at AS price_updated_at
        FROM watchlist w
        JOIN cards c ON w.card_id = c.card_id
        LEFT JOIN sets s ON c.set_id = s.set_id
        LEFT JOIN price_history p ON p.price_id = (
            SELECT ph.price_id
            FROM price_history ph
            WHERE ph.card_id = c.card_id
            ORDER BY ph.recorded_at DESC
            LIMIT 1
        )
        WHERE w.user_id = ?
        ORDER BY w.date_added DESC
    """, (user_id,)).fetchall()
    # return db.execute("""
    #     SELECT watchlist.watchlist_id,
    #            users.username,
    #            cards.card_name,
    #            cards.rarity,
    #            watchlist.target_price,
    #            watchlist.alert_direction
    #     FROM watchlist
    #     JOIN users ON watchlist.user_id = users.user_id
    #     JOIN cards ON watchlist.card_id = cards.card_id
    #     WHERE users.user_id = ?
    # """, (user_id,)).fetchall()

def get_watchlist_price_analysis(user_id):
    db = get_db()

    return db.execute("""
        SELECT
            w.watchlist_id,
            w.user_id,
            w.card_id,
            w.target_price,
            w.alert_direction,
            w.date_added,

            c.card_name,
            c.card_number,
            c.rarity,
            c.type,
            c.image_url,

            s.set_name,

            p.price_value AS current_price,
            p.source AS price_source,
            p.recorded_at AS price_updated_at,

            ROUND(p.price_value - w.target_price, 2) AS price_difference,

            CASE
                WHEN p.price_value IS NULL THEN NULL
                WHEN w.target_price IS NULL OR w.target_price = 0 THEN NULL
                ELSE ROUND(((p.price_value - w.target_price) / w.target_price) * 100, 2)
            END AS percent_difference,

            CASE
                WHEN p.price_value IS NULL THEN 'No Price Data'
                WHEN w.target_price IS NULL OR w.target_price = 0 THEN 'No Target'

                WHEN w.alert_direction = 'below'
                    AND p.price_value <= w.target_price
                THEN 'Triggered'

                WHEN w.alert_direction = 'above'
                    AND p.price_value >= w.target_price
                THEN 'Triggered'

                WHEN ABS((p.price_value - w.target_price) / w.target_price) <= 0.10
                THEN 'Buy Now'

                WHEN ABS((p.price_value - w.target_price) / w.target_price) <= 0.20
                THEN 'Almost There'

                WHEN ABS((p.price_value - w.target_price) / w.target_price) <= 0.30
                THEN 'Keep Watching'

                ELSE 'Not Close'
            END AS alert_status

        FROM watchlist w
        JOIN cards c ON w.card_id = c.card_id
        LEFT JOIN sets s ON c.set_id = s.set_id
        LEFT JOIN price_history p ON p.price_id = (
            SELECT ph.price_id
            FROM price_history ph
            WHERE ph.card_id = c.card_id
            ORDER BY ph.recorded_at DESC
            LIMIT 1
        )
        WHERE w.user_id = ?
        ORDER BY
            CASE
                WHEN p.price_value IS NULL THEN 7
                WHEN w.target_price IS NULL OR w.target_price = 0 THEN 6

                WHEN w.alert_direction = 'below'
                    AND p.price_value <= w.target_price
                THEN 1

                WHEN w.alert_direction = 'above'
                    AND p.price_value >= w.target_price
                THEN 1

                WHEN ABS((p.price_value - w.target_price) / w.target_price) <= 0.10
                THEN 2

                WHEN ABS((p.price_value - w.target_price) / w.target_price) <= 0.20
                THEN 3

                WHEN ABS((p.price_value - w.target_price) / w.target_price) <= 0.30
                THEN 4

                ELSE 5
            END,
            ABS(p.price_value - w.target_price) ASC
    """, (user_id,)).fetchall()

def get_watchlist_analysis_stats(user_id):
    db = get_db()

    return db.execute("""
        SELECT
            COUNT(*) AS total_cards,
            COUNT(p.price_value) AS cards_with_price_data,
            COUNT(*) - COUNT(p.price_value) AS cards_missing_price_data,
            ROUND(AVG(p.price_value), 2) AS average_current_price,
            ROUND(SUM(p.price_value), 2) AS total_estimated_value,
            ROUND(MAX(p.price_value), 2) AS highest_current_price,
            ROUND(MIN(p.price_value), 2) AS lowest_current_price,

            SUM(
                CASE
                    WHEN p.price_value IS NOT NULL
                         AND w.target_price IS NOT NULL
                         AND w.target_price > 0
                         AND w.alert_direction = 'below'
                         AND p.price_value <= w.target_price
                    THEN 1

                    WHEN p.price_value IS NOT NULL
                         AND w.target_price IS NOT NULL
                         AND w.target_price > 0
                         AND w.alert_direction = 'above'
                         AND p.price_value >= w.target_price
                    THEN 1

                    ELSE 0
                END
            ) AS triggered_count,

            SUM(
                CASE
                    WHEN p.price_value IS NOT NULL
                         AND w.target_price IS NOT NULL
                         AND w.target_price > 0
                         AND ABS((p.price_value - w.target_price) / w.target_price) <= 0.10
                    THEN 1
                    ELSE 0
                END
            ) AS buy_now_count,

            SUM(
                CASE
                    WHEN p.price_value IS NOT NULL
                         AND w.target_price IS NOT NULL
                         AND w.target_price > 0
                         AND ABS((p.price_value - w.target_price) / w.target_price) > 0.10
                         AND ABS((p.price_value - w.target_price) / w.target_price) <= 0.20
                    THEN 1
                    ELSE 0
                END
            ) AS almost_there_count,

            SUM(
                CASE
                    WHEN p.price_value IS NOT NULL
                         AND w.target_price IS NOT NULL
                         AND w.target_price > 0
                         AND ABS((p.price_value - w.target_price) / w.target_price) > 0.20
                         AND ABS((p.price_value - w.target_price) / w.target_price) <= 0.30
                    THEN 1
                    ELSE 0
                END
            ) AS keep_watching_count,

            (
                SELECT c2.card_name
                FROM watchlist w2
                JOIN cards c2 ON w2.card_id = c2.card_id
                LEFT JOIN price_history p2 ON p2.price_id = (
                    SELECT ph2.price_id
                    FROM price_history ph2
                    WHERE ph2.card_id = c2.card_id
                    ORDER BY ph2.recorded_at DESC
                    LIMIT 1
                )
                WHERE w2.user_id = ?
                  AND p2.price_value IS NOT NULL
                  AND w2.target_price IS NOT NULL
                  AND w2.target_price > 0
                ORDER BY ABS(p2.price_value - w2.target_price) ASC
                LIMIT 1
            ) AS best_opportunity_card,

            (
                SELECT ROUND(ABS(p2.price_value - w2.target_price), 2)
                FROM watchlist w2
                JOIN cards c2 ON w2.card_id = c2.card_id
                LEFT JOIN price_history p2 ON p2.price_id = (
                    SELECT ph2.price_id
                    FROM price_history ph2
                    WHERE ph2.card_id = c2.card_id
                    ORDER BY ph2.recorded_at DESC
                    LIMIT 1
                )
                WHERE w2.user_id = ?
                  AND p2.price_value IS NOT NULL
                  AND w2.target_price IS NOT NULL
                  AND w2.target_price > 0
                ORDER BY ABS(p2.price_value - w2.target_price) ASC
                LIMIT 1
            ) AS best_opportunity_difference,

            (
                SELECT ROUND(ABS((p2.price_value - w2.target_price) / w2.target_price) * 100, 2)
                FROM watchlist w2
                JOIN cards c2 ON w2.card_id = c2.card_id
                LEFT JOIN price_history p2 ON p2.price_id = (
                    SELECT ph2.price_id
                    FROM price_history ph2
                    WHERE ph2.card_id = c2.card_id
                    ORDER BY ph2.recorded_at DESC
                    LIMIT 1
                )
                WHERE w2.user_id = ?
                  AND p2.price_value IS NOT NULL
                  AND w2.target_price IS NOT NULL
                  AND w2.target_price > 0
                ORDER BY ABS((p2.price_value - w2.target_price) / w2.target_price) ASC
                LIMIT 1
            ) AS best_opportunity_percent

        FROM watchlist w
        JOIN cards c ON w.card_id = c.card_id
        LEFT JOIN price_history p ON p.price_id = (
            SELECT ph.price_id
            FROM price_history ph
            WHERE ph.card_id = c.card_id
            ORDER BY ph.recorded_at DESC
            LIMIT 1
        )
        WHERE w.user_id = ?
    """, (user_id, user_id, user_id, user_id)).fetchone()

def get_average_watchlist_price(user_id):
    db = get_db()

    row = db.execute("""
        SELECT AVG(latest_prices.price_value) AS average_price
        FROM watchlist w
        JOIN (
            SELECT ph.card_id, ph.price_value
            FROM price_history ph
            JOIN (
                SELECT card_id, MAX(recorded_at) AS latest_recorded_at
                FROM price_history
                GROUP BY card_id
            ) latest
                ON ph.card_id = latest.card_id
               AND ph.recorded_at = latest.latest_recorded_at
        ) latest_prices
            ON w.card_id = latest_prices.card_id
        WHERE w.user_id = ?
    """, (user_id,)).fetchone()

    return row["average_price"]

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



# for importing card prices

def get_all_cards_for_price_import():
    db = get_db()
    rows = db.execute("""
        SELECT card_id, tcgdex_card_id, card_name
        FROM cards
        WHERE tcgdex_card_id IS NOT NULL
        ORDER BY card_id
    """).fetchall()

    return [dict(row) for row in rows]


def insert_price_history_row(card_id, price_value, price_type, source, recorded_at):
    db = get_db()
    db.execute("""
        INSERT INTO price_history (card_id, price_value, price_type, source, recorded_at)
        VALUES (?, ?, ?, ?, ?)
    """, (card_id, price_value, price_type, source, recorded_at))
    db.commit()



def get_card_by_id(card_id: int):
    db = get_db()
    row = db.execute("""
        SELECT card_id, tcgdex_card_id, card_name
        FROM cards
        WHERE card_id = ?
    """, (card_id,)).fetchone()

    return dict(row) if row else None

from datetime import datetime
from services.tcgdex_service import get_card_raw_by_tcgdex_id, extract_market_price_usd

def refresh_card_market_price(card_id: int):
    card = get_card_by_id(card_id)
    if not card:
        return {"success": False, "message": "Card not found."}
    

    card_json = get_card_raw_by_tcgdex_id(card["tcgdex_card_id"])
    price_info = extract_market_price_usd(card_json)

    print(card["card_name"])
    print(card_json.get("pricing"))

    if price_info is None:
        return {"success": False, "message": "No market price available for this card."}

    insert_price_history_row(
        card_id=card["card_id"],
        price_value=price_info["price_value"],
        price_type=price_info["price_type"],
        source=price_info["source"],
        recorded_at=datetime.now().isoformat()
    )

    return {
        "success": True,
        "message": f"Saved current market price for {card['card_name']}.",
        "price_value": price_info["price_value"],
        "source": price_info["source"]
    }


    