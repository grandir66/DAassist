#!/bin/bash

echo "=== DAAssist Proxy Troubleshooting Script ==="
echo ""

echo "1. Checking if containers are running..."
docker compose ps
echo ""

echo "2. Testing backend health endpoint directly..."
docker exec daassist-backend curl -s http://localhost:8000/health || echo "FAILED: Backend not responding"
echo ""

echo "3. Testing backend API endpoint directly..."
docker exec daassist-backend curl -s http://localhost:8000/api/v1/lookup/priorities || echo "FAILED: Backend API not responding"
echo ""

echo "4. Testing backend connectivity from frontend container..."
docker exec daassist-frontend wget -O- -T 5 http://backend:8000/health 2>&1 || echo "FAILED: Cannot reach backend from frontend"
echo ""

echo "5. Testing backend API from frontend container..."
docker exec daassist-frontend wget -O- -T 5 http://backend:8000/api/v1/lookup/priorities 2>&1 || echo "FAILED: Cannot reach backend API from frontend"
echo ""

echo "6. Checking Vite proxy configuration..."
docker exec daassist-frontend cat /app/vite.config.ts | grep -A 10 "proxy:"
echo ""

echo "7. Checking frontend container network..."
docker exec daassist-frontend cat /etc/hosts | grep backend
docker exec daassist-frontend nslookup backend 2>&1 || echo "Note: nslookup might not be available"
echo ""

echo "8. Checking recent backend logs..."
docker compose logs backend --tail=20
echo ""

echo "9. Checking recent frontend logs..."
docker compose logs frontend --tail=20
echo ""

echo "=== Test Complete ==="
echo ""
echo "Next steps:"
echo "1. Pull latest changes: git pull"
echo "2. Restart services: docker compose down && docker compose up -d --build"
echo "3. Wait 30 seconds for services to start"
echo "4. Try login again from browser with hard refresh (CTRL+SHIFT+R)"
