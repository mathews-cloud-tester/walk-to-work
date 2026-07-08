#!/bin/bash
set -e
cd "$(dirname "$0")/backend"
echo "Starting Walk to Work API on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
