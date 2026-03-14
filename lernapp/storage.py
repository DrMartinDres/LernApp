from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lernapp.models import Flashcard, LearningEvent, now_iso, parse_iso


class JsonStorage:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"cards": [], "events": [], "created_at": now_iso()})

    def _read(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, payload: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def list_cards(self, subject: str | None = None) -> list[Flashcard]:
        data = self._read()
        cards = [Flashcard.from_dict(card) for card in data["cards"]]
        if subject:
            cards = [card for card in cards if card.subject.lower() == subject.lower()]
        return cards

    def save_card(self, card: Flashcard) -> Flashcard:
        data = self._read()
        data["cards"].append(card.to_dict())
        self._write(data)
        return card

    def upsert_cards(self, cards: list[Flashcard]) -> None:
        data = self._read()
        data["cards"] = [card.to_dict() for card in cards]
        self._write(data)

    def add_event(self, event: LearningEvent) -> None:
        data = self._read()
        data["events"].append(event.to_dict())
        self._write(data)

    def stats(self) -> dict[str, Any]:
        cards = self.list_cards()
        data = self._read()
        due_now = [c for c in cards if parse_iso(c.due_at) <= parse_iso(now_iso())]
        by_subject: dict[str, int] = {}
        for card in cards:
            by_subject[card.subject] = by_subject.get(card.subject, 0) + 1

        return {
            "cards_total": len(cards),
            "events_total": len(data["events"]),
            "due_now": len(due_now),
            "subjects": by_subject,
        }
