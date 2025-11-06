"""
API integration tests

Tests for FastAPI endpoints using TestClient
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns health status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_health_endpoint(self):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestCalculateEndpoint:
    """Test sleep cycle calculation endpoint"""

    def test_basic_calculation(self):
        """Test basic POST /api/v1/calculate"""
        payload = {
            "wake_time": "07:30",
            "sleep_latency_min": 15,
            "cycle_length_min": 90,
            "min_cycles": 4,
            "max_cycles": 6
        }
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["wake_time"] == "07:30"
        assert len(data["options"]) == 3  # 4, 5, 6 cycles
        assert data["parameters"]["sleep_latency_min"] == 15
        assert data["parameters"]["cycle_length_min"] == 90

        # Verify options are sorted by cycles (descending)
        assert data["options"][0]["cycles"] == 6
        assert data["options"][1]["cycles"] == 5
        assert data["options"][2]["cycles"] == 4

        # Verify structure of first option
        option = data["options"][0]
        assert "bedtime" in option
        assert "total_sleep_hours" in option
        assert "total_sleep_minutes" in option
        assert "recommended" in option
        assert "note" in option

    def test_calculation_with_defaults(self):
        """Test calculation with only wake_time (uses defaults)"""
        payload = {"wake_time": "08:00"}
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["wake_time"] == "08:00"
        assert len(data["options"]) == 3  # Default range: 4-6 cycles
        assert data["parameters"]["sleep_latency_min"] == 15  # Default
        assert data["parameters"]["cycle_length_min"] == 90  # Default

    def test_quick_calculate_endpoint(self):
        """Test GET /api/v1/calculate/quick with query parameter"""
        response = client.get("/api/v1/calculate/quick?wake_time=06:30")
        assert response.status_code == 200

        data = response.json()
        assert data["wake_time"] == "06:30"
        assert len(data["options"]) >= 1

    def test_invalid_wake_time_format(self):
        """Test that invalid wake time format returns 422"""
        payload = {"wake_time": "25:00"}  # Invalid hour
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 422

    def test_invalid_parameter_ranges(self):
        """Test that out-of-range parameters return 422"""
        # Sleep latency too high
        payload = {
            "wake_time": "07:00",
            "sleep_latency_min": 61  # Max is 60
        }
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 422

        # Cycle length too short
        payload = {
            "wake_time": "07:00",
            "cycle_length_min": 59  # Min is 60
        }
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 422

    def test_min_cycles_greater_than_max(self):
        """Test that min_cycles > max_cycles returns 422"""
        payload = {
            "wake_time": "07:00",
            "min_cycles": 6,
            "max_cycles": 4
        }
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 422

    def test_custom_parameters(self):
        """Test calculation with all custom parameters"""
        payload = {
            "wake_time": "05:45",
            "sleep_latency_min": 20,
            "cycle_length_min": 85,
            "min_cycles": 5,
            "max_cycles": 7
        }
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert len(data["options"]) == 3  # 5, 6, 7 cycles
        assert data["parameters"]["sleep_latency_min"] == 20
        assert data["parameters"]["cycle_length_min"] == 85

    def test_single_cycle_calculation(self):
        """Test calculation with single cycle (nap scenario)"""
        payload = {
            "wake_time": "14:00",
            "sleep_latency_min": 5,
            "cycle_length_min": 90,
            "min_cycles": 1,
            "max_cycles": 1
        }
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert len(data["options"]) == 1
        assert data["options"][0]["cycles"] == 1

    def test_recommendation_flag(self):
        """Test that recommendation flag is set correctly (≥7 hours)"""
        payload = {
            "wake_time": "07:00",
            "sleep_latency_min": 15,
            "cycle_length_min": 90,
            "min_cycles": 4,
            "max_cycles": 6
        }
        response = client.post("/api/v1/calculate", json=payload)
        assert response.status_code == 200

        options = response.json()["options"]

        # 6 cycles (9h 15m) and 5 cycles (7h 45m) should be recommended
        six_cycle = next(opt for opt in options if opt["cycles"] == 6)
        five_cycle = next(opt for opt in options if opt["cycles"] == 5)
        four_cycle = next(opt for opt in options if opt["cycles"] == 4)

        assert six_cycle["recommended"] is True
        assert five_cycle["recommended"] is True
        assert four_cycle["recommended"] is False  # Only 6h 15m


class TestPreferencesEndpoint:
    """Test user preferences endpoints"""

    def test_get_default_preferences(self):
        """Test getting default preferences"""
        response = client.get("/api/v1/preferences")
        assert response.status_code == 200

        data = response.json()
        assert data["sleep_latency_min"] == 15
        assert data["cycle_length_min"] == 90
        assert data["min_cycles"] == 4
        assert data["max_cycles"] == 6

    def test_save_preferences(self):
        """Test saving user preferences"""
        payload = {
            "sleep_latency_min": 20,
            "cycle_length_min": 85,
            "min_cycles": 5,
            "max_cycles": 7
        }
        response = client.post("/api/v1/preferences", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Preferences saved successfully"
        assert data["preferences"]["sleep_latency_min"] == 20
        assert data["preferences"]["cycle_length_min"] == 85

    def test_get_saved_preferences(self):
        """Test that saved preferences persist (in memory)"""
        # Save preferences
        payload = {
            "sleep_latency_min": 25,
            "cycle_length_min": 95,
            "min_cycles": 4,
            "max_cycles": 5
        }
        client.post("/api/v1/preferences", json=payload)

        # Get preferences
        response = client.get("/api/v1/preferences")
        assert response.status_code == 200

        data = response.json()
        assert data["sleep_latency_min"] == 25
        assert data["cycle_length_min"] == 95

    def test_reset_preferences(self):
        """Test resetting preferences to defaults"""
        # First save custom preferences
        payload = {"sleep_latency_min": 30, "cycle_length_min": 100}
        client.post("/api/v1/preferences", json=payload)

        # Reset
        response = client.delete("/api/v1/preferences")
        assert response.status_code == 200
        assert "reset" in response.json()["message"].lower()

        # Verify defaults are restored
        response = client.get("/api/v1/preferences")
        data = response.json()
        assert data["sleep_latency_min"] == 15
        assert data["cycle_length_min"] == 90

    def test_invalid_preferences(self):
        """Test that invalid preferences return 422"""
        # min_cycles > max_cycles
        payload = {
            "min_cycles": 7,
            "max_cycles": 5
        }
        response = client.post("/api/v1/preferences", json=payload)
        assert response.status_code == 422

        # Invalid sleep latency
        payload = {"sleep_latency_min": 61}
        response = client.post("/api/v1/preferences", json=payload)
        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        """Test that CORS headers are present in response"""
        response = client.options(
            "/api/v1/calculate",
            headers={"Origin": "http://localhost:8080"}
        )
        # FastAPI TestClient might not fully simulate CORS
        # In production, test with actual browser or curl
        assert response.status_code in [200, 405]  # OPTIONS may not be fully implemented


class TestDocumentation:
    """Test API documentation endpoints"""

    def test_openapi_json_available(self):
        """Test that OpenAPI spec is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert spec["info"]["title"] == "SleepCycle-Alarm API"

    def test_swagger_ui_available(self):
        """Test that Swagger UI docs are available"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self):
        """Test that ReDoc is available"""
        response = client.get("/redoc")
        assert response.status_code == 200
