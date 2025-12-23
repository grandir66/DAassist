#!/bin/bash

# DAAssist Management Script
# Script helper per gestire il progetto

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${GREEN}===================================================${NC}"
    echo -e "${GREEN}  DAAssist - $1${NC}"
    echo -e "${GREEN}===================================================${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Commands
cmd_start() {
    print_header "Avvio Applicazione"
    print_info "Avvio dei container Docker..."
    docker-compose up -d
    print_success "Container avviati!"
    echo ""
    print_info "Servizi disponibili:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/api/docs"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
}

cmd_stop() {
    print_header "Stop Applicazione"
    docker-compose down
    print_success "Container fermati!"
}

cmd_restart() {
    print_header "Restart Applicazione"
    docker-compose restart
    print_success "Container riavviati!"
}

cmd_logs() {
    SERVICE=${1:-backend}
    print_header "Logs - $SERVICE"
    docker-compose logs -f $SERVICE
}

cmd_init() {
    print_header "Inizializzazione Database"

    # Check if containers are running
    if ! docker-compose ps | grep -q "Up"; then
        print_info "Avvio dei container..."
        docker-compose up -d
        sleep 5
    fi

    print_info "Esecuzione script di inizializzazione..."
    docker-compose exec backend python init_db.py
    print_success "Database inizializzato!"
}

cmd_shell() {
    SERVICE=${1:-backend}
    print_header "Shell - $SERVICE"
    docker-compose exec $SERVICE bash
}

cmd_psql() {
    print_header "PostgreSQL Shell"
    docker-compose exec postgres psql -U daassist -d daassist
}

cmd_backup() {
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    print_header "Backup Database"
    print_info "Creazione backup: $BACKUP_FILE"
    docker-compose exec postgres pg_dump -U daassist daassist > $BACKUP_FILE
    print_success "Backup creato: $BACKUP_FILE"
}

cmd_restore() {
    if [ -z "$1" ]; then
        print_error "Specificare il file di backup"
        echo "Uso: ./manage.sh restore <backup_file.sql>"
        exit 1
    fi

    print_header "Restore Database"
    print_info "Restore da: $1"
    docker-compose exec -T postgres psql -U daassist daassist < $1
    print_success "Restore completato!"
}

cmd_clean() {
    print_header "Pulizia Completa"
    echo -e "${YELLOW}ATTENZIONE: Questo cancellerà tutti i container, volumi e dati!${NC}"
    read -p "Sei sicuro? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy]es$ ]]; then
        docker-compose down -v
        print_success "Pulizia completata!"
    else
        print_info "Operazione annullata"
    fi
}

cmd_test() {
    print_header "Esecuzione Test"
    docker-compose exec backend pytest -v
}

cmd_help() {
    print_header "Comandi Disponibili"
    echo ""
    echo "Gestione Container:"
    echo "  start          - Avvia l'applicazione"
    echo "  stop           - Ferma l'applicazione"
    echo "  restart        - Riavvia l'applicazione"
    echo "  logs [service] - Mostra i log (default: backend)"
    echo ""
    echo "Database:"
    echo "  init           - Inizializza il database"
    echo "  psql           - Apre shell PostgreSQL"
    echo "  backup         - Crea backup database"
    echo "  restore <file> - Ripristina da backup"
    echo ""
    echo "Sviluppo:"
    echo "  shell [service] - Apre shell nel container (default: backend)"
    echo "  test            - Esegue i test"
    echo ""
    echo "Manutenzione:"
    echo "  clean          - Rimuove tutti i container e volumi"
    echo ""
    echo "Esempio:"
    echo "  ./manage.sh start"
    echo "  ./manage.sh logs backend"
    echo "  ./manage.sh backup"
    echo ""
}

# Main
case "$1" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    logs)
        cmd_logs $2
        ;;
    init)
        cmd_init
        ;;
    shell)
        cmd_shell $2
        ;;
    psql)
        cmd_psql
        ;;
    backup)
        cmd_backup
        ;;
    restore)
        cmd_restore $2
        ;;
    clean)
        cmd_clean
        ;;
    test)
        cmd_test
        ;;
    help|*)
        cmd_help
        ;;
esac
