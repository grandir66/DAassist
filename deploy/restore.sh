#!/bin/bash

# =============================================================================
# DAAssist - Script di Restore Database
# =============================================================================
# Questo script ripristina un backup del database PostgreSQL
#
# Uso:
#   ./deploy/restore.sh <backup_file.sql.gz>
# =============================================================================

set -e

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}[ERROR]${NC} Specifica il file di backup"
    echo ""
    echo "Uso: $0 <backup_file.sql.gz>"
    echo ""
    echo "Backup disponibili:"
    ls -lht ./backups/*.sql.gz 2>/dev/null | head -10 || echo "Nessun backup trovato"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} File non trovato: $BACKUP_FILE"
    exit 1
fi

echo -e "${YELLOW}=========================================="
echo "   DAAssist - Restore Database"
echo "==========================================${NC}"
echo ""
echo -e "${RED}ATTENZIONE: Questa operazione sovrascriverà il database corrente!${NC}"
echo ""
read -p "Sei sicuro di voler continuare? (scrivi 'yes' per confermare): " -r
echo

if [ "$REPLY" != "yes" ]; then
    echo -e "${YELLOW}[INFO]${NC} Operazione annullata"
    exit 0
fi

# Verifica che docker-compose sia running
if ! docker-compose ps db | grep -q "Up"; then
    echo -e "${YELLOW}[INFO]${NC} Avvio servizio database..."
    docker-compose up -d db
    sleep 5
fi

echo -e "${YELLOW}[INFO]${NC} Creazione backup di sicurezza prima del restore..."
SAFETY_BACKUP="./backups/pre_restore_$(date +%Y%m%d_%H%M%S).sql"
docker-compose exec -T db pg_dump -U daassist_user -d daassist_db > "$SAFETY_BACKUP"
gzip -f "$SAFETY_BACKUP"
echo -e "${GREEN}[SUCCESS]${NC} Backup di sicurezza: ${SAFETY_BACKUP}.gz"
echo ""

echo -e "${YELLOW}[INFO]${NC} Fermata servizi applicazione..."
docker-compose stop backend frontend

echo -e "${YELLOW}[INFO]${NC} Ripristino database da: $BACKUP_FILE"

# Decomprimi se necessario
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo -e "${YELLOW}[INFO]${NC} Decompressione backup..."
    gunzip -c "$BACKUP_FILE" | docker-compose exec -T db psql -U daassist_user -d daassist_db
else
    cat "$BACKUP_FILE" | docker-compose exec -T db psql -U daassist_user -d daassist_db
fi

echo ""
echo -e "${GREEN}[SUCCESS]${NC} Database ripristinato con successo!"

echo -e "${YELLOW}[INFO]${NC} Riavvio servizi..."
docker-compose up -d

echo ""
echo -e "${GREEN}=========================================="
echo "   Restore completato!"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}[INFO]${NC} Backup di sicurezza salvato in: ${SAFETY_BACKUP}.gz"
echo -e "${YELLOW}[INFO]${NC} I servizi sono stati riavviati"
echo ""
