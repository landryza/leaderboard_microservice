# Leaderboard Microservice

## Description
The Leaderboard Microservice tracks the **biggest single win** recorded for a game. It allows other applications (main programs or microservices) to read the current record and submit a new win amount. The record is updated only when a submitted win exceeds the existing value.citeturn1search1

If a `gameId` is omitted, the service uses the default `global` leaderboard.citeturn1search1

---

# Endpoints

# 1. Health Check
GET /healthz

Used to verify that the microservice is running.citeturn1search1

Example Request:
GET /healthz

Example Response:
```
{
  "status": "ok",
  "service": "leaderboard",
  "version": "0.1.0"
}
```

---

# 2. Get Biggest Win
GET /leaderboard/biggest-win

Retrieves the biggest win stored for a given scope.
If `gameId` is omitted, the `global` scope is used.citeturn1search1

Example Request:
GET /leaderboard/biggest-win?gameId=spinning_sevens

Example Response:
```
{
  "amount": 2500,
  "gameId": "spinning_sevens",
  "updated_at": 1739222112345678900
}
```

Error Example:
```
{
  "detail": "no record yet for this scope"
}
```

---

# 3. Record a Win
POST /leaderboard/record

Submits a new win value for a scope. The record only updates if the new amount is **strictly greater** than the current record. Ties do not overwrite.citeturn1search1

Example Request:
POST /leaderboard/record

Body:
```
{
  "amount": 2500,
  "gameId": "spinning_sevens"
}
```

Example Response (updated):
```
{
  "updated": true,
  "amount": 2500,
  "gameId": "spinning_sevens",
  "updated_at": 1739222112345678900
}
```

Example Response (not updated — tie or smaller):
```
{
  "updated": false,
  "amount": 2500,
  "gameId": "spinning_sevens",
  "updated_at": 1739222112345678900
}
```

---

# Communication Contract

# Requesting Data
To request data from the Leaderboard Microservice:

1. Send an HTTP request to the appropriate endpoint.
2. For leaderboard operations, optionally include a `gameId` query parameter.
3. For recording wins, include a JSON body containing `amount` and optional `gameId`.citeturn1search1

Example (Python):
```python
import requests

response = requests.get("http://127.0.0.1:8090/leaderboard/biggest-win")
print(response.json())
```

---

# Receiving Data
The microservice responds with JSON data.

Example response format:
```
{
  "amount": 2500,
  "gameId": "global",
  "updated_at": 1739222112345678900
}
```

Example handling in Python:
```python
data = response.json()
print("Scope:", data["gameId"])
print("Record:", data["amount"])
```

---

# UML Sequence Diagram
```
Main Program        Leaderboard Microservice
     |                      |
     |---- POST /leaderboard/record --------------------->|
     |                      |---- Compare & Update ------>|
     |                      |<--- JSON {updated:true} ----|
     |<--- JSON Response ---|                             |
     |                      |
     |---- GET /leaderboard/biggest-win ----------------->|
     |                      |---- Fetch Record ---------->|
     |                      |<--- JSON {amount:X} --------|
     |<--- JSON Response ---|                             |
```

---

# How to Run the Microservice

1. Install dependencies:
```
pip install fastapi uvicorn pydantic
```

2. Start the server:
```
uvicorn leaderboard_microservice:app --reload --port 8090
```

3. Open in browser:
```
http://127.0.0.1:8090/docs
```

---

# Test Program Example
```python
import requests

BASE = "http://127.0.0.1:8090"

# Record a new win
r = requests.post(f"{BASE}/leaderboard/record", json={"amount": 1200, "gameId": "spinning_sevens"})
print("Record attempt:", r.json())

# Attempt a smaller win
r = requests.post(f"{BASE}/leaderboard/record", json={"amount": 800, "gameId": "spinning_sevens"})
print("Smaller win attempt:", r.json())

# Get current record
r = requests.get(f"{BASE}/leaderboard/biggest-win?gameId=spinning_sevens")
print("Current record:", r.json())
```

---

## Notes
- All communication is done using JSON over HTTP.
- Records only update when the new amount is strictly greater than the current stored value.citeturn1search1
- Omitted or empty `gameId` defaults to `global`.citeturn1search1
- In-memory storage resets on restart.
