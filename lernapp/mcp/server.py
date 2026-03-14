from __future__ import annotations

import json
import sys
from pathlib import Path

from lernapp.agents.english_card_agent import generate_english_cards
from lernapp.models import Flashcard
from lernapp.storage import JsonStorage


DATA_PATH = Path(__file__).resolve().parents[2] / "lernapp" / "data_store" / "cards.json"
storage = JsonStorage(DATA_PATH)


def write(message: dict) -> None:
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle_request(request: dict) -> dict:
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})

    if method == "tools/list":
        result = {
            "tools": [
                {
                    "name": "generate_english_cards",
                    "description": "Erzeugt Englisch-Karteikarten als Lernmaterial.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "count": {"type": "integer", "minimum": 1, "maximum": 20}
                        },
                    },
                },
                {
                    "name": "get_learning_stats",
                    "description": "Liefert Lernfortschritt und Fälligkeiten.",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            ]
        }
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name == "generate_english_cards":
            cards = generate_english_cards(arguments.get("topic", "school"), int(arguments.get("count", 5)))
            existing = storage.list_cards()
            existing.extend(cards)
            storage.upsert_cards(existing)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": f"{len(cards)} Karten erstellt."}]},
            }

        if name == "get_learning_stats":
            stats = storage.stats()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(stats, ensure_ascii=False)}]},
            }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "Method not found"},
    }


def main() -> None:
    for line in sys.stdin:
        payload = line.strip()
        if not payload:
            continue
        request = json.loads(payload)
        write(handle_request(request))


if __name__ == "__main__":
    main()
