"""Edge Event Generator.

Converts generic AI model detection objects into standardized backend event payloads
(matching EventCreate API schema) by enriching detections with GPS location,
timezone-aware timestamp, vehicle configuration, and severity classification.

This module is model-agnostic and does NOT import or depend on specific AI models.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from edge.gps.mock_gps import MockGPSProvider, BaseGPSProvider


def calculate_severity(detection: Dict[str, Any]) -> str:
    """
    Calculate event severity based on detection metadata.

    IMPORTANT DISCLAIMER:
    This is a temporary prototype rule for Phase 2 integration testing.
    Detection confidence is used as a simple proxy heuristic and does NOT represent
    true physical pothole severity (which requires physical dimensions, depth estimation,
    or dedicated severity ML models).

    :param detection: Generic detection object containing 'confidence' or 'bbox'
    :return: Severity string: 'HIGH', 'MEDIUM', or 'LOW'
    """
    confidence = float(detection.get("confidence", 0.0))
    
    if confidence >= 0.85:
        return "HIGH"
    elif confidence >= 0.60:
        return "MEDIUM"
    else:
        return "LOW"


class EventGenerator:
    """
    Edge-side Event Generator.
    
    Transforms generic object detection dictionary outputs into backend EventCreate schema format.
    """

    def __init__(
        self,
        bus_id: str = "BUS_01",
        camera_id: str = "CAM_FRONT",
        gps_provider: Optional[BaseGPSProvider] = None
    ):
        """
        Initialize the EventGenerator with fleet/camera metadata and GPS provider.

        :param bus_id: Identifier of the public transport vehicle
        :param camera_id: Identifier of the camera mounting position
        :param gps_provider: Implementation of BaseGPSProvider (defaults to MockGPSProvider)
        """
        self.bus_id = bus_id
        self.camera_id = camera_id
        self.gps_provider = gps_provider or MockGPSProvider()

    def generate_event(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert generic AI detection into backend EventCreate dictionary format.

        :param detection: Dictionary containing generic AI detection properties:
            - 'class' or 'object_class': Detected class name (e.g. 'pothole')
            - 'confidence': Detection confidence score [0.0 - 1.0]
            - 'bbox': Bounding box coordinates [x_min, y_min, x_max, y_max]
        :return: Standardized EventCreate payload dictionary
        """
        # Support both 'class' and 'object_class' key names for generic AI output
        object_class = str(detection.get("class") or detection.get("object_class") or "pothole")
        confidence = float(detection.get("confidence", 0.0))
        bbox = detection.get("bbox", None)

        # Map object class to event_type (e.g., 'pothole' -> 'POTHOLE')
        event_type = object_class.upper()

        # Calculate prototype severity
        severity = calculate_severity(detection)

        # Retrieve geographic location from GPS provider
        location = self.gps_provider.get_location()
        latitude = location.get("latitude", 0.0)
        longitude = location.get("longitude", 0.0)

        # Generate timezone-aware UTC timestamp in ISO 8601 format
        timestamp = datetime.now(timezone.utc).isoformat()

        # Construct standardized backend event payload
        event_payload = {
            "event_type": event_type,
            "bus_id": self.bus_id,
            "camera_id": self.camera_id,
            "confidence": confidence,
            "severity": severity,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp,
            "bbox": bbox,
            "object_class": object_class
        }

        return event_payload
