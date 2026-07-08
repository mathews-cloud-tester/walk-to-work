# Walk to Work

A small full-stack app for tracking your walking commute between home and work.

Track live GPS walks, save distance and duration, set home/work locations, and see streak stats.

## Features

- **Start / finish walks** with browser geolocation
- **To work** or **to home** direction
- Live distance, duration, and path sketch
- Home & work labels / coordinates
- History, totals, and day streak
- JSON-backed persistence (no database required)

## Stack

- **Backend:** FastAPI + Pydantic
- **Frontend:** Vue 3 + Vite
- **Storage:** `data/commute_walks.json`

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

Or use the helper scripts from the repo root:

```bash
./start-backend.sh
./start-frontend.sh
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET/PUT | `/api/commute/settings` | Home/work labels & coordinates |
| GET | `/api/commute/stats` | Aggregate walk stats |
| GET/POST | `/api/commute/walks` | List / start walks |
| GET/PATCH/DELETE | `/api/commute/walks/{id}` | Read / update / delete |
| POST | `/api/commute/walks/{id}/points` | Append GPS points |

## Tests

```bash
cd backend
source .venv/bin/activate
pytest -v
```

## Notes

- Geolocation requires HTTPS or `localhost` and user permission.
- Keep the tab open while tracking; points flush to the API every few seconds.
- Walk data is stored locally in `data/commute_walks.json` (gitignored).
