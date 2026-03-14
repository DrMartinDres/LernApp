from __future__ import annotations

from lernapp.models import Flashcard


ENGLISH_THEMES: dict[str, list[tuple[str, str]]] = {
    "animals": [("dog", "Hund"), ("cat", "Katze"), ("bird", "Vogel"), ("horse", "Pferd"), ("mouse", "Maus")],
    "school": [("book", "Buch"), ("pen", "Stift"), ("teacher", "Lehrer/in"), ("classroom", "Klassenraum"), ("homework", "Hausaufgabe")],
    "food": [("apple", "Apfel"), ("bread", "Brot"), ("water", "Wasser"), ("cheese", "Käse"), ("milk", "Milch")],
}


def generate_english_cards(topic: str, count: int = 5) -> list[Flashcard]:
    topic = (topic or "school").strip().lower()
    count = max(1, min(20, count))

    source = ENGLISH_THEMES.get(topic)
    if not source:
        source = ENGLISH_THEMES["school"]

    cards = []
    for english, german in source[:count]:
        cards.append(
            Flashcard(
                subject="Englisch",
                front=f"Übersetze ins Deutsche: {english}",
                back=german,
                tags=["agent", topic, "vokabel"],
            )
        )
    return cards
