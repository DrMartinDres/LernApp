from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from lernapp.agents.english_card_agent import generate_english_cards
from lernapp.models import Flashcard, LearningEvent
from lernapp.storage import JsonStorage


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "lernapp" / "data_store" / "cards.json"
WEB_DIR = ROOT / "lernapp" / "web"
storage = JsonStorage(DATA_PATH)


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/api/cards":
            subject = parse_qs(parsed.query).get("subject", [None])[0]
            cards = [c.to_dict() for c in storage.list_cards(subject)]
            return json_response(self, 200, {"cards": cards})

        if parsed.path == "/api/stats":
            return json_response(self, 200, storage.stats())

        if parsed.path == "/" or parsed.path == "/index.html":
            return self._serve_file(WEB_DIR / "index.html", "text/html; charset=utf-8")

        if parsed.path.startswith("/static/"):
            file_name = parsed.path.replace("/static/", "", 1)
            full_path = WEB_DIR / file_name
            mime = "text/javascript; charset=utf-8" if file_name.endswith(".js") else "text/css; charset=utf-8"
            return self._serve_file(full_path, mime)

        self.send_error(404, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

        if parsed.path == "/api/cards":
            card = Flashcard(
                subject=payload.get("subject", "Deutsch"),
                front=payload["front"],
                back=payload["back"],
                tags=payload.get("tags", []),
            )
            storage.save_card(card)
            return json_response(self, 201, {"card": card.to_dict()})

        if parsed.path == "/api/review":
            card_id = payload["card_id"]
            quality = int(payload.get("quality", 0))
            cards = storage.list_cards()
            for card in cards:
                if card.id == card_id:
                    card.apply_review(quality)
                    storage.upsert_cards(cards)
                    storage.add_event(LearningEvent(card_id=card_id, quality=quality))
                    return json_response(self, 200, {"card": card.to_dict()})
            return json_response(self, 404, {"error": "Card not found"})

        if parsed.path == "/api/agents/generate-english-cards":
            cards = generate_english_cards(payload.get("topic", "school"), int(payload.get("count", 5)))
            existing = storage.list_cards()
            existing.extend(cards)
            storage.upsert_cards(existing)
            return json_response(self, 201, {"created": [card.to_dict() for card in cards]})

        self.send_error(404, "Not found")

    def log_message(self, format: str, *args) -> None:
        return

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(404, "File not found")
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = HTTPServer((host, port), AppHandler)
    print(f"LernApp läuft auf http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
