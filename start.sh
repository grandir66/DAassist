#!/bin/bash

# DAAssist Startup Script

echo "🚀 Starting DAAssist..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "⚠️  PostgreSQL not running. Starting PostgreSQL..."
    brew services start postgresql@14
    sleep 2
fi

# Get script directory once
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start Backend
echo "📦 Starting Backend (port 8000)..."
cd "$SCRIPT_DIR/backend"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/daassist-backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "   Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "   ✅ Backend started successfully!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ Backend failed to start. Check logs: tail -f /tmp/daassist-backend.log"
        exit 1
    fi
    sleep 1
done

# Start Frontend
echo "📱 Starting Frontend (port 3000)..."
cd "$SCRIPT_DIR/frontend"
npm run dev > /tmp/daassist-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ DAAssist started successfully!"
echo ""
echo "🌐 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/daassist-backend.log"
echo "   Frontend: tail -f /tmp/daassist-frontend.log"
echo ""
echo "🛑 To stop:"
echo "   ./stop.sh"
echo ""
echo "📋 Credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
