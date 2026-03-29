from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Event, EventStatus, TicketType, User
from app.schemas import (
    EventCreate, EventUpdate, EventResponse, EventListResponse,
    TicketTypeCreate, TicketTypeResponse,
)

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = Event(
        title=data.title,
        description=data.description,
        venue=data.venue,
        date=data.date,
        capacity=data.capacity,
        image_url=data.image_url,
        organizer_id=current_user.id,
    )
    db.add(event)
    db.flush()

    for tt in data.ticket_types:
        ticket_type = TicketType(
            event_id=event.id,
            name=tt.name,
            price=tt.price,
            quantity=tt.quantity,
        )
        db.add(ticket_type)

    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[EventListResponse])
def list_events(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: DBSession = Depends(get_db),
):
    query = db.query(Event)
    if status_filter:
        query = query.filter(Event.status == status_filter)
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))
    events = query.order_by(Event.date.desc()).offset(skip).limit(limit).all()

    result = []
    for ev in events:
        result.append(EventListResponse(
            id=ev.id,
            title=ev.title,
            venue=ev.venue,
            date=ev.date,
            capacity=ev.capacity,
            status=ev.status.value if isinstance(ev.status, EventStatus) else ev.status,
            image_url=ev.image_url,
            attendee_count=len(ev.attendees),
        ))
    return result


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: DBSession = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    data: EventUpdate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(event)
    db.commit()


@router.post("/{event_id}/publish", response_model=EventResponse)
def publish_event(
    event_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    event.status = EventStatus.PUBLISHED
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/ticket-types", response_model=TicketTypeResponse, status_code=201)
def add_ticket_type(
    event_id: int,
    data: TicketTypeCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    tt = TicketType(event_id=event_id, name=data.name, price=data.price, quantity=data.quantity)
    db.add(tt)
    db.commit()
    db.refresh(tt)
    return tt
