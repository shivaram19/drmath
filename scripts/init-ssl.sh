#!/bin/bash
# Dr. Math — SSL Initialization Script
# Obtains Let's Encrypt certificate and switches nginx to HTTPS.
# Run this AFTER DNS is configured and the site is reachable on HTTP.
#
# Usage:
#   chmod +x scripts/init-ssl.sh
#   ./scripts/init-ssl.sh

set -e

# The system certbot package conflicts with newer user-site urllib3.
# Force certbot to use only system packages.
export PYTHONNOUSERSITE=1

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DOMAIN="drmath.trelolabs.com"
NGINX_HTTP_CONF="$PROJECT_DIR/nginx.http.conf"
NGINX_SSL_CONF="$PROJECT_DIR/nginx.ssl.conf"
NGINX_ACTIVE_CONF="$PROJECT_DIR/nginx.conf"
CERTBOT_WEBROOT="/var/www/certbot"
NGINX_SITE_CONF="/etc/nginx/sites-enabled/$DOMAIN"

# Run commands as root only when we are not already root.
run_as_root() {
    if [ "$EUID" -eq 0 ]; then
        "$@"
    else
        sudo -E "$@"
    fi
}

echo "=========================================="
echo "🔒 Dr. Math SSL Initialization"
echo "=========================================="
echo ""

# ------------------------------------------------------------------
# 1. Check DNS
# ------------------------------------------------------------------
echo "[1/5] Checking DNS resolution for $DOMAIN..."

SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
RESOLVED_IP=$(dig +short "$DOMAIN" 2>/dev/null || nslookup "$DOMAIN" 2>/dev/null | grep -oP 'Address: \K[\d.]+' | tail -1 || echo "")

if [ -z "$RESOLVED_IP" ]; then
    echo "⚠️  Could not resolve $DOMAIN via DNS."
    echo "   Make sure the Namecheap A-record is set:"
    echo "   $DOMAIN → $SERVER_IP"
    echo ""
    read -rp "Continue anyway? (y/n) " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
elif [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
    echo "⚠️  DNS resolves $DOMAIN to $RESOLVED_IP, but this server is $SERVER_IP."
    echo "   Update the Namecheap A-record before proceeding."
    exit 1
else
    echo "✅ DNS resolves correctly to $SERVER_IP"
fi

# ------------------------------------------------------------------
# 2. Check certbot
# ------------------------------------------------------------------
echo ""
echo "[2/5] Checking certbot..."

if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    if command -v apt-get &> /dev/null; then
        run_as_root apt-get update && run_as_root apt-get install -y certbot
    elif command -v yum &> /dev/null; then
        run_as_root yum install -y certbot
    else
        echo "❌ Could not install certbot automatically."
        echo "   Install it manually: https://certbot.eff.org/"
        exit 1
    fi
fi

echo "✅ certbot available"

# ------------------------------------------------------------------
# 3. Obtain certificate
# ------------------------------------------------------------------
echo ""
echo "[3/5] Obtaining SSL certificate for $DOMAIN..."

mkdir -p "$CERTBOT_WEBROOT"

run_as_root certbot certonly \
    --cert-name "$DOMAIN" \
    --key-type ecdsa \
    --webroot \
    -w "$CERTBOT_WEBROOT" \
    -d "$DOMAIN" \
    --agree-tos \
    --non-interactive \
    --email "admin@$DOMAIN" 2>/dev/null || \
run_as_root certbot certonly \
    --cert-name "$DOMAIN" \
    --key-type ecdsa \
    --standalone \
    -d "$DOMAIN" \
    --agree-tos \
    --non-interactive \
    --email "admin@$DOMAIN"

if ! run_as_root test -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
    echo "❌ Certificate not found at /etc/letsencrypt/live/$DOMAIN/"
    exit 1
fi

echo "✅ Certificate obtained"

# ------------------------------------------------------------------
# 4. Switch nginx to SSL
# ------------------------------------------------------------------
echo ""
echo "[4/5] Switching nginx to HTTPS..."

cp "$NGINX_SSL_CONF" "$NGINX_ACTIVE_CONF"
run_as_root cp "$NGINX_ACTIVE_CONF" "$NGINX_SITE_CONF"
run_as_root nginx -t && run_as_root nginx -s reload

echo "✅ nginx restarted with SSL config"

# ------------------------------------------------------------------
# 5. Set up auto-renewal
# ------------------------------------------------------------------
echo ""
echo "[5/5] Setting up auto-renewal..."

# Add cron job for renewal
CRON_JOB="0 3 * * * PYTHONNOUSERSITE=1 sudo -E certbot renew --webroot -w $CERTBOT_WEBROOT --quiet --deploy-hook 'sudo nginx -s reload'"

if crontab -l 2>/dev/null | grep -q "certbot renew.*drmath"; then
    echo "ℹ️  Renewal cron job already exists"
else
    (crontab -l 2>/dev/null || true; echo "$CRON_JOB") | crontab -
    echo "✅ Auto-renewal cron job added (runs daily at 3 AM)"
fi

# ------------------------------------------------------------------
echo ""
echo "=========================================="
echo "🔒 SSL Enabled!"
echo "=========================================="
echo ""
echo "Your site should now be reachable at:"
echo "  https://$DOMAIN"
echo ""
echo "HTTP requests will automatically redirect to HTTPS."
echo ""
echo "To test renewal (dry run):"
echo "  certbot renew --dry-run"
echo ""
