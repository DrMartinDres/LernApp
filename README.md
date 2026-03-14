# LernApp

Eine lokal startbare Lernapp für Kinder mit Karteikasten für **Deutsch, Englisch und Mathe**.

## Features
- Lokale Datenspeicherung in JSON (`lernapp/data_store/cards.json`)
- Active Recall (Antwort erst nach Klick anzeigen)
- Spaced Repetition (SM-2-ähnliche Planung pro Karte)
- Lerntracking (wie oft gelernt, richtig/falsch, nächste Fälligkeit)
- Agent-Endpoint zum Generieren von Englisch-Karteikarten
- MCP-Server (`lernapp/mcp/server.py`) mit Tools für Card-Generierung und Stats
- Skills-Definitionen (`lernapp/skills/learning_skills.json`)

## Lokal starten
```bash
python3 app.py
```
Dann öffnen: `http://localhost:8000`

## MCP Server starten
```bash
python3 -m lernapp.mcp.server
```

## API Kurzüberblick
- `POST /api/cards` Karte anlegen
- `GET /api/cards` Karten holen
- `POST /api/review` Review-Bewertung (0-5)
- `POST /api/agents/generate-english-cards` Agent erstellt Englischkarten
- `GET /api/stats` Fortschrittswerte
