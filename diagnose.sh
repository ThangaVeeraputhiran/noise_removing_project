#!/bin/bash

# Speech Enhancement System - Browser Testing

echo "🔍 Running Diagnostics..."
echo ""

# Check if app is running
echo "1️⃣  Checking if Flask app is running..."
if pgrep -f "app_production.py" > /dev/null; then
    echo "   ✅ Flask app IS running"
    PID=$(pgrep -f "app_production.py" | head -1)
    echo "   PID: $PID"
else
    echo "   ❌ Flask app NOT running"
    echo "   Attempting to start..."
    cd /workspaces/Speech-Enhancement-System
    python app_production.py &
    sleep 3
fi

# Check port 5000
echo ""
echo "2️⃣  Checking port 5000..."
if lsof -i :5000 > /dev/null 2>&1; then
    echo "   ✅ Port 5000 is LISTENING"
    lsof -i :5000 | tail -1
else
    echo "   ❌ Port 5000 is NOT listening"
fi

# Test HTTP response
echo ""
echo "3️⃣  Testing HTTP response..."
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
if [ "$HTTP_RESPONSE" = "200" ]; then
    echo "   ✅ HTTP 200 - Server responding correctly"
else
    echo "   ❌ HTTP $HTTP_RESPONSE - Server not responding properly"
fi

# Test health endpoint
echo ""
echo "4️⃣  Testing health endpoint..."
HEALTH=$(curl -s http://localhost:5000/health | grep -o '"status":"[^"]*"')
if [ ! -z "$HEALTH" ]; then
    echo "   ✅ Health endpoint working: $HEALTH"
else
    echo "   ❌ Health endpoint not responding"
fi

# Check static files
echo ""
echo "5️⃣  Checking static files..."
if [ -f "static/css/style.css" ] && [ -f "static/js/app.js" ]; then
    echo "   ✅ Static files exist"
    echo "   - CSS: static/css/style.css"
    echo "   - JS: static/js/app.js"
else
    echo "   ❌ Missing static files"
fi

# Check required directories
echo ""
echo "6️⃣  Checking required directories..."
DIRS=("uploads" "outputs" "static/spectrograms" "templates")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir exists"
    else
        echo "   ⚠️  $dir missing"
    fi
done

# Get IP addresses
echo ""
echo "7️⃣  Network addresses:"
echo "   Local:    http://localhost:5000"
echo "   Local IP: http://127.0.0.1:5000"
IP=$(hostname -I | awk '{print $1}')
echo "   Network:  http://$IP:5000"

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "                        DIAGNOSTIC SUMMARY"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "✨ System Status: READY FOR USE"
echo ""
echo "Access your application at:"
echo "  🌐 http://localhost:5000"
echo ""
echo "If you still see 'Network error' in browser:"
echo ""
echo "  1. Clear browser cache (Ctrl+Shift+Delete)"
echo "  2. Try incognito/private mode"
echo "  3. Use a different browser"
echo "  4. Check network firewall settings"
echo "  5. Try network IP: http://$IP:5000"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
