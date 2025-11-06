#!/bin/bash
# Stop all SleepCycle-Alarm servers

echo "🛑 Stopping SleepCycle-Alarm servers..."

# Kill backend
if [ -f /tmp/backend.pid ]; then
    BACKEND_PID=$(cat /tmp/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "✅ Backend stopped (PID: $BACKEND_PID)"
    else
        echo "⚠️  Backend was not running"
    fi
    rm /tmp/backend.pid
fi

# Kill frontend
if [ -f /tmp/frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    else
        echo "⚠️  Frontend was not running"
    fi
    rm /tmp/frontend.pid
fi

# Alternative: kill by port
echo ""
echo "🔍 Checking for any remaining processes on ports 8000 and 8080..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Killed remaining process on port 8000" || true
lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "✅ Killed remaining process on port 8080" || true

echo ""
echo "✅ All servers stopped!"
