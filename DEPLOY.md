# Deploy Dr. Math to Cloud

## Server IP
```
20.193.129.119
```

## Step 1: Namecheap DNS Setup

1. Log in to Namecheap → Domain List → Manage "trelolabs.com"
2. Go to **Advanced DNS** tab
3. Add these records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | drmath | 20.193.129.119 | Automatic |

4. Save. DNS propagation takes 5–30 minutes.

## Step 2: On the Server

SSH into your server:
```bash
ssh user@20.193.129.119
```

Clone or copy the project:
```bash
cd /opt
git clone <your-repo> drmath
cd drmath
```

Set environment:
```bash
# .env is already configured with OpenAI key
cat .env
```

Start the app:
```bash
docker-compose up --build -d
```

Check it's running:
```bash
docker ps
curl http://localhost:8000/api/topics
```

## Step 3: Verify

Visit: **http://drmath.trelolabs.com**

## Step 4: HTTPS (Let's Encrypt) — Optional but Recommended

```bash
docker run -it --rm \
  -v /opt/drmath/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  -v /opt/drmath/certbot-data:/etc/letsencrypt \
  certbot/certbot certonly --standalone -d drmath.trelolabs.com
```

Then update nginx.conf to use SSL certificates.

## Files That Matter

| File | Purpose |
|------|---------|
| `.env` | API keys + config |
| `docker-compose.yml` | App + nginx stack |
| `nginx.conf` | Routes drmath.trelolabs.com |
| `data/prompts_db.json` | Research-backed prompts |
| `data/generations_db.json` | Generation history |
| `output/` | Generated topic JSONs |
