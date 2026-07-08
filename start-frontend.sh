#!/bin/bash
set -e
cd "$(dirname "$0")/frontend"
echo "Starting Walk to Work frontend on http://localhost:5173"
npm run dev
