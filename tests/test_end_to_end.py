"""End-to-End Integration Test and Demo Script.

Demonstrates the complete Phase 2 Edge-to-Backend data flow:
Generic Detection -> Event Generator -> Mock GPS -> Event JSON -> POST /events -> GET /events confirmation.
"""

import os
import sys
import unittest
import json
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from backend.database.database import engine, Base
from edge.gps.mock_gps import MockGPSProvider
from edge.event_generator.event_generator import EventGenerator
from edge.pipeline.send_event import send_event, EventSubmissionError

client = TestClient(app)


def run_end_to_end_demo(api_url: str = "http://127.0.0.1:8000/events", use_test_client: bool = False):
    """
    Executes the full pipeline for generic AI detection submission.

    :param api_url: URL for POST /events endpoint
    :param use_test_client: If True, uses FastAPI TestClient instead of HTTP socket
    :return: Tuple of (generated_event, created_event_response)
    """
    print("\n==================================================")
    print("      PHASE 2: END-TO-END EDGE PIPELINE DEMO     ")
    print("==================================================")

    # 1. Generic AI Detection Input
    generic_detection = {
        "class": "pothole",
        "confidence": 0.93,
        "bbox": [420, 210, 610, 380]
    }
    print(f"\n[1] Generic Detection Input:\n{json.dumps(generic_detection, indent=2)}")

    # 2. Mock GPS Initialization
    mock_gps = MockGPSProvider(latitude=18.5204, longitude=73.8567)
    print(f"\n[2] Mock GPS Location: {mock_gps.get_location()}")

    # 3. Event Generator Layer
    event_generator = EventGenerator(
        bus_id="BUS_01",
        camera_id="CAM_FRONT",
        gps_provider=mock_gps
    )
    generated_event = event_generator.generate_event(generic_detection)
    print(f"\n[3] Generated Backend Event Payload:\n{json.dumps(generated_event, indent=2)}")

    # 4. Transmit Event via Backend Client / API
    print(f"\n[4] Submitting Event to POST /events ({api_url})...")
    if use_test_client:
        response = client.post("/events", json=generated_event)
        if response.status_code != 201:
            raise RuntimeError(f"Failed to post event via TestClient: {response.status_code} - {response.text}")
        created_event = response.json()
    else:
        created_event = send_event(generated_event, api_url=api_url)

    print(f"\n[5] POST /events Success Response:\n{json.dumps(created_event, indent=2)}")

    # 5. Verification: GET /events/{id} or GET /events
    created_id = created_event.get("id")
    print(f"\n[6] Verifying storage via GET /events/{created_id}...")
    if use_test_client:
        get_resp = client.get(f"/events/{created_id}")
        assert get_resp.status_code == 200
        fetched_event = get_resp.json()
    else:
        import urllib.request
        get_url = api_url.rstrip("/") + f"/{created_id}"
        req = urllib.request.Request(get_url)
        with urllib.request.urlopen(req) as resp:
            fetched_event = json.loads(resp.read().decode("utf-8"))

    print(f"\n[7] Retrieved Event from Backend DB:\n{json.dumps(fetched_event, indent=2)}")
    print("\n==================================================")
    print("      END-TO-END PIPELINE COMPLETED SUCCESSFULLY  ")
    print("==================================================\n")

    return generated_event, created_event


class TestEndToEndPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    def test_end_to_end_flow(self):
        """Test full pipeline using in-memory TestClient."""
        generated_event, created_event = run_end_to_end_demo(use_test_client=True)

        self.assertIn("id", created_event)
        self.assertEqual(created_event["event_type"], "POTHOLE")
        self.assertEqual(created_event["bus_id"], "BUS_01")
        self.assertEqual(created_event["camera_id"], "CAM_FRONT")
        self.assertEqual(created_event["confidence"], 0.93)
        self.assertEqual(created_event["severity"], "HIGH")
        self.assertEqual(created_event["latitude"], 18.5204)
        self.assertEqual(created_event["longitude"], 73.8567)
        self.assertEqual(created_event["bbox"], [420, 210, 610, 380])
        self.assertEqual(created_event["object_class"], "pothole")


if __name__ == "__main__":
    # If API server is running locally, attempt live POST, else run unittest using TestClient
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        api_target = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8000/events"
        run_end_to_end_demo(api_url=api_target, use_test_client=False)
    else:
        unittest.main()
