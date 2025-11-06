# API Usage Examples

This document provides practical examples for using the SleepCycle-Alarm API.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

These pages allow you to test the API directly in your browser!

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint**: `GET /health`

**Example with curl**:
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

### 2. Calculate Bedtimes (Full Options)

Calculate optimal bedtimes with custom parameters.

**Endpoint**: `POST /api/v1/calculate`

**Example with curl**:
```bash
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "wake_time": "07:30",
    "sleep_latency_min": 15,
    "cycle_length_min": 90,
    "min_cycles": 4,
    "max_cycles": 6
  }'
```

**Example with Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/calculate",
    json={
        "wake_time": "07:30",
        "sleep_latency_min": 15,
        "cycle_length_min": 90,
        "min_cycles": 4,
        "max_cycles": 6
    }
)

data = response.json()
for option in data["options"]:
    print(f"{option['cycles']} cycles: go to bed at {option['bedtime']}")
    print(f"  Total sleep: {option['total_sleep_hours']:.1f} hours")
    print(f"  Recommended: {option['recommended']}")
    print()
```

**Example with JavaScript**:
```javascript
const response = await fetch('http://localhost:8000/api/v1/calculate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    wake_time: "07:30",
    sleep_latency_min: 15,
    cycle_length_min: 90,
    min_cycles: 4,
    max_cycles: 6
  })
});

const data = await response.json();
console.log('Bedtime options:', data.options);
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
    },
    {
      "cycles": 4,
      "bedtime": "01:45",
      "total_sleep_hours": 6.25,
      "total_sleep_minutes": 375,
      "recommended": false,
      "note": "4 cycles = 6h 0m (360 min) + 15 min to fall asleep = 6h 15m total"
    }
  ],
  "parameters": {
    "sleep_latency_min": 15,
    "cycle_length_min": 90
  }
}
```

---

### 3. Quick Calculate (Defaults)

Quick calculation with default parameters - just provide wake time.

**Endpoint**: `GET /api/v1/calculate/quick`

**Parameters**:
- `wake_time` (query parameter): Wake time in HH:MM format

**Example with curl**:
```bash
curl "http://localhost:8000/api/v1/calculate/quick?wake_time=06:30"
```

**Example with Python**:
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/calculate/quick",
    params={"wake_time": "06:30"}
)
print(response.json())
```

**Example with JavaScript**:
```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/calculate/quick?wake_time=06:30'
);
const data = await response.json();
```

---

### 4. Save User Preferences

Save default calculation parameters.

**Endpoint**: `POST /api/v1/preferences`

**Example with curl**:
```bash
curl -X POST http://localhost:8000/api/v1/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "sleep_latency_min": 20,
    "cycle_length_min": 85,
    "min_cycles": 5,
    "max_cycles": 6
  }'
```

**Example with Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/preferences",
    json={
        "sleep_latency_min": 20,
        "cycle_length_min": 85,
        "min_cycles": 5,
        "max_cycles": 6
    }
)
print(response.json())
```

**Response**:
```json
{
  "message": "Preferences saved successfully",
  "preferences": {
    "sleep_latency_min": 20,
    "cycle_length_min": 85,
    "min_cycles": 5,
    "max_cycles": 6
  }
}
```

**Note**: In this MVP version, preferences are stored in memory and will be lost on server restart.

---

### 5. Get User Preferences

Retrieve saved preferences.

**Endpoint**: `GET /api/v1/preferences`

**Example with curl**:
```bash
curl http://localhost:8000/api/v1/preferences
```

**Example with Python**:
```python
import requests

response = requests.get("http://localhost:8000/api/v1/preferences")
preferences = response.json()
print(f"Sleep latency: {preferences['sleep_latency_min']} min")
print(f"Cycle length: {preferences['cycle_length_min']} min")
```

---

### 6. Reset Preferences

Reset preferences to system defaults.

**Endpoint**: `DELETE /api/v1/preferences`

**Example with curl**:
```bash
curl -X DELETE http://localhost:8000/api/v1/preferences
```

**Example with Python**:
```python
import requests

response = requests.delete("http://localhost:8000/api/v1/preferences")
print(response.json())
```

---

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `422 Unprocessable Entity`: Validation error (invalid parameters)
- `500 Internal Server Error`: Server error

**Example error response** (422):
```json
{
  "detail": "min_cycles must be less than or equal to max_cycles"
}
```

**Example with error handling (Python)**:
```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/api/v1/calculate",
        json={
            "wake_time": "25:00",  # Invalid hour
            "sleep_latency_min": 15
        }
    )
    response.raise_for_status()  # Raises exception for 4xx/5xx
    data = response.json()
except requests.exceptions.HTTPError as e:
    print(f"Error: {e}")
    print(f"Details: {response.json()['detail']}")
```

---

## Complete Example: Bedtime Calculator Script

Here's a complete Python script that uses the API:

```python
#!/usr/bin/env python3
"""
Simple command-line bedtime calculator
Usage: python bedtime_calculator.py 07:30
"""
import sys
import requests

API_URL = "http://localhost:8000/api/v1/calculate"

def calculate_bedtimes(wake_time: str):
    """Calculate bedtimes for given wake time"""
    response = requests.post(
        API_URL,
        json={"wake_time": wake_time}
    )

    if response.status_code != 200:
        print(f"Error: {response.json()['detail']}")
        return

    data = response.json()
    print(f"\n🛏️  Bedtime options for waking at {wake_time}:\n")

    for option in data["options"]:
        rec = "✓ RECOMMENDED" if option["recommended"] else ""
        print(f"  {option['bedtime']} - {option['cycles']} cycles "
              f"({option['total_sleep_hours']:.1f}h) {rec}")

    print("\n💤 Go to bed at one of these times to wake up refreshed!\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bedtime_calculator.py HH:MM")
        print("Example: python bedtime_calculator.py 07:30")
        sys.exit(1)

    calculate_bedtimes(sys.argv[1])
```

**Usage**:
```bash
python bedtime_calculator.py 07:30
```

**Output**:
```
🛏️  Bedtime options for waking at 07:30:

  22:45 - 6 cycles (8.8h)
  00:15 - 5 cycles (7.2h) ✓ RECOMMENDED
  01:45 - 4 cycles (6.2h)

💤 Go to bed at one of these times to wake up refreshed!
```

---

## Testing the API

### Using the Interactive Docs

1. Start the server: `docker-compose up` or `uvicorn app.main:app --reload`
2. Open http://localhost:8000/docs in your browser
3. Click on any endpoint
4. Click "Try it out"
5. Fill in the parameters
6. Click "Execute"
7. See the response!

### Using curl

```bash
# Basic calculation
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"wake_time": "08:00"}'

# With custom parameters
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "wake_time": "06:00",
    "sleep_latency_min": 10,
    "cycle_length_min": 85,
    "min_cycles": 5,
    "max_cycles": 7
  }'
```

### Using Postman or Insomnia

1. Create a new POST request to `http://localhost:8000/api/v1/calculate`
2. Set header: `Content-Type: application/json`
3. Body (raw JSON):
   ```json
   {
     "wake_time": "07:30",
     "sleep_latency_min": 15,
     "cycle_length_min": 90,
     "min_cycles": 4,
     "max_cycles": 6
   }
   ```
4. Send request

---

## CORS Configuration

The API is configured to accept requests from:
- http://localhost:8080 (default frontend)
- http://localhost:3000 (common dev port)

If you're running the frontend on a different port, you'll need to update the CORS settings in `backend/app/main.py`.

---

## Running the API

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up

# API: http://localhost:8000
# Frontend: http://localhost:8080
# API Docs: http://localhost:8000/docs
```

### Using Python Directly

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Next Steps

- Explore the interactive docs at http://localhost:8000/docs
- Try the frontend at http://localhost:8080
- Integrate the API into your own applications
- Check out the [README.md](README.md) for more information

Happy sleeping! 😴
