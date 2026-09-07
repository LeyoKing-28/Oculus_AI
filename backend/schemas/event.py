from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class EventBase(BaseModel):
    """Base Pydantic schema for common urban event payload."""
    event_type: str = Field(..., description="Type of urban event, e.g. POTHOLE, CONGESTION", example="POTHOLE")
    bus_id: str = Field(..., description="Unique identifier of the public transport vehicle", example="BUS_01")
    camera_id: str = Field(..., description="Identifier for the camera mounted on the vehicle", example="CAM_FRONT")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score between 0.0 and 1.0", example=0.93)
    severity: str = Field(..., description="Severity level, e.g. HIGH, MEDIUM, LOW", example="HIGH")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 Latitude coordinate", example=18.5204)
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 Longitude coordinate", example=73.8567)
    timestamp: datetime = Field(..., description="ISO 8601 timestamp of event detection", example="2026-09-02T18:30:00")
    bbox: Optional[List[Union[int, float]]] = Field(None, description="Optional bounding box coordinates [x_min, y_min, x_max, y_max]", example=[420, 210, 610, 380])
    object_class: Optional[str] = Field(None, description="Optional specific class name of detected object", example="pothole")


class EventCreate(EventBase):
    """Schema for creating a new urban event."""
    pass


class EventResponse(EventBase):
    """Schema for returning event details from API."""
    id: int = Field(..., description="Database event ID")
    created_at: datetime = Field(..., description="Server timestamp when event was stored")

    model_config = ConfigDict(from_attributes=True)
