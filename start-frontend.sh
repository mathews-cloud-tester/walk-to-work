#!/bin/bash
set -e
cd "$(dirname "$0")/frontend"
echo "Starting Walk to Work (offline-first PWA) on http://localhost:5173"
echo "Tip: open on your phone via your machine's LAN IP, or build & install as a native app."
npm run dev
