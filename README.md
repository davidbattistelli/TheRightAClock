# SleepCycle-Alarm 😴⏰

**Calculate the perfect bedtime based on sleep cycles**

An intelligent sleep calculator that suggests optimal bedtimes based on your wake-up time, sleep cycles (~90 minutes), and personal sleep latency.

## Why Sleep Cycles Matter

Most adults go through 4-6 complete sleep cycles per night. Each cycle lasts approximately 90-120 minutes. Waking up at the end of a cycle (rather than in the middle) helps you feel more refreshed and alert.

**This app helps you:**
- Calculate bedtimes that align with complete sleep cycles
- Avoid waking up in the middle of deep sleep
- Get recommended 7-9 hours of sleep per night
- Customize for your personal sleep patterns

## Features

✅ **Smart Bedtime Calculation**: Enter your wake time, get multiple bedtime options
✅ **Customizable Parameters**: Adjust sleep latency and cycle length for your body
✅ **Multiple Options**: See 4, 5, and 6 cycle options with total sleep time
✅ **Clear Recommendations**: Highlights the ideal option (≥7 hours)
✅ **Educational**: Learn about sleep cycles and sleep science
✅ **REST API**: Backend API for future mobile app integration

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd TheRightAClock

# Start the application
docker-compose up --build

# Access the app
# - Frontend: http://localhost:8080
# - API docs: http://localhost:8000/docs
# - API: http://localhost:8000
```

### Manual Setup

**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
# Open index.html in browser or use a simple HTTP server:
python -m http.server 8080
```

## API Usage

### Calculate Bedtimes

**POST** `/api/v1/calculate`

```json
{
  "wake_time": "07:30",
  "sleep_latency_min": 15,
  "cycle_length_min": 90,
  "min_cycles": 4,
  "max_cycles": 6
}
```

**Response**:
```json
{
  "wake_time": "07:30",
  "options": [
    {
      "cycles": 6,
      "bedtime": "22:45",
      "total_sleep_hours": 8.75,
      "total_sleep_minutes": 525,
      "recommended": false,
      "note": "6 cycles = 9h 0m (540 min) + 15 min to fall asleep = 9h 15m total"
    },
    {
      "cycles": 5,
      "bedtime": "00:15",
      "total_sleep_hours": 7.25,
      "total_sleep_minutes": 435,
      "recommended": true,
      "note": "5 cycles = 7h 30m (450 min) + 15 min to fall asleep = 7h 45m total"
    }
  ],
  "parameters": {
    "sleep_latency_min": 15,
    "cycle_length_min": 90
  }
}
```

### Save Preferences

**POST** `/api/v1/preferences`

```json
{
  "sleep_latency_min": 20,
  "cycle_length_min": 85,
  "min_cycles": 5,
  "max_cycles": 6
}
```

## Testing

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_calculator.py -v
```

## Project Structure

```
TheRightAClock/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   └── tests/        # Test suite
├── frontend/         # Simple web interface
├── docker-compose.yml
└── README.md
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest
- **Deployment**: Docker, docker-compose

## Development

### Running Tests
```bash
cd backend
pytest -v --cov=app
```

### API Documentation
FastAPI auto-generates interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Code Quality
```bash
# Type checking
mypy app/

# Linting
ruff check app/

# Formatting
black app/
```

## Sleep Science Reference

### Typical Sleep Cycle
- **Duration**: 90-120 minutes (varies by person)
- **Cycles per night**: 4-6 for most adults
- **Total sleep recommendation**: 7-9 hours

### Sleep Stages in a Cycle
1. **N1 (Light sleep)**: 1-5 minutes
2. **N2 (Light sleep)**: 10-60 minutes
3. **N3 (Deep sleep)**: 20-40 minutes
4. **REM (Dream sleep)**: 10-60 minutes

### Important Notes
- Cycle length varies between individuals (60-110 min)
- Cycles change duration throughout the night
- This is a guideline, not medical advice
- Consistency is more important than perfection

## Roadmap

- [x] Core sleep cycle calculation algorithm
- [x] REST API with FastAPI
- [x] Simple web frontend
- [x] Docker deployment
- [ ] User authentication
- [ ] Sleep history tracking
- [ ] Flutter mobile app
- [ ] Native alarm integration
- [ ] Smart cycle length learning
- [ ] Dark mode
- [ ] Multi-language support (Italian, etc.)

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file

## Resources

- [Sleep Foundation - Sleep Cycles](https://www.sleepfoundation.org/stages-of-sleep/sleep-cycle)
- [Harvard Medical School - Sleep](https://sleep.hms.harvard.edu/)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

---

**Note**: This app provides general guidance based on sleep science research. It is not a substitute for medical advice. Consult a healthcare provider for sleep disorders or concerns.
