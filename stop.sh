#!/bin/bash

# DAAssist Stop Script

echo "🛑 Stopping DAAssist..."

# Stop Backend (port 8000)
BACKEND_PIDS=$(lsof -ti:8000)
if [ ! -z "$BACKEND_PIDS" ]; then
    echo "   Stopping Backend (PIDs: $BACKEND_PIDS)..."
    echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
    echo "   ✅ Backend stopped"
else
    echo "   ℹ️  Backend not running"
fi

# Stop Frontend (port 3000)
FRONTEND_PIDS=$(lsof -ti:3000)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo "   Stopping Frontend (PIDs: $FRONTEND_PIDS)..."
    echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
    echo "   ✅ Frontend stopped"
else
    echo "   ℹ️  Frontend not running"
fi

echo ""
echo "✅ DAAssist stopped successfully!"
echo ""
