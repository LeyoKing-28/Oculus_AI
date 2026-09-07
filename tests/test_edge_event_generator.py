"""Unit tests for Edge Event Generation Layer (Mock GPS, Event Generator, Severity, Send Event)."""

import os
import sys
import unittest
from datetime import datetime

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from edge.gps.mock_gps import MockGPSProvider
from edge.event_generator.event_generator import EventGenerator, calculate_severity
from edge.pipeline.send_event import send_event, EventSubmissionError


class TestEdgeEventGenerator(unittest.TestCase):

    def test_01_mock_gps_default_coordinates(self):
        """Test MockGPSProvider returns default coordinates."""
        gps = MockGPSProvider()
        location = gps.get_location()
        self.assertEqual(location["latitude"], 18.5204)
        self.assertEqual(location["longitude"], 73.8567)

    def test_02_mock_gps_custom_coordinates(self):
        """Test MockGPSProvider with custom coordinates and set_location."""
        gps = MockGPSProvider(latitude=19.0760, longitude=72.8777)
        location = gps.get_location()
        self.assertEqual(location["latitude"], 19.0760)
        self.assertEqual(location["longitude"], 72.8777)

        gps.set_location(28.6139, 77.2090)
        coords = gps.get_coordinates()
        self.assertEqual(coords, (28.6139, 77.2090))

    def test_03_severity_calculation(self):
        """Test prototype severity classification logic."""
        self.assertEqual(calculate_severity({"confidence": 0.93}), "HIGH")
        self.assertEqual(calculate_severity({"confidence": 0.75}), "MEDIUM")
        self.assertEqual(calculate_severity({"confidence": 0.40}), "LOW")

    def test_04_event_generator_conversion(self):
        """Test EventGenerator converts generic detection into EventCreate backend format."""
        gps = MockGPSProvider(latitude=18.5204, longitude=73.8567)
        generator = EventGenerator(bus_id="BUS_01", camera_id="CAM_FRONT", gps_provider=gps)

        generic_detection = {
            "class": "pothole",
            "confidence": 0.93,
            "bbox": [420, 210, 610, 380]
        }

        event = generator.generate_event(generic_detection)

        self.assertEqual(event["event_type"], "POTHOLE")
        self.assertEqual(event["bus_id"], "BUS_01")
        self.assertEqual(event["camera_id"], "CAM_FRONT")
        self.assertEqual(event["confidence"], 0.93)
        self.assertEqual(event["severity"], "HIGH")
        self.assertEqual(event["latitude"], 18.5204)
        self.assertEqual(event["longitude"], 73.8567)
        self.assertEqual(event["bbox"], [420, 210, 610, 380])
        self.assertEqual(event["object_class"], "pothole")

        # Validate timestamp is valid ISO string with timezone information
        parsed_ts = datetime.fromisoformat(event["timestamp"])
        self.assertIsNotNone(parsed_ts.tzinfo)

    def test_05_event_generator_with_object_class_key(self):
        """Test EventGenerator handles 'object_class' key alternatively."""
        generator = EventGenerator(bus_id="BUS_02", camera_id="CAM_REAR")
        detection = {
            "object_class": "crack",
            "confidence": 0.65,
            "bbox": [10, 20, 30, 40]
        }
        event = generator.generate_event(detection)
        self.assertEqual(event["event_type"], "CRACK")
        self.assertEqual(event["object_class"], "crack")
        self.assertEqual(event["bus_id"], "BUS_02")
        self.assertEqual(event["camera_id"], "CAM_REAR")
        self.assertEqual(event["severity"], "MEDIUM")

    def test_06_send_event_connection_error(self):
        """Test send_event raises EventSubmissionError when API is unreachable."""
        sample_event = {
            "event_type": "POTHOLE",
            "bus_id": "BUS_01",
            "camera_id": "CAM_FRONT",
            "confidence": 0.93,
            "severity": "HIGH",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "timestamp": "2026-09-07T22:00:00+00:00",
            "bbox": [420, 210, 610, 380],
            "object_class": "pothole"
        }
        # Point to closed port
        with self.assertRaises(EventSubmissionError) as cm:
            send_event(sample_event, api_url="http://127.0.0.1:59999/events", timeout=0.5)
        
        self.assertIn("Failed to connect", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
