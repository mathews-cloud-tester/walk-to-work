# Walk to Work

Installable phone app for tracking your walking commute between home and work.

Works **offline on your device** (PWA / native). Optional FastAPI backend if you want server sync.

## What you get

- **Install on your phone** (Add to Home Screen / PWA, or Capacitor iOS/Android)
- Start / finish GPS walks (to work or home)
- Live distance, duration, and path sketch
- Home & work labels / coordinates
- History, totals, and day streak
- Walks saved in on-device storage by default

## Quick start (web / PWA)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Install on your phone

1. Deploy or open the app over **HTTPS** (or use localhost on the same device).
2. **iPhone (Safari):** Share → **Add to Home Screen**
3. **Android (Chrome):** Menu → **Install app** / **Add to Home Screen**

You’ll get a full-screen app icon with offline support.

## Native iOS / Android (Capacitor)

```bash
cd frontend
npm install
npm run build

# First time only:
npx cap add android   # requires Android Studio / SDK
npx cap add ios       # requires macOS + Xcode

npm run cap:sync
npx cap open android  # or: npx cap open ios
```

App ID: `com.walktowork.app`

Location permission prompts come from `@capacitor/geolocation`.

## Optional backend

By default the UI uses **localStorage** (no server needed).

To use the FastAPI API instead:

```bash
# terminal 1
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# terminal 2
cd frontend
VITE_USE_API=true npm run dev
```

## Project layout

```
walk-to-work/
├── frontend/          # Vue 3 + Vite + PWA + Capacitor
│   ├── public/        # manifest, icons, service worker
│   └── src/
├── backend/           # Optional FastAPI API
└── data/              # Server-side walk JSON (when using API)
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Vite dev server |
| `npm run build` | Production web build |
| `npm run cap:sync` | Build + sync into native projects |
| `npm run cap:android` | Sync and open Android Studio |
| `npm run cap:ios` | Sync and open Xcode |

## Notes

- Geolocation needs permission; keep the app open while tracking.
- Offline-first data key: `walk-to-work:v1` in localStorage.
- Backend tests: `cd backend && pytest -v`
