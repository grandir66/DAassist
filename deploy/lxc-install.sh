#!/bin/bash

# =============================================================================
# DAAssist - Script di Installazione per Container LXC Proxmox
# =============================================================================
# Questo script installa e configura DAAssist su un container LXC Ubuntu/Debian
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/grandir66/DAassist/main/deploy/lxc-install.sh | bash
#
# Oppure manualmente:
#   wget https://raw.githubusercontent.com/grandir66/DAassist/main/deploy/lxc-install.sh
#   chmod +x lxc-install.sh
#   ./lxc-install.sh
# =============================================================================

set -e  # Exit on error

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni helper
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Verifica che lo script sia eseguito come root
if [[ $EUID -ne 0 ]]; then
   error "Questo script deve essere eseguito come root (usa sudo)"
fi

info "=========================================="
info "   DAAssist - Installazione LXC Proxmox"
info "=========================================="
echo ""

# Variabili configurabili
INSTALL_DIR="/opt/daassist"
DOMAIN="${DOMAIN:-}"
EMAIL="${EMAIL:-}"
ENABLE_SSL="${ENABLE_SSL:-false}"

# Se eseguito con parametri, usa quelli
# Uso: DOMAIN=example.com EMAIL=admin@example.com ENABLE_SSL=true ./lxc-install.sh
if [ -z "$DOMAIN" ] && [ -t 0 ]; then
    # Solo se stdin è un terminale (esecuzione interattiva)
    read -p "Inserisci il dominio (lascia vuoto per localhost): " DOMAIN
    if [ -n "$DOMAIN" ]; then
        read -p "Vuoi abilitare SSL con Let's Encrypt? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ENABLE_SSL=true
            read -p "Inserisci email per Let's Encrypt: " EMAIL
        fi
    fi
fi

info "Aggiornamento sistema..."
apt-get update
apt-get upgrade -y

info "Installazione dipendenze base..."
apt-get install -y \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw

success "Dipendenze base installate"

# Installazione Docker
info "Installazione Docker..."
if ! command -v docker &> /dev/null; then
    # Aggiungi repository Docker
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    systemctl enable docker
    systemctl start docker

    success "Docker installato"
else
    success "Docker già installato"
fi

# Installazione Docker Compose standalone (se non già presente)
if ! command -v docker-compose &> /dev/null; then
    info "Installazione Docker Compose..."
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    success "Docker Compose installato"
fi

# Clone repository
info "Clone repository DAAssist..."
if [ -d "$INSTALL_DIR" ]; then
    warning "Directory $INSTALL_DIR già esistente, aggiornamento..."
    cd $INSTALL_DIR
    git pull
else
    git clone https://github.com/grandir66/DAassist.git $INSTALL_DIR
    cd $INSTALL_DIR
fi

success "Repository clonato"

# Configurazione environment
info "Configurazione variabili d'ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env

    # Genera secret key random
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/change_this_secret_key_to_a_random_string_in_production_use_openssl_rand_hex_32/$SECRET_KEY/" .env

    # Genera password database random
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    sed -i "s/change_this_secure_password_in_production/$DB_PASSWORD/" .env

    # Configura dominio se fornito
    if [ -n "$DOMAIN" ]; then
        echo "DOMAIN=$DOMAIN" >> .env
        sed -i "s|http://localhost:5173|https://$DOMAIN|" .env
    fi

    success "File .env configurato"
else
    warning "File .env già esistente, non modificato"
fi

# Configurazione firewall
info "Configurazione firewall UFW..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
success "Firewall configurato"

# Avvio servizi
info "Avvio servizi Docker..."
docker-compose down 2>/dev/null || true
docker-compose pull
docker-compose up -d --build

# Attendi che i servizi siano pronti
info "Attesa avvio servizi..."
sleep 10

# Verifica stato servizi
if docker-compose ps | grep -q "Up"; then
    success "Servizi avviati correttamente"
else
    error "Errore nell'avvio dei servizi"
fi

# Configurazione nginx reverse proxy (se SSL abilitato)
if [ "$ENABLE_SSL" = true ]; then
    info "Configurazione Nginx e Let's Encrypt..."

    apt-get install -y nginx certbot python3-certbot-nginx

    # Crea configurazione nginx
    cat > /etc/nginx/sites-available/daassist <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
    }
}
EOF

    ln -sf /etc/nginx/sites-available/daassist /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    nginx -t && systemctl reload nginx

    # Ottieni certificato SSL
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL --redirect

    success "SSL configurato con successo"
fi

# Setup backup automatico
info "Configurazione backup automatici..."
cat > /etc/cron.daily/daassist-backup <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/daassist/backups"
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR
cd /opt/daassist

# Backup database
docker-compose exec -T db pg_dump -U daassist_user daassist_db | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Rimuovi backup vecchi
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completato: $(date)"
EOF

chmod +x /etc/cron.daily/daassist-backup
success "Backup automatici configurati"

# Informazioni finali
echo ""
info "=========================================="
success "   Installazione completata!"
info "=========================================="
echo ""
info "Accedi all'applicazione:"
if [ -n "$DOMAIN" ] && [ "$ENABLE_SSL" = "true" ]; then
    echo -e "  ${GREEN}https://$DOMAIN${NC}"
elif [ -n "$DOMAIN" ]; then
    echo -e "  ${GREEN}http://$DOMAIN${NC}"
else
    IP_ADDR=$(hostname -I | awk '{print $1}')
    echo -e "  Frontend: ${GREEN}http://${IP_ADDR}:5173${NC}"
    echo -e "  Backend:  ${GREEN}http://${IP_ADDR}:8000${NC}"
    echo -e "  API Docs: ${GREEN}http://${IP_ADDR}:8000/docs${NC}"
fi
echo ""
info "Credenziali default:"
echo -e "  Username: ${YELLOW}admin${NC}"
echo -e "  Password: ${YELLOW}admin${NC}"
echo ""
warning "IMPORTANTE: Cambia le credenziali di default al primo accesso!"
echo ""
info "Comandi utili:"
echo "  - Visualizza log:     docker-compose logs -f"
echo "  - Riavvia servizi:    docker-compose restart"
echo "  - Ferma servizi:      docker-compose down"
echo "  - Aggiorna app:       git pull && docker-compose up -d --build"
echo "  - Backup manuale:     /etc/cron.daily/daassist-backup"
echo ""
info "File configurazione: $INSTALL_DIR/.env"
info "Backup giornalieri:  $INSTALL_DIR/backups/"
echo ""
success "Installazione completata con successo!"
