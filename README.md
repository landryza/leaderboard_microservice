# leaderboard_microservice

This microservice tracks **biggest single win** records for game(s). It supports a global scope and optional per-`gameId` scopes.

**Features**
- Record a win if it **exceeds** the current record (ties keep original holder)
- Retrieve the current biggest win for a scope
- Simple health and ping endpoints
- Interactive API docs at **`/docs`** (FastAPI Swagger UI)

---

## 1) Health Check
Quick liveness check.

**Method**: `GET`

**Route**: `/healthz`

**Example**
```bash
curl -s http://127.0.0.1:8090/healthz | jq
```

**Sample Response**
```json
{
  "status": "ok",
  "service": "leaderboard",
  "version": "0.1.0"
}
```

---

## 2) Ping (Echo)
Connectivity / round‑trip test; echoes any JSON you send.

**Method**: `POST`

**Route**: `/ping`

**Request Body (optional)**
```json
{ "hello": "world" }
```

**Example**
```bash
curl -s -X POST http://127.0.0.1:8090/ping \
  -H "Content-Type: application/json" \
  -d '{"hello":"world"}' | jq
```

**Sample Response**
```json
{ "pong": true, "echo": { "hello": "world" } }
```

---

## 3) Get Biggest Win (per scope)
Returns the biggest single win for the requested scope. If `gameId` is omitted or blank, the **`global`** scope is used.

**Method**: `GET`

**Route**: `/leaderboard/biggest-win`

**Query Params**
- `gameId` *(optional, string)* — scope key; defaults to `global` when omitted or empty.

**Example (global scope)**
```bash
curl -s "http://127.0.0.1:8090/leaderboard/biggest-win" | jq
```

**Example (per-game scope)**
```bash
curl -s "http://127.0.0.1:8090/leaderboard/biggest-win?gameId=spinning_sevens" | jq
```

**Successful Response**
```json
{
  "amount": 2500,
  "gameId": "spinning_sevens",
  "updated_at": 1739222112345678900
}
```

**Errors**
- `404` — no record exists yet for this scope.

---

## 4) Record a Win (only if new record)
Creates/updates the record **iff** the submitted `amount` is **strictly greater** than the current record for that scope.

**Method**: `POST`

**Route**: `/leaderboard/record`

**Request Body**
```json
{
  "amount": 2500,
  "gameId": "spinning_sevens"   // optional; defaults to global
}
```

**Example (first write creates the record)**
```bash
curl -s -X POST http://127.0.0.1:8090/leaderboard/record \
  -H "Content-Type: application/json" \
  -d '{"amount":2500, "gameId":"spinning_sevens"}' | jq
```

**Sample Response (created/updated)**
```json
{
  "updated": true,
  "amount": 2500,
  "gameId": "spinning_sevens",
  "updated_at": 1739222112345678900
}
```

**Sample Response (tie or lower — unchanged)**
```json
{
  "updated": false,
  "amount": 2500,
  "gameId": "spinning_sevens",
  "updated_at": 1739222112345678900
}
```

---

## UML Sequence Diagram:
```
sequenceDiagram
    participant Client
    participant Leaderboard as LeaderboardService

    Client->>Leaderboard: POST /leaderboard/record {amount: 1200, gameId: "spinning_sevens"}
    Leaderboard-->>Client: 200 OK {updated: true, ...}

    Client->>Leaderboard: POST /leaderboard/record {amount: 900, gameId: "spinning_sevens"}
    Leaderboard-->>Client: 200 OK {updated: false, amount: 1200, ...}

    Client->>Leaderboard: GET /leaderboard/biggest-win?gameId=spinning_sevens
    Leaderboard-->>Client: 200 OK {amount: 1200, gameId: "spinning_sevens", ...}
```