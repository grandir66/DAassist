#!/bin/bash

# DAAssist Database Inspector

DB_NAME="daassist"
DB_USER="daassist_user"
DB_HOST="localhost"

echo "🔍 DAAssist Database Inspector"
echo "================================"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "❌ PostgreSQL is not running!"
    echo "Start it with: brew services start postgresql@14"
    exit 1
fi

echo "📊 Database: $DB_NAME"
echo "👤 User: $DB_USER"
echo ""

# List all tables
echo "📋 TABELLE (Total count):"
PGPASSWORD=daassist_password psql -U $DB_USER -d $DB_NAME -h $DB_HOST -t -c "
SELECT
    schemaname,
    COUNT(*) as table_count
FROM pg_tables
WHERE schemaname = 'public'
GROUP BY schemaname;
" 2>/dev/null

echo ""
echo "📋 ELENCO TABELLE:"
PGPASSWORD=daassist_password psql -U $DB_USER -d $DB_NAME -h $DB_HOST -c "
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
" 2>/dev/null

echo ""
echo "📊 STATISTICHE DATI:"
echo "-------------------"

# Tecnici
TECNICI_COUNT=$(PGPASSWORD=daassist_password psql -U $DB_USER -d $DB_NAME -h $DB_HOST -t -c "SELECT COUNT(*) FROM tecnici;" 2>/dev/null | xargs)
echo "👥 Tecnici: $TECNICI_COUNT"

# Clienti
CLIENTI_COUNT=$(PGPASSWORD=daassist_password psql -U $DB_USER -d $DB_NAME -h $DB_HOST -t -c "SELECT COUNT(*) FROM cache_clienti;" 2>/dev/null | xargs)
echo "🏢 Clienti: $CLIENTI_COUNT"

# Contratti
CONTRATTI_COUNT=$(PGPASSWORD=daassist_password psql -U $DB_USER -d $DB_NAME -h $DB_HOST -t -c "SELECT COUNT(*) FROM cache_contratti;" 2>/dev/null | xargs)
echo "📄 Contratti: $CONTRATTI_COUNT"

# Ticket
TICKET_COUNT=$(PGPASSWORD=daassist_password psql -U $DB_USER -d $DB_NAME -h $DB_HOST -t -c "SELECT COUNT(*) FROM ticket;" 2>/dev/null | xargs)
echo "🎫 Ticket: $TICKET_COUNT"

# Interventi
INTERVENTI_COUNT=$(PGPASSWORD=daassist_password psql -U $DB_USER -d $DB_NAME -h $DB_HOST -t -c "SELECT COUNT(*) FROM interventi;" 2>/dev/null | xargs)
echo "🔧 Interventi: $INTERVENTI_COUNT"

echo ""
echo "💡 Per accedere alla shell psql:"
echo "   PGPASSWORD=daassist_password psql -U $DB_USER -d $DB_NAME -h $DB_HOST"
echo ""
echo "💡 Query utili:"
echo "   SELECT * FROM tecnici;"
echo "   SELECT tablename FROM pg_tables WHERE schemaname='public';"
echo "   \\dt          -- Lista tabelle"
echo "   \\d tecnici   -- Struttura tabella tecnici"
echo ""
