#!/bin/bash
# Start Dr. Math locally + expose via ngrok
set -e

cd "$(dirname "$0")"

# Load env silently (do NOT export to shell — python-dotenv reads it)
# .env is read by pipeline/config.py via load_dotenv()

echo "🚀 Starting Dr. Math on port 8000..."
python3 -m uvicorn web.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!
sleep 3

echo "🌐 Starting ngrok..."
ngrok http 8000 --bind-tls true &
NGROK_PID=$!
sleep 4

echo ""
echo "========================================"
echo "  PUBLIC URL:"
curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*"' | head -1 | sed 's/.*"https:/https:/; s/"$//'
echo ""
echo "  LOCAL URL: http://localhost:8000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap "kill $UVICORN_PID $NGROK_PID 2>/dev/null; exit" INT
wait
