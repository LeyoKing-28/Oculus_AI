from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.models import Event
from backend.schemas.event import EventCreate


def create_event(db: Session, event_data: EventCreate) -> Event:
    """Create a new urban event record in the database."""
    db_event = Event(
        event_type=event_data.event_type,
        bus_id=event_data.bus_id,
        camera_id=event_data.camera_id,
        confidence=event_data.confidence,
        severity=event_data.severity,
        latitude=event_data.latitude,
        longitude=event_data.longitude,
        timestamp=event_data.timestamp,
        object_class=event_data.object_class,
        bbox=event_data.bbox,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_all_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
    """Retrieve stored events with optional pagination."""
    return db.query(Event).order_by(Event.id.asc()).offset(skip).limit(limit).all()


def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
    """Retrieve a single event by its database ID."""
    return db.query(Event).filter(Event.id == event_id).first()
