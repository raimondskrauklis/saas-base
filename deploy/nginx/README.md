# deploy/nginx — placeholder vhosts (replace hosts via APP_REPLACE.md)

Production-ready vhosts for **app.example.com** + **auth.app.example.com**.  
TLS: DNS-01 (no port 80) — see `docs/utils/CERTBOT_DIGITALOCEAN_DNS_RENEWAL.md`.

## Files

| File | Install path |
|------|----------------|
| `app.example.com.conf` | `/etc/nginx/sites-available/app.example.com` |
| `auth.app.example.com.conf` | `/etc/nginx/sites-available/auth.app.example.com` |
| `nginx-http.snippet` | inside `http { }` in `/etc/nginx/nginx.conf` |

Templates with `<domain>` placeholders: `internal-docs/starter-pack/deploy/nginx/*.example`.

## Deploy

```bash
# From repo on droplet
sudo cp deploy/nginx/nginx-http.snippet /etc/nginx/conf.d/app-rate-limit.conf
# Or paste limit_req_zone line into nginx.conf http {}

sudo cp deploy/nginx/app.example.com.conf /etc/nginx/sites-available/
sudo cp deploy/nginx/auth.app.example.com.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/app.example.com /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/auth.app.example.com /etc/nginx/sites-enabled/

# Remove certbot stub / port-80 blocks from sites-enabled
sudo nginx -t && sudo systemctl reload nginx
```

## Wiring

| Service | Host port | Container |
|---------|-----------|-----------|
| API | `127.0.0.1:8000` | `app-api` |
| SPA | `127.0.0.1:5173` | `app-web` |
| Keycloak | `127.0.0.1:8080` | `app-kc` |
| KC health | `127.0.0.1:9000` | `app-kc` (not public) |

Cert: `/etc/letsencrypt/live/app.example.com/{fullchain,privkey}.pem`
