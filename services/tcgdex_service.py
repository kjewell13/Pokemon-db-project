from tcgdexsdk import TCGdex, Query

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
    
def get_card_by_id(card_id):
    return tcgdex.card.getSync(card_id)

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

if __name__ == "__main__":
    card = get_card_by_id("swsh3-136")
    print(f"Found: {card.name} ({card.localId}/{card.set.cardCount.total})")
    print(f"id: {card.id} vs localID: {card.localId} vs set: {card.set.name} vs set id: {card.set.id}")
    results = search_cards_by_name("charizard")
    print(f"Found {len(results)} cards")