# Dr. Math — Deployment Guide

**Target:** `20.193.129.119`  
**Domain:** `drmath.trelolabs.com`  
**Method:** Git clone + Docker Compose + Let's Encrypt SSL

---

## Prerequisites

- Server with Docker and docker-compose installed
- Git access to clone the repository
- Namecheap account with `trelolabs.com` domain

---

## Step 1: DNS (You do this)

1. Log in to **Namecheap** → Domain List → Manage `trelolabs.com`
2. Go to **Advanced DNS** tab
3. Add:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | `drmath` | `20.193.129.119` | Automatic |

4. Save. Propagation takes 5–30 minutes.
5. Verify: `dig drmath.trelolabs.com +short` should return `20.193.129.119`

---

## Step 2: Clone & Deploy (On the server)

SSH into your server and run:

```bash
# 1. Clone the repo
cd /opt
git clone <your-repo-url> drmath
cd drmath

# 2. Run the deploy script
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

The script will:
- Check Docker is installed
- Verify `.env` has real API keys
- Start containers in **HTTP mode** first
- Run a health check

---

## Step 3: Configure Environment

If `.env` was missing, the script created a template. Edit it:

```bash
nano /opt/drmath/.env
```

Minimum required:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-real-key
OPENAI_MODEL=gpt-4o-mini
```

Then restart:
```bash
cd /opt/drmath && docker-compose up -d
```

---

## Step 4: Enable HTTPS (SSL)

Once DNS is resolving and the site loads on **HTTP**:

```bash
cd /opt/drmath
chmod +x scripts/init-ssl.sh
./scripts/init-ssl.sh
```

This script will:
1. Verify DNS resolves to this server
2. Install certbot if missing
3. Obtain a Let's Encrypt certificate
4. Switch nginx from HTTP to HTTPS
5. Set up auto-renewal (daily cron at 3 AM)

After this, `http://drmath.trelolabs.com` redirects to `https://` automatically.

---

## Update After Code Changes

```bash
cd /opt/drmath
git pull

# Regenerate runtime artifacts (e.g., nursing seed bank)
python3 scripts/generate_nursing_seed.py

docker-compose up --build -d
```

---

## Useful Commands

```bash
# View logs
docker-compose logs -f

# View only app logs
docker-compose logs -f drmath

# Restart just nginx
docker-compose restart nginx

# Full reset (keeps data/ and output/ volumes)
docker-compose down && docker-compose up -d

# Test SSL renewal (dry run)
certbot renew --dry-run

# Check cron job for auto-renewal
crontab -l | grep certbot
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `nginx.conf` not found | `cp nginx.http.conf nginx.conf` |
| Port 80 already in use | `sudo lsof -i :80` then kill the process |
| Certbot fails | Check DNS resolves first: `dig drmath.trelolabs.com +short` |
| 502 Bad Gateway | Check FastAPI is running: `docker-compose logs drmath` |
| `.env` keys not loading | Verify file is at `/opt/drmath/.env` and not gitignored |
