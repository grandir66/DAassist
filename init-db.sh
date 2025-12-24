#!/bin/bash
# Script per inizializzare il database DAAssist

set -e

echo "=== Inizializzazione Database DAAssist ==="
echo ""

# Verifica che i container siano attivi
echo "1. Verifica container..."
docker compose ps | grep -q "daassist-backend.*Up" || { echo "❌ Backend non attivo"; exit 1; }
docker compose ps | grep -q "daassist-postgres.*Up" || { echo "❌ Postgres non attivo"; exit 1; }
echo "✓ Container attivi"
echo ""

# Esegui le migrazioni Alembic
echo "2. Esecuzione migrazioni Alembic..."
docker exec daassist-backend alembic upgrade head
echo "✓ Migrazioni completate"
echo ""

# Esegui script SQL di inizializzazione
echo "3. Inserimento dati iniziali..."
docker exec -i daassist-postgres psql -U daassist -d daassist < init-db.sql
echo "✓ Dati iniziali inseriti"
echo ""

echo "=== Inizializzazione Completata ==="
echo ""
echo "Credenziali di accesso:"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "IMPORTANTE: Cambia la password al primo accesso!"
