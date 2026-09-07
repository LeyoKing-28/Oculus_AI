from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.event import EventCreate, EventResponse
from backend.services import event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new urban event",
    description="Accepts a standardized urban event payload from edge devices and stores it in the database."
)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create and persist a new urban event."""
    return event_service.create_event(db=db, event_data=event)


@router.get(
    "",
    response_model=List[EventResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all urban events",
    description="Fetches all stored urban events from the database."
)
def get_all_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all stored urban events."""
    return event_service.get_all_events(db=db, skip=skip, limit=limit)


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a specific urban event by ID",
    description="Fetches a single urban event by its unique database ID."
)
def get_event_by_id(event_id: int, db: Session = Depends(get_db)):
    """Retrieve a single event by ID or return HTTP 404 if not found."""
    event = event_service.get_event_by_id(db=db, event_id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    return event
