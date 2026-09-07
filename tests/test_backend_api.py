import os
import sys
import unittest
from datetime import datetime
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from backend.database.database import engine, Base

client = TestClient(app)


class TestBackendAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure database tables are created before running tests."""
        Base.metadata.create_all(bind=engine)

    def test_01_root_health_check(self):
        """Test GET / endpoint."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("message", data)

    def test_02_create_event(self):
        """Test POST /events with valid sample event payload."""
        sample_event = {
            "event_type": "POTHOLE",
            "bus_id": "BUS_01",
            "camera_id": "CAM_FRONT",
            "confidence": 0.93,
            "severity": "HIGH",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "timestamp": "2026-09-02T18:30:00",
            "bbox": [420, 210, 610, 380],
            "object_class": "pothole"
        }
        response = client.post("/events", json=sample_event)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["event_type"], "POTHOLE")
        self.assertEqual(data["bus_id"], "BUS_01")
        self.assertEqual(data["camera_id"], "CAM_FRONT")
        self.assertEqual(data["confidence"], 0.93)
        self.assertEqual(data["severity"], "HIGH")
        self.assertEqual(data["latitude"], 18.5204)
        self.assertEqual(data["longitude"], 73.8567)
        self.assertEqual(data["bbox"], [420, 210, 610, 380])
        self.assertEqual(data["object_class"], "pothole")
        self.assertIn("created_at", data)
        
        # Save created ID for next tests
        TestBackendAPI.created_event_id = data["id"]

    def test_03_get_all_events(self):
        """Test GET /events endpoint."""
        response = client.get("/events")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_04_get_event_by_id(self):
        """Test GET /events/{event_id} with existing ID."""
        event_id = getattr(TestBackendAPI, "created_event_id", 1)
        response = client.get(f"/events/{event_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], event_id)
        self.assertEqual(data["bus_id"], "BUS_01")

    def test_05_get_event_by_nonexistent_id(self):
        """Test GET /events/{event_id} with invalid/missing ID returning 404."""
        response = client.get("/events/999999")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Event with ID 999999 not found")

    def test_06_invalid_event_payload(self):
        """Test POST /events with invalid data (out-of-range confidence)."""
        invalid_event = {
            "event_type": "POTHOLE",
            "bus_id": "BUS_01",
            "camera_id": "CAM_FRONT",
            "confidence": 1.5,  # Invalid: > 1.0
            "severity": "HIGH",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "timestamp": "2026-09-02T18:30:00"
        }
        response = client.post("/events", json=invalid_event)
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity

    def test_07_swagger_docs(self):
        """Test GET /docs endpoint."""
        response = client.get("/docs")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
