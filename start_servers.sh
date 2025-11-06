#!/bin/bash
# Start all SleepCycle-Alarm servers

echo "🚀 Starting SleepCycle-Alarm..."
echo ""

# Check if already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use!"
    echo "   Run ./stop_servers.sh first"
    exit 1
fi

if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8080 is already in use!"
    echo "   Run ./stop_servers.sh first"
    exit 1
fi

# Start backend
echo "🔧 Starting backend API..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/backend.pid
cd ..
sleep 2

# Check backend started
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend running on http://localhost:8000 (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start! Check /tmp/backend.log"
    exit 1
fi

# Start frontend
echo "🌐 Starting frontend..."
cd frontend
python3 -m http.server 8080 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/frontend.pid
cd ..
sleep 1

echo "✅ Frontend running on http://localhost:8080 (PID: $FRONTEND_PID)"

echo ""
echo "🎉 SleepCycle-Alarm is running!"
echo ""
echo "📱 Access the app:"
echo "   - Web Interface: http://localhost:8080"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - API Base: http://localhost:8000"
echo ""
echo "🛑 To stop: ./stop_servers.sh"
echo "📋 Logs:"
echo "   - Backend: tail -f /tmp/backend.log"
echo "   - Frontend: tail -f /tmp/frontend.log"
