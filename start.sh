#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -f ".venv/Scripts/activate" ]; then
  echo "Venv nao encontrado. Crie com: py -3.12 -m venv .venv"
  exit 1
fi

source .venv/Scripts/activate
python -m uvicorn presentation.main:app --reload --port 8000