# Deploy Veloce su LXC

## Comandi da eseguire sul container LXC:

```bash
# 1. Pull ultime modifiche
cd /root/daassist
git pull

# 2. Ferma tutto
docker compose down

# 3. Riavvia con nuova architettura
docker compose up -d --build

# 4. Verifica che sia tutto attivo
docker compose ps
```

## Accesso:

- **URL**: http://IP_CONTAINER (porta 80, non serve specificare)
- **Login**: admin / admin

## Architettura:

```
Browser (porta 80)
    ↓
Nginx Container
    ├─→ Frontend statico (/)
    └─→ Backend API (/api/*)
```

Tutto passa da Nginx sulla porta 80. Niente più problemi di CORS o porte multiple.

## Troubleshooting:

```bash
# Vedi log
docker compose logs nginx
docker compose logs backend

# Verifica salute backend
curl http://localhost/health

# Verifica API
curl http://localhost/api/v1/lookup/priorities
```
