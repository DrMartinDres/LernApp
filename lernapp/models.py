from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any
import uuid


ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def now_iso() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)


def parse_iso(value: str) -> datetime:
    return datetime.strptime(value, ISO_FORMAT)


@dataclass
class Flashcard:
    subject: str
    front: str
    back: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=now_iso)
    due_at: str = field(default_factory=now_iso)
    repetitions: int = 0
    interval_days: int = 0
    ease_factor: float = 2.5
    correct_count: int = 0
    incorrect_count: int = 0
    review_count: int = 0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Flashcard":
        return cls(**payload)

    def apply_review(self, quality: int) -> None:
        quality = max(0, min(5, quality))
        self.review_count += 1

        if quality < 3:
            self.repetitions = 0
            self.interval_days = 1
            self.incorrect_count += 1
        else:
            self.repetitions += 1
            self.correct_count += 1
            if self.repetitions == 1:
                self.interval_days = 1
            elif self.repetitions == 2:
                self.interval_days = 3
            else:
                self.interval_days = max(1, round(self.interval_days * self.ease_factor))

            self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        next_due = datetime.utcnow() + timedelta(days=self.interval_days)
        self.due_at = next_due.strftime(ISO_FORMAT)


@dataclass
class LearningEvent:
    card_id: str
    quality: int
    reviewed_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
