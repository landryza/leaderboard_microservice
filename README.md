
# Leaderboard Microservice — Biggest Single Win

A FastAPI service to **record** and **fetch** the biggest single win, optionally scoped by `gameId`. Designed to meet your user stories:

- **See Biggest Win**: `GET /leaderboard/biggest-win?gameId=...`
- **Biggest Win Recording**: `POST /leaderboard/record` (updates **only** when `amount` is strictly greater; ties keep original)

## Endpoints
- `GET /healthz` → quick liveness probe
- `POST /ping`   → echo utility
- `GET /leaderboard/biggest-win?gameId=slot1` → returns `{ amount, gameId, updated_at }` or 404 if none
- `POST /leaderboard/record` with JSON body `{ "amount": 123, "gameId": "slot1" }` → returns `{ updated, amount, gameId, updated_at }`

## Windows PowerShell Run
```
cd <folder>
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install fastapi uvicorn pydantic
uvicorn leaderboard_service_min:app --host 127.0.0.1 --port 8090 --reload
```

## Quick tests
```
# health
curl http://127.0.0.1:8090/healthz

# reading when no record yet (returns 404)
curl "http://127.0.0.1:8090/leaderboard/biggest-win?gameId=global"

# record a win (creates)
curl -X POST http://127.0.0.1:8090/leaderboard/record -H "Content-Type: application/json" -d '{"amount": 250, "gameId": "global"}'

# record a tie (no update)
curl -X POST http://127.0.0.1:8090/leaderboard/record -H "Content-Type: application/json" -d '{"amount": 250, "gameId": "global"}'

# fetch biggest win
curl "http://127.0.0.1:8090/leaderboard/biggest-win?gameId=global"
```
