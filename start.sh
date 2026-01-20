#!/bin/bash
#
# Unite-I Start Script
# Starts the development server with auto-reload
#

set -e

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found."
    echo ""
    echo "Create it with:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found. Using defaults."
    echo "Copy .env.example to .env and add your API keys."
fi

# Start the service
echo "Starting Unite-I service..."
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
