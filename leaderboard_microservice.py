"""
Leaderboard Microservice

Features:
- GET  /healthz                       → liveness/quick check
- POST /ping                          → echo endpoint for connectivity checks
- GET  /leaderboard/biggest-win       → returns biggest single win amount (optional `gameId` scope)
- POST /leaderboard/record            → record a new win IF it exceeds current record (ties keep original)
- Swagger UI at /docs (FastAPI default)

Run:
  python -m venv .venv
  . .\.venv\Scripts\Activate.ps1
  python -m pip install --upgrade pip
  pip install fastapi uvicorn pydantic
  uvicorn leaderboard_microservice:app --host 127.0.0.1 --port 8090 --reload
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, conint
from typing import Optional, Dict
import asyncio
import time

app = FastAPI(title="Leaderboard Microservice", version="0.1.0")

# --- In-memory storage (fast, simple) ---
# Keyed by gameId; 'global' if none supplied.
_records: Dict[str, Dict[str, int]] = {}
_lock = asyncio.Lock()

def _key(game_id: Optional[str]) -> str:
    return game_id if (game_id and game_id.strip()) else "global"

# --- Schemas ---
class RecordRequest(BaseModel):
    amount: conint(ge=0) = Field(..., description="win amount; must be >= 0")
    gameId: Optional[str] = Field(None, description="optional game scope; defaults to 'global'")

class RecordResponse(BaseModel):
    updated: bool
    amount: int
    gameId: str
    updated_at: int

class BiggestWinResponse(BaseModel):
    amount: int
    gameId: str
    updated_at: int

# --- Utility ---
def _now_ns() -> int:
    return time.time_ns()

# --- Health & ping ---
@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "leaderboard", "version": app.version}

@app.post("/ping")
def ping(msg: Optional[dict] = None):
    return {"pong": True, "echo": msg or {}}

# --- Read biggest win ---
@app.get("/leaderboard/biggest-win", response_model=BiggestWinResponse)
def get_biggest_win(gameId: Optional[str] = Query(None, description="optional game scope; defaults to 'global'")):
    k = _key(gameId)
    rec = _records.get(k)
    if not rec:
        raise HTTPException(status_code=404, detail="no record yet for this scope")
    return {"amount": rec["amount"], "gameId": k, "updated_at": rec["updated_at"]}

# --- Record a win if it's a new record ---
@app.post("/leaderboard/record", response_model=RecordResponse)
async def record_win(body: RecordRequest):
    k = _key(body.gameId)
    now = _now_ns()
    async with _lock:
        current = _records.get(k)
        if current is None:
            _records[k] = {"amount": int(body.amount), "updated_at": now}
            return {"updated": True, "amount": int(body.amount), "gameId": k, "updated_at": now}
        # Update only if strictly greater (ties keep original)
        if int(body.amount) > int(current["amount"]):
            _records[k] = {"amount": int(body.amount), "updated_at": now}
            return {"updated": True, "amount": int(body.amount), "gameId": k, "updated_at": now}
        else:
            return {"updated": False, "amount": int(current["amount"]), "gameId": k, "updated_at": int(current["updated_at"]) }
