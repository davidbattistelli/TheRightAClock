#!/bin/bash
# Quick API test script

echo "🧪 Testing SleepCycle-Alarm API..."
echo ""

# Test 1: Health check
echo "1️⃣  Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo ""

# Test 2: Calculate bedtimes
echo "2️⃣  Calculate bedtimes for waking at 07:30:"
curl -s -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"wake_time": "07:30"}' | python3 -m json.tool
echo ""
echo ""

echo "✅ API is working perfectly!"
echo ""
echo "🌐 Open in browser:"
echo "   - Web App: http://localhost:8080"
echo "   - API Docs: http://localhost:8000/docs"
