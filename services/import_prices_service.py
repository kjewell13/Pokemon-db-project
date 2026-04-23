from datetime import datetime

from app.app import app
from db import get_db
from services.tcgdex_service import get_card_by_tcgdexId, get_card_raw_by_tcgdex_id
from services.db_service import (
    get_all_cards_for_price_import,
    insert_price_history_row,
)


def extract_market_price(card_json):
    if not card_json:
        return None

    pricing = card_json.get("pricing")
    if not pricing:
        return None

    tcgplayer = pricing.get("tcgplayer")
    if not tcgplayer:
        return None

    normal = tcgplayer.get("normal")
    if normal and normal.get("marketPrice") is not None:
        return float(normal["marketPrice"])

    reverse = tcgplayer.get("reverse")
    if reverse and reverse.get("marketPrice") is not None:
        return float(reverse["marketPrice"])

    holofoil = tcgplayer.get("holofoil")
    if holofoil and holofoil.get("marketPrice") is not None:
        return float(holofoil["marketPrice"])

    return None


def import_market_prices():
    db = get_db()
    cards = get_all_cards_for_price_import()

    inserted_count = 0
    skipped_count = 0
    timestamp = datetime.now().isoformat()

    print(f"Found {len(cards)} cards in local database.")

    for index, card in enumerate(cards, start=1):
        local_card_id = card["card_id"]
        tcgdex_card_id = card["tcgdex_card_id"]
        card_name = card["card_name"]

        try:
            # api_card = get_card_by_tcgdexId(tcgdex_card_id)
            # print("CARD TYPE:", type(api_card))
            # print("PRICING TYPE:", type(api_card.pricing))
            # print("PRICING VALUE:", api_card.pricing)
            # api_card = get_card_by_tcgdexId("base1-4")

            # print("TYPE:", type(api_card))
            # print("DIR HAS pricing?", "pricing" in dir(api_card))
            # print("DICT:", getattr(api_card, "__dict__", None))
            # print("DIR:", dir(api_card))
            

            # market_price = extract_market_price(api_card)

            # card_json = get_card_raw_by_tcgdex_id(tcgdex_card_id)
            card_json = get_card_raw_by_tcgdex_id("base1-4")
            print(card_json.get("pricing"))
            print(extract_market_price(card_json))
            # market_price = extract_market_price(card_json)

            raise SystemExit

            if market_price is None:
                skipped_count += 1
                print(f"[{index}] Skipped {card_name} ({tcgdex_card_id}) - no market price found")
                continue

            insert_price_history_row(
                db=db,
                card_id=local_card_id,
                price_value=market_price,
                price_type="market",
                source="tcgplayer",
                recorded_at=timestamp
            )

            inserted_count += 1

            if index % 100 == 0:
                print(f"Processed {index}/{len(cards)} cards...")

        except Exception as exc:
            skipped_count += 1
            print(f"[{index}] Error on {card_name} ({tcgdex_card_id}): {exc}")

    db.commit()

    print(f"Done. Inserted {inserted_count} price rows. Skipped {skipped_count}.")
    return {
        "success": True,
        "inserted": inserted_count,
        "skipped": skipped_count
    }


def main():
    with app.app_context():
        print("Starting market price import...")
        result = import_market_prices()
        print(result)
        print("Price import complete.")


if __name__ == "__main__":
    main()