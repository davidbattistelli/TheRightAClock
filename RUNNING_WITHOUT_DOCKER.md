# Running SleepCycle-Alarm Without Docker 🚀

You encountered a Docker permission issue, so the app is running **manually** (which works great!).

## 🎯 Current Status

✅ **Backend API**: Running on http://localhost:8000
✅ **Frontend Web**: Running on http://localhost:8080
✅ **API Docs**: Available at http://localhost:8000/docs

## 📱 Quick Access

| What | URL |
|------|-----|
| **Main App** | http://localhost:8080 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

## 🔧 Management Commands

### Stop the Servers
```bash
cd ~/Documents/TheRightAClock
./stop_servers.sh
```

### Start the Servers
```bash
cd ~/Documents/TheRightAClock
./start_servers.sh
```

### Test the API
```bash
cd ~/Documents/TheRightAClock
./test_api.sh
```

### View Logs
```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
tail -f /tmp/frontend.log
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports 8000 and 8080
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9

# Or use the stop script
./stop_servers.sh
```

### Backend Not Starting
```bash
# Check if dependencies are installed
cd backend
pip install -r requirements.txt

# Try manual start
python3 -m uvicorn app.main:app --reload
```

### Frontend Not Loading
```bash
# Check if port 8080 is free
lsof -i:8080

# Try different port
cd frontend
python3 -m http.server 3000
# Then access: http://localhost:3000
```

## 🐳 Fixing Docker Permissions (Optional)

If you want to use Docker in the future, fix the permissions:

### Option 1: Add User to Docker Group
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# IMPORTANT: Log out and log back in for changes to take effect
# Or run: newgrp docker

# Test
docker ps
```

### Option 2: Use sudo with docker-compose
```bash
sudo docker-compose up --build
```

### Verify Docker Works
```bash
# Should work without sudo after Option 1
docker ps
docker run hello-world

# If it works, you can use:
docker-compose up --build
```

## 🎓 Understanding What's Running

### Backend (FastAPI)
- **Location**: `backend/` directory
- **Process**: Python uvicorn server
- **Port**: 8000
- **Auto-reload**: Yes (changes reflect automatically)
- **Logs**: `/tmp/backend.log`

### Frontend (Static Files)
- **Location**: `frontend/` directory
- **Process**: Python HTTP server
- **Port**: 8080
- **Auto-reload**: No (need to refresh browser)
- **Logs**: `/tmp/frontend.log`

## 🔄 Making Code Changes

### Backend Changes
1. Edit files in `backend/app/`
2. Save the file
3. Backend automatically reloads (hot reload enabled)
4. Test at http://localhost:8000/docs

### Frontend Changes
1. Edit files in `frontend/`
2. Save the file
3. **Refresh browser** (F5 or Cmd+R)
4. Changes appear immediately

### Running Tests
```bash
cd backend
pytest -v
```

## 💡 Tips

### 1. Keep Terminals Organized
```bash
# Terminal 1: Start servers
./start_servers.sh

# Terminal 2: View backend logs
tail -f /tmp/backend.log

# Terminal 3: Development work
# Edit files, run tests, etc.
```

### 2. Quick Restart
```bash
./stop_servers.sh && ./start_servers.sh
```

### 3. Test API from Command Line
```bash
# Quick test
curl http://localhost:8000/health

# Calculate bedtimes
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"wake_time": "07:30"}'

# Or use the Python CLI tool
python3 bedtime_calculator.py 07:30
```

## 📚 Next Steps

1. **Try the app**: Open http://localhost:8080
2. **Explore API docs**: Open http://localhost:8000/docs
3. **Make changes**: Edit code and see results
4. **Run tests**: `cd backend && pytest -v`
5. **(Optional) Fix Docker**: Follow instructions above

## 🎉 Advantages of Manual Mode

✅ **No Docker needed**: Simpler setup
✅ **Faster startup**: No container overhead
✅ **Easy debugging**: Direct access to processes
✅ **Hot reload**: Backend changes reflect immediately
✅ **Native performance**: No virtualization

## 📝 When to Use Docker

Use Docker for:
- Production deployment
- Consistent environments across team
- Easy deployment to cloud
- When you need database containers
- Multi-service orchestration

For now, manual mode is perfect for development! 🚀

---

**Quick Commands Summary**:
```bash
# Start
./start_servers.sh

# Stop
./stop_servers.sh

# Test
./test_api.sh

# Use
open http://localhost:8080
```

Happy coding! 😊
