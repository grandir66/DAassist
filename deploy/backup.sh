#!/bin/bash

# =============================================================================
# DAAssist - Script di Backup Database
# =============================================================================
# Questo script crea un backup del database PostgreSQL
#
# Uso:
#   ./deploy/backup.sh [nome_backup_opzionale]
# =============================================================================

set -e

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Directory backup
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

# Nome backup
if [ -n "$1" ]; then
    BACKUP_NAME="$1"
else
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
fi

BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.sql"

echo -e "${GREEN}=========================================="
echo "   DAAssist - Backup Database"
echo "==========================================${NC}"
echo ""

# Verifica che docker-compose sia running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}[ERROR]${NC} I servizi Docker non sono in esecuzione"
    echo "Avvia i servizi con: docker-compose up -d"
    exit 1
fi

echo -e "${YELLOW}[INFO]${NC} Creazione backup..."
echo -e "${YELLOW}[INFO]${NC} File: $BACKUP_FILE"

# Esegui backup
docker-compose exec -T db pg_dump -U daassist_user -d daassist_db > "$BACKUP_FILE"

# Comprimi backup
echo -e "${YELLOW}[INFO]${NC} Compressione backup..."
gzip -f "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

# Dimensione backup
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo ""
echo -e "${GREEN}[SUCCESS]${NC} Backup completato!"
echo -e "${GREEN}[SUCCESS]${NC} File: $BACKUP_FILE"
echo -e "${GREEN}[SUCCESS]${NC} Dimensione: $BACKUP_SIZE"
echo ""

# Lista ultimi 5 backup
echo -e "${YELLOW}[INFO]${NC} Ultimi backup disponibili:"
ls -lht "$BACKUP_DIR"/*.sql.gz 2>/dev/null | head -5 || echo "Nessun backup precedente"

echo ""
echo -e "${YELLOW}[INFO]${NC} Per ripristinare questo backup usa:"
echo -e "  ${GREEN}./deploy/restore.sh $BACKUP_FILE${NC}"
