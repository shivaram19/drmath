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

# Run commands as root only when we are not already root.
run_as_root() {
    if [ "$EUID" -eq 0 ]; then
        "$@"
    else
        sudo "$@"
    fi
}

echo "=========================================="
echo "🚀 Dr. Math Deploy Script"
echo "=========================================="
echo ""

# ------------------------------------------------------------------
# 1. Pre-flight checks
# ------------------------------------------------------------------
echo "[1/9] Checking dependencies..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install it first:"
    echo "    curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Prefer Docker Compose v2 plugin; fall back to legacy docker-compose binary.
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ docker compose not found. Install it first:"
    echo "    curl -fsSL https://get.docker.com | sh"
    exit 1
fi

echo "✅ Docker and '$DOCKER_COMPOSE' found"

# ------------------------------------------------------------------
# 2. Environment file
# ------------------------------------------------------------------
echo ""
echo "[2/9] Checking .env file..."

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

if grep -q "sk-\\.\\.\\." "$PROJECT_DIR/.env"; then
    echo "❌ .env still has placeholder API keys. Please edit it with real keys."
    exit 1
fi

echo "✅ .env configured"

# ------------------------------------------------------------------
# 3. Prepare nginx config (HTTP first, SSL later)
# ------------------------------------------------------------------
echo ""
echo "[3/9] Preparing nginx config..."

# Create certbot webroot if missing
mkdir -p "$PROJECT_DIR/certbot-www"

DOMAIN="drmath.trelolabs.com"
NGINX_SITE_CONF="/etc/nginx/sites-enabled/$DOMAIN"

if run_as_root test -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
    cp "$NGINX_SSL_CONF" "$NGINX_ACTIVE_CONF"
    echo "✅ SSL certificate found; copied nginx.ssl.conf → nginx.conf"
else
    cp "$NGINX_HTTP_CONF" "$NGINX_ACTIVE_CONF"
    echo "✅ No SSL certificate yet; copied nginx.http.conf → nginx.conf"
fi

# Install the active config into nginx's sites-enabled directory so it is used
# by the host-level nginx process. If nginx is containerised, this step can be
# skipped manually.
if [ -d "/etc/nginx/sites-enabled" ]; then
    run_as_root cp "$NGINX_ACTIVE_CONF" "$NGINX_SITE_CONF"
    run_as_root nginx -t && run_as_root nginx -s reload
    echo "✅ nginx site config installed and reloaded"
fi

# Install DPDPA-aligned logrotate config for dedicated nginx logs.
if [ -d "/etc/logrotate.d" ]; then
    run_as_root cp "$PROJECT_DIR/scripts/logrotate-drmath.conf" /etc/logrotate.d/drmath
    run_as_root chmod 644 /etc/logrotate.d/drmath
    echo "✅ Log retention config installed (30 days)"
fi

# ------------------------------------------------------------------
# 4. Generate runtime artifacts
# ------------------------------------------------------------------
echo ""
echo "[4/9] Generating runtime artifacts..."

# Nursing seed bank is gitignored but required by the repository.
python3 "$PROJECT_DIR/scripts/generate_nursing_seed.py"

# ------------------------------------------------------------------
# 5. Build Flutter release APK (optional)
# ------------------------------------------------------------------
echo ""
echo "[5/9] Building Flutter release APK (optional)..."

FLUTTER_DIR="$PROJECT_DIR/mathwise_build"
if [ -d "$FLUTTER_DIR" ] && command -v flutter &> /dev/null; then
    cd "$FLUTTER_DIR"
    flutter clean
    flutter build apk --release
    cp "$FLUTTER_DIR/build/app/outputs/flutter-apk/app-release.apk" "$PROJECT_DIR/web/static/mathwise.apk"
    echo "✅ Flutter release APK copied to web/static/mathwise.apk"
else
    echo "ℹ️  Flutter SDK or mathwise_build/ not found; skipping APK build"
fi

# ------------------------------------------------------------------
# 6. Deploy static PWA assets to nginx webroot
# ------------------------------------------------------------------
echo ""
echo "[6/9] Deploying static PWA assets to nginx webroot..."

NGINX_HTML="/usr/share/nginx/html"
run_as_root rm -rf "$NGINX_HTML/static/nursing" "$NGINX_HTML/nursing"
run_as_root mkdir -p "$NGINX_HTML/static"
run_as_root cp -r "$PROJECT_DIR/web/static/." "$NGINX_HTML/static/"
run_as_root cp -r "$PROJECT_DIR/web/static/nursing" "$NGINX_HTML/nursing"
run_as_root chown -R www-data:www-data "$NGINX_HTML"

if command -v nginx &> /dev/null; then
    run_as_root nginx -t && run_as_root nginx -s reload
    echo "✅ nginx config reloaded"
else
    echo "ℹ️  nginx binary not found; assuming it runs in a separate container"
fi

echo "✅ Static assets copied to $NGINX_HTML"

# ------------------------------------------------------------------
# 7. Build & start
# ------------------------------------------------------------------
echo ""
echo "[7/9] Building and starting containers..."

cd "$PROJECT_DIR"
$DOCKER_COMPOSE down 2>/dev/null || true
$DOCKER_COMPOSE up --build -d

echo "✅ Containers started"

# ------------------------------------------------------------------
# 8. Health check
# ------------------------------------------------------------------
echo ""
echo "[8/9] Health check..."

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

if curl -fsS -o /dev/null -H "Host: drmath.trelolabs.com" http://127.0.0.1:80/ 2>/dev/null; then
    echo "✅ nginx responding on port 80"
else
    echo "⚠️  nginx not responding yet (may need a few more seconds)"
fi

if curl -fsS -o /dev/null -H "Host: drmath.trelolabs.com" http://127.0.0.1/nursing/ 2>/dev/null; then
    echo "✅ Nursing PWA landing served at /nursing/"
else
    echo "⚠️  Nursing PWA landing not reachable at /nursing/ yet"
fi

# ------------------------------------------------------------------
# 9. Next steps
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
echo "Flutter APK:"
echo "  Local:    $PROJECT_DIR/web/static/mathwise.apk"
echo "  Public:   http://localhost/mathwise.apk"
echo ""
echo "Next steps:"
echo "  1. Ensure DNS A-record points to this server:"
echo "     drmath.trelolabs.com → $(curl -s ifconfig.me || echo 'YOUR_SERVER_IP')"
echo ""
echo "  2. To enable HTTPS, run:"
echo "     ./scripts/init-ssl.sh"
echo ""
echo "  3. To view logs:"
echo "     $DOCKER_COMPOSE logs -f"
echo ""
echo "  4. To update after code changes:"
echo "     git pull && ./scripts/deploy.sh"
echo ""
