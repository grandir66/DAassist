# Deploy Veloce su LXC

## Prima installazione:

```bash
cd /opt/daassist
git pull
docker compose up -d --build

# Aspetta che i container siano pronti (30-60 secondi)
sleep 30

# Inizializza il database
bash init-db.sh
```

## Aggiornamenti successivi:

```bash
cd /opt/daassist
git pull
docker compose down
docker compose up -d --build
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
