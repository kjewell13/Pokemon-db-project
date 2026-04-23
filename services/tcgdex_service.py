from tcgdexsdk import TCGdex, Query
import requests

tcgdex = TCGdex()


# def test_card():
#     try:
#         card = tcgdex.card.getSync("swsh3-136")
#         print("Connected successfully.")
#         print(f"Name: {card.name}")
#         print(f"Local ID: {card.localId}")
#         print(f"Set: {card.set.name}")
#         print(f"HP: {card.hp}")
#         return card
#     except Exception as e:
#         print(f"TCGdex test failed: {e}")
#         return None

BASE_URL = "https://api.tcgdex.net/v2/en"

def get_card_raw_by_tcgdex_id(tcgdex_card_id: str):
    url = f"{BASE_URL}/cards/{tcgdex_card_id}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()
    
def get_card_by_id(card_id):
    return tcgdex.card.getSync(card_id)

def get_card_by_tcgdexId(tcgdex_card_id: str):
    return tcgdex.card.getSync(tcgdex_card_id)

def search_cards_by_name(name: str):
    return tcgdex.card.listSync(
        Query().contains("name", name)
    )

def get_cards_by_set(set_id: str):
    return tcgdex.card.listSync(
        Query().equal("set.id", set_id)
    )


def fetch_all_sets():
    return tcgdex.set.listSync()

def fetch_cards_by_set(tcgdex_set_id: str):
    return tcgdex.card.listSync(
        Query().equal("set.id", tcgdex_set_id)
    )


def get_eur_to_usd_rate():
    return 1.08

def extract_market_price_usd(card_json):
    pricing = card_json.get("pricing")
    if not pricing:
        return None

    tcgplayer = pricing.get("tcgplayer")
    if tcgplayer:
        for key in ["normal", "reverse", "holofoil"]:
            variant = tcgplayer.get(key)
            if variant and variant.get("marketPrice") is not None:
                return {
                    "price_value": float(variant["marketPrice"]),
                    "price_type": "market",
                    "source": "tcgplayer"
                }

    cardmarket = pricing.get("cardmarket")
    if cardmarket and cardmarket.get("avg") is not None:
        eur_to_usd = get_eur_to_usd_rate()
        usd_value = round(float(cardmarket["avg"]) * eur_to_usd, 2)

        return {
            "price_value": usd_value,
            "price_type": "market",
            "source": "cardmarket_converted"
        }

    return None

if __name__ == "__main__":
    card = get_card_by_id("swsh3-136")
    print(f"Found: {card.name} ({card.localId}/{card.set.cardCount.total})")
    print(f"id: {card.id} vs localID: {card.localId} vs set: {card.set.name} vs set id: {card.set.id}")
    results = search_cards_by_name("charizard")
    print(f"Found {len(results)} cards")