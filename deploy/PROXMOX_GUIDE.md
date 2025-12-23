# Guida Deployment DAAssist su Proxmox LXC

Questa guida descrive come deployare DAAssist su un container LXC in Proxmox.

## Prerequisiti

- Server Proxmox 7.x o superiore
- Template LXC Ubuntu 22.04 o Debian 11/12
- Accesso root al server Proxmox

## Metodo 1: Installazione Automatica (Consigliato)

### Passo 1: Creazione Container LXC

Sul server Proxmox, crea un nuovo container:

```bash
# Scarica template se non presente
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst

# Crea container (ID 100, modifica se necessario)
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname daassist \
  --memory 4096 \
  --cores 2 \
  --storage local-lvm \
  --rootfs local-lvm:20 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1 \
  --unprivileged 1

# Avvia container
pct start 100
```

**Nota**: `nesting=1` è necessario per eseguire Docker dentro LXC.

### Passo 2: Installazione Automatica

Entra nel container ed esegui lo script di installazione:

```bash
# Entra nel container
pct enter 100

# Esegui script di installazione
curl -fsSL https://raw.githubusercontent.com/grandir66/DAassist/main/deploy/lxc-install.sh | bash
```

Lo script installa automaticamente:
- Docker e Docker Compose
- DAAssist completo (backend + frontend + database)
- Nginx reverse proxy (opzionale)
- Certificato SSL con Let's Encrypt (opzionale)
- Backup automatici giornalieri
- Firewall UFW configurato

### Passo 3: Configurazione (durante installazione)

Lo script chiederà:

1. **Dominio** (opzionale):
   - Lascia vuoto per usare solo IP locale
   - Inserisci dominio (es. `daassist.example.com`) per configurare SSL

2. **SSL con Let's Encrypt** (se dominio fornito):
   - Rispondere `y` per abilitare HTTPS
   - Inserire email per notifiche certificato

3. Lo script completa l'installazione automaticamente

### Passo 4: Accesso

Al termine, lo script mostrerà:

- URL di accesso (http://IP:5173 o https://dominio)
- Credenziali di default: `admin` / `admin`
- Comandi utili per gestione

**⚠️ IMPORTANTE**: Cambia le credenziali di default al primo accesso!

## Metodo 2: Installazione Manuale

### Passo 1: Preparazione Container

```bash
# Entra nel container
pct enter 100

# Aggiorna sistema
apt update && apt upgrade -y

# Installa dipendenze
apt install -y curl wget git ca-certificates gnupg lsb-release
```

### Passo 2: Installazione Docker

```bash
# Aggiungi repository Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installa Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verifica installazione
docker --version
docker compose version
```

### Passo 3: Clone Repository

```bash
cd /opt
git clone https://github.com/grandir66/DAassist.git
cd DAassist
```

### Passo 4: Configurazione

```bash
# Copia file environment
cp .env.example .env

# Modifica configurazione
nano .env

# Cambia almeno:
# - POSTGRES_PASSWORD (password database)
# - SECRET_KEY (chiave JWT)
```

Genera chiavi sicure:
```bash
# Secret key
openssl rand -hex 32

# Password database
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
```

### Passo 5: Avvio Servizi

```bash
# Avvia servizi
docker compose up -d

# Verifica stato
docker compose ps

# Visualizza log
docker compose logs -f
```

### Passo 6: Firewall (opzionale)

```bash
# Installa e configura UFW
apt install -y ufw

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5173/tcp  # Frontend (se esponi direttamente)
ufw --force enable
```

## Configurazione SSL con Nginx (opzionale)

Se hai un dominio e vuoi HTTPS:

### Installazione Nginx e Certbot

```bash
apt install -y nginx certbot python3-certbot-nginx
```

### Configurazione Nginx

```bash
cat > /etc/nginx/sites-available/daassist <<'EOF'
server {
    listen 80;
    server_name tuo-dominio.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}
EOF

# Attiva configurazione
ln -s /etc/nginx/sites-available/daassist /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Testa configurazione
nginx -t

# Riavvia nginx
systemctl restart nginx
```

### Ottieni Certificato SSL

```bash
certbot --nginx -d tuo-dominio.com --non-interactive --agree-tos -m tuo-email@example.com --redirect
```

Certbot configurerà automaticamente:
- Certificato SSL
- Redirect HTTP → HTTPS
- Rinnovo automatico

## Backup e Manutenzione

### Backup Manuale

```bash
cd /opt/DAassist
./deploy/backup.sh
```

Backup salvato in `backups/backup_YYYYMMDD_HHMMSS.sql.gz`

### Backup Automatico

Il cron job è già configurato dallo script di installazione automatica. Per configurarlo manualmente:

```bash
cat > /etc/cron.daily/daassist-backup <<'EOF'
#!/bin/bash
cd /opt/DAassist
./deploy/backup.sh
EOF

chmod +x /etc/cron.daily/daassist-backup
```

### Restore

```bash
cd /opt/DAassist
./deploy/restore.sh backups/backup_YYYYMMDD_HHMMSS.sql.gz
```

### Aggiornamento Applicazione

```bash
cd /opt/DAassist

# Pull ultimi aggiornamenti
git pull

# Rebuild e riavvio servizi
docker compose down
docker compose up -d --build

# Verifica log
docker compose logs -f
```

## Monitoraggio

### Visualizza Log

```bash
cd /opt/DAassist

# Tutti i servizi
docker compose logs -f

# Solo backend
docker compose logs -f backend

# Solo frontend
docker compose logs -f frontend

# Solo database
docker compose logs -f db
```

### Stato Servizi

```bash
docker compose ps
```

### Utilizzo Risorse

```bash
docker stats
```

## Troubleshooting

### Container non si avvia

```bash
# Verifica errori
docker compose logs

# Rebuild completo
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Errore di permessi

Se Docker da errori di permessi nel container LXC:

```bash
# Sul server Proxmox
pct set 100 -features nesting=1

# Riavvia container
pct restart 100
```

### Database non si connette

```bash
# Verifica che il database sia running
docker compose ps db

# Controlla log database
docker compose logs db

# Reset completo database (ATTENZIONE: cancella dati!)
docker compose down -v
docker compose up -d db
```

### Frontend non raggiungibile

```bash
# Verifica che il servizio sia up
docker compose ps frontend

# Controlla log
docker compose logs frontend

# Rebuild frontend
docker compose up -d --build frontend
```

## Specifiche Container Consigliate

### Configurazione Minima
- RAM: 2GB
- CPU: 1 core
- Disco: 10GB
- Adatto per: Test, sviluppo, piccole installazioni

### Configurazione Raccomandata
- RAM: 4GB
- CPU: 2 cores
- Disco: 20GB
- Adatto per: Produzione piccola/media azienda

### Configurazione Performance
- RAM: 8GB
- CPU: 4 cores
- Disco: 50GB
- Adatto per: Grandi installazioni, molti utenti concorrenti

## Note Importanti

1. **Nesting Docker in LXC**:
   - Il container deve avere `features: nesting=1`
   - Potrebbe avere limitazioni rispetto a VM completa

2. **Sicurezza**:
   - Cambia SEMPRE le password di default
   - Usa HTTPS in produzione
   - Mantieni il sistema aggiornato
   - Configura firewall correttamente

3. **Backup**:
   - Configura backup automatici
   - Testa il restore periodicamente
   - Considera backup anche dei volumi Docker

4. **Performance**:
   - PostgreSQL beneficia di storage SSD
   - Monitora utilizzo risorse
   - Scala verticalmente (più RAM/CPU) se necessario

## Supporto

Per problemi o domande:
- GitHub Issues: https://github.com/grandir66/DAassist/issues
- Documentazione: https://github.com/grandir66/DAassist

## Prossimi Passi

Dopo l'installazione:

1. ✅ Accedi all'applicazione
2. ✅ Cambia password admin
3. ✅ Configura backup (se non automatico)
4. ✅ Importa dati iniziali (clienti, tecnici, lookup)
5. ✅ Personalizza impostazioni
6. ✅ Inizia ad usare il sistema!
