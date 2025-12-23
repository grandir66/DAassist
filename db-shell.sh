#!/bin/bash

# DAAssist Database Shell - Quick Access

DB_NAME="daassist"
DB_HOST="localhost"

echo "🔍 DAAssist Database Shell"
echo "=========================="
echo ""
echo "Connecting to PostgreSQL..."
echo ""

# Use postgres superuser for convenience
psql -h $DB_HOST -U postgres -d $DB_NAME

echo ""
echo "Session closed."
