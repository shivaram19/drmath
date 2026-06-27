#!/bin/bash
# Dr. Math — Server Deploy Script
# Run this on the target server after cloning the repo.
#
# Usage:
#   chmod +x scripts/deploy.sh
#   ./scripts/deploy.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NGINX_HTTP_CONF="$PROJECT_DIR/nginx.http.conf"
NGINX_SSL_CONF="$PROJECT_DIR/nginx.ssl.conf"
NGINX_ACTIVE_CONF="$PROJECT_DIR/nginx.conf"

echo "=========================================="
echo "🚀 Dr. Math Deploy Script"
echo "=========================================="
echo ""

# ------------------------------------------------------------------
# 1. Pre-flight checks
# ------------------------------------------------------------------
echo "[1/6] Checking dependencies..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install it first:"
    echo "    curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Install it first:"
    echo "    pip install docker-compose"
    exit 1
fi

echo "✅ Docker and docker-compose found"

# ------------------------------------------------------------------
# 2. Environment file
# ------------------------------------------------------------------
echo ""
echo "[2/6] Checking .env file..."

if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env not found. Creating template..."
    cat > "$PROJECT_DIR/.env" << 'EOF'
# LLM Provider: openai, azure, or grok
LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Azure OpenAI (optional)
AZURE_OPENAI_ENDPOINT=https://test-1-voice.openai.azure.com
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-06-01

# Grok / xAI (optional)
GROK_API_KEY=...

# Obscura headless browser binary path
OBSCURA_BINARY=/usr/local/bin/obscura
EOF
    echo "❌ Please edit $PROJECT_DIR/.env with your API keys, then re-run this script."
    exit 1
fi

if grep -q "sk-\.\.\." "$PROJECT_DIR/.env"; then
    echo "❌ .env still has placeholder API keys. Please edit it with real keys."
    exit 1
fi

echo "✅ .env configured"

# ------------------------------------------------------------------
# 3. Prepare nginx (HTTP first, SSL later)
# ------------------------------------------------------------------
echo ""
echo "[3/6] Preparing nginx config (HTTP mode)..."

if [ ! -f "$NGINX_ACTIVE_CONF" ]; then
    cp "$NGINX_HTTP_CONF" "$NGINX_ACTIVE_CONF"
    echo "✅ Copied nginx.http.conf → nginx.conf"
else
    echo "ℹ️  nginx.conf already exists (keeping current)"
fi

# Create certbot webroot if missing
mkdir -p "$PROJECT_DIR/certbot-www"

# ------------------------------------------------------------------
# 4. Generate runtime artifacts
# ------------------------------------------------------------------
echo ""
echo "[4/7] Generating runtime artifacts..."

# Nursing seed bank is gitignored but required by the repository.
python3 "$PROJECT_DIR/scripts/generate_nursing_seed.py"

# ------------------------------------------------------------------
# 5. Build & start
# ------------------------------------------------------------------
echo ""
echo "[5/7] Building and starting containers..."

cd "$PROJECT_DIR"
docker-compose down 2>/dev/null || true
docker-compose up --build -d

echo "✅ Containers started"

# ------------------------------------------------------------------
# 6. Health check
# ------------------------------------------------------------------
echo ""
echo "[6/7] Health check..."

sleep 3

if curl -fsS http://localhost:8000/api/topics &> /dev/null; then
    echo "✅ FastAPI app responding on localhost:8000"
else
    echo "⚠️  FastAPI app not responding yet (may need a few more seconds)"
fi

if curl -fsS http://localhost:8000/api/nursing/status &> /dev/null; then
    echo "✅ Nursing module responding on /api/nursing/status"
else
    echo "⚠️  Nursing module not responding yet (may need a few more seconds)"
fi

if curl -fsS -o /dev/null http://localhost:80/ 2>/dev/null || curl -fsS -o /dev/null http://127.0.0.1:80/ 2>/dev/null; then
    echo "✅ nginx responding on port 80"
else
    echo "⚠️  nginx not responding yet (may need a few more seconds)"
fi

# ------------------------------------------------------------------
# 6. Next steps
# ------------------------------------------------------------------
echo ""
echo "=========================================="
echo "🎉 Deploy complete!"
echo "=========================================="
echo ""
echo "Nursing module:"
echo "  Landing:  http://localhost/nursing"
echo "  API:      http://localhost/api/nursing/status"
echo ""
echo "Next steps:"
echo "  1. Ensure DNS A-record points to this server:"
echo "     drmath.trelolabs.com → $(curl -s ifconfig.me || echo 'YOUR_SERVER_IP')"
echo ""
echo "  2. To enable HTTPS, run:"
echo "     ./scripts/init-ssl.sh"
echo ""
echo "  3. To view logs:"
echo "     docker-compose logs -f"
echo ""
echo "  4. To update after code changes:"
echo "     git pull && docker-compose up --build -d"
echo ""
