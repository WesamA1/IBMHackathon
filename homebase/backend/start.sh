#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# WVU LCSEE Home Base — Backend Startup Script
# Usage: ./start.sh [--reload]
# ─────────────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 1. Create / activate virtualenv ──────────────────────────────────────────
if [ ! -d ".venv" ]; then
  echo ">>> Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# ── 2. Install dependencies ───────────────────────────────────────────────────
echo ">>> Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# ── 3. Copy .env if missing ───────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ">>> Created .env from .env.example — edit if needed."
fi

# ── 4. Start server ───────────────────────────────────────────────────────────
RELOAD_FLAG=""
if [[ "$1" == "--reload" ]]; then
  RELOAD_FLAG="--reload"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   WVU LCSEE Home Base API                ║"
echo "║   http://localhost:8000                  ║"
echo "║   Docs: http://localhost:8000/api/docs   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 $RELOAD_FLAG
