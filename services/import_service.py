# used to import cards and sets from tcg dex api -- for seeding database
from tcgdexsdk import TCGdex, Query
from services.tcgdex_service import fetch_all_sets, fetch_cards_by_set
from services.db_service import insert_set_to_db, get_all_sets_from_db, insert_card


def import_all_sets():
    all_sets = fetch_all_sets()

    print("Returned object type:", type(all_sets))
    try:
        print("Number of sets:", len(all_sets))
    except TypeError:
        print("Cannot get len(all_sets)")

    for i, api_set in enumerate(all_sets):
        print("DEBUG SET:", i, getattr(api_set, "id", None), getattr(api_set, "name", None))
        if i >= 9:
            break
    inserted = 0

    for api_set in all_sets:
        tcgdex_set_id = getattr(api_set, "id", None)
        set_name = getattr(api_set, "name", None)
        release_date = getattr(api_set, "releaseDate", None)

        series_obj = getattr(api_set, "serie", None)
        series_name = getattr(series_obj, "name", None) if series_obj else None

        if not tcgdex_set_id or not set_name:
            continue

        insert_set_to_db(tcgdex_set_id, set_name, release_date, series_name)
        inserted += 1

    return {
        "success": True,
        "message": f"Processed {inserted} sets."
    }
    

def import_cards_for_all_sets():
    sets = get_all_sets_from_db()
    total_cards_processed = 0
    sets_processed = 0

    for db_set in sets:
        internal_set_id = db_set["set_id"]
        tcgdex_set_id = db_set["tcgdex_set_id"]

        cards = fetch_cards_by_set(tcgdex_set_id)

        for api_card in cards:
            tcgdex_card_id = getattr(api_card, "id", None)
            card_name = getattr(api_card, "name", None)
            card_number = getattr(api_card, "localId", None)
            rarity = getattr(api_card, "rarity", None)

            card_types = getattr(api_card, "types", None)
            card_type = ", ".join(card_types) if card_types else None

            image_url = getattr(api_card, "image", None)

            if not tcgdex_card_id or not card_name:
                continue

            insert_card(
                tcgdex_card_id=tcgdex_card_id,
                card_name=card_name,
                card_number=card_number,
                rarity=rarity,
                card_type=card_type,
                set_id=internal_set_id,
                image_url=image_url
            )
            total_cards_processed += 1

        sets_processed += 1

    return {
        "success": True,
        "message": f"Processed cards for {sets_processed} sets and attempted to import {total_cards_processed} cards."
    }


def main():
    print("Starting Pokémon database import...")

    print("Importing sets...")
    result_sets = import_all_sets()
    print(result_sets)

    print("Importing cards...")
    result_cards = import_cards_for_all_sets()
    print(result_cards)

    print("Import complete.")

if __name__ == "__main__":
    main()