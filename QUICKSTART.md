# Quick Start Guide 🚀

Get SleepCycle-Alarm running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.11+ and a web browser

## Option 1: Using Docker (Recommended) ⭐

The fastest way to get everything running:

```bash
# 1. Navigate to the project
cd TheRightAClock

# 2. Start all services
docker-compose up --build

# 3. Open in your browser
# Frontend: http://localhost:8080
# API Docs: http://localhost:8000/docs
```

That's it! The app is now running.

### Stop the services:
```bash
docker-compose down
```

---

## Option 2: Running Manually

### Start the Backend

```bash
# Navigate to backend
cd backend

# Install dependencies
python3 -m pip install -r requirements.txt

# Run the API server
python3 -m uvicorn app.main:app --reload --port 8000

# API will be available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Start the Frontend

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Option A: Using Python's built-in server
python3 -m http.server 8080

# Option B: Using Node.js http-server
npx http-server -p 8080

# Frontend will be available at: http://localhost:8080
```

---

## First Steps

### 1. Use the Web Interface

1. Open http://localhost:8080
2. Enter your wake time (e.g., 07:30)
3. Click "Calculate Bedtimes"
4. See your optimal bedtime options!

### 2. Try the API Docs

1. Open http://localhost:8000/docs
2. Click on "POST /api/v1/calculate"
3. Click "Try it out"
4. Enter wake time: `"07:30"`
5. Click "Execute"
6. See the JSON response!

### 3. Use the Command-Line Tool

```bash
# Install requests (if not already installed)
pip install requests

# Calculate bedtimes
python bedtime_calculator.py 07:30

# With custom parameters
python bedtime_calculator.py 06:00 --latency 20 --cycle 85
```

---

## Testing

Run the comprehensive test suite:

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Expected result**: All 37 tests should pass! ✅

---

## Example API Usage

### Using curl

```bash
# Basic calculation
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"wake_time": "07:30"}'

# Quick calculation
curl "http://localhost:8000/api/v1/calculate/quick?wake_time=08:00"
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/calculate",
    json={"wake_time": "07:30"}
)

data = response.json()
for option in data["options"]:
    print(f"Go to bed at {option['bedtime']} for {option['cycles']} cycles")
```

### Using JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/v1/calculate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({wake_time: "07:30"})
});

const data = await response.json();
console.log(data.options);
```

---

## Project Structure

```
TheRightAClock/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # API entry point
│   │   ├── calculator.py # Core algorithm
│   │   ├── models.py    # Pydantic models
│   │   └── routes/      # API endpoints
│   └── tests/           # Test suite
├── frontend/            # Web interface
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docker-compose.yml   # Docker orchestration
├── CLAUDE.md           # Development guide
├── README.md           # Full documentation
└── API_EXAMPLES.md     # API usage examples
```

---

## Troubleshooting

### Port Already in Use

If port 8000 or 8080 is already in use:

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:8080 | xargs kill -9  # Frontend

# Or change ports in docker-compose.yml
```

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Import Errors (Python)

```bash
# Make sure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Next Steps

1. ✅ Get the app running (you just did this!)
2. 📖 Read [README.md](README.md) for full documentation
3. 🔍 Explore [API_EXAMPLES.md](API_EXAMPLES.md) for integration examples
4. 🛠️ Check [CLAUDE.md](CLAUDE.md) for development guidelines
5. 🧪 Run tests with `pytest -v`
6. 🎨 Customize the frontend design
7. 📱 Build the Flutter mobile app (coming soon!)

---

## Key Features

✅ **Smart Calculation**: Calculates bedtimes based on sleep cycles
✅ **Customizable**: Adjust sleep latency and cycle length
✅ **Recommendations**: Highlights options with ≥7 hours sleep
✅ **Tested**: 37 tests with 88% coverage
✅ **API-First**: REST API with auto-generated docs
✅ **Docker Ready**: One command to run everything

---

## Getting Help

- **Documentation**: See README.md and API_EXAMPLES.md
- **API Docs**: http://localhost:8000/docs (interactive!)
- **CLAUDE.md**: Development best practices and tips
- **Issues**: Check for common problems in README.md

---

Happy sleeping! 😴💤

**Remember**: This tool provides general guidance. Consult a healthcare provider for sleep disorders or concerns.
