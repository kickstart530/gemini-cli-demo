import uuid
import io
import base64
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Attendee, Event, Ticket, TicketType, Payment, PaymentStatus, User
from app.schemas import (
    AttendeeResponse, CheckInRequest, TicketPurchaseRequest, TicketResponse,
)

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

router = APIRouter(prefix="/api", tags=["Attendees & Tickets"])


def generate_qr_code(data: str) -> str:
    """Generate a QR code and return as base64 encoded PNG."""
    if not HAS_QRCODE:
        return f"qr:{data}"
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


@router.post("/events/{event_id}/register", response_model=AttendeeResponse, status_code=201)
def register_for_event(
    event_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    existing = db.query(Attendee).filter(
        Attendee.user_id == current_user.id,
        Attendee.event_id == event_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this event")

    if len(event.attendees) >= event.capacity:
        raise HTTPException(status_code=400, detail="Event is at full capacity")

    attendee = Attendee(user_id=current_user.id, event_id=event_id)
    db.add(attendee)
    db.commit()
    db.refresh(attendee)

    return AttendeeResponse(
        id=attendee.id,
        user_id=attendee.user_id,
        event_id=attendee.event_id,
        registration_date=attendee.registration_date,
        check_in_status=attendee.check_in_status,
        checked_in_at=attendee.checked_in_at,
        user_name=current_user.name,
        user_email=current_user.email,
    )


@router.get("/events/{event_id}/attendees", response_model=list[AttendeeResponse])
def list_attendees(
    event_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendees = db.query(Attendee).filter(Attendee.event_id == event_id).all()
    result = []
    for a in attendees:
        result.append(AttendeeResponse(
            id=a.id,
            user_id=a.user_id,
            event_id=a.event_id,
            registration_date=a.registration_date,
            check_in_status=a.check_in_status,
            checked_in_at=a.checked_in_at,
            user_name=a.user.name,
            user_email=a.user.email,
        ))
    return result


@router.post("/attendees/{attendee_id}/check-in", response_model=AttendeeResponse)
def check_in_attendee(
    attendee_id: int,
    data: CheckInRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendee = db.query(Attendee).filter(Attendee.id == attendee_id).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    if attendee.check_in_status:
        raise HTTPException(status_code=400, detail="Already checked in")

    # Verify QR code matches a ticket for this attendee
    ticket = db.query(Ticket).filter(
        Ticket.attendee_id == attendee_id,
        Ticket.qr_code == data.qr_code,
    ).first()
    if not ticket:
        raise HTTPException(status_code=400, detail="Invalid QR code")

    attendee.check_in_status = True
    attendee.checked_in_at = datetime.utcnow()
    db.commit()
    db.refresh(attendee)

    return AttendeeResponse(
        id=attendee.id,
        user_id=attendee.user_id,
        event_id=attendee.event_id,
        registration_date=attendee.registration_date,
        check_in_status=attendee.check_in_status,
        checked_in_at=attendee.checked_in_at,
        user_name=attendee.user.name,
        user_email=attendee.user.email,
    )


@router.post("/events/{event_id}/tickets/purchase", response_model=TicketResponse, status_code=201)
def purchase_ticket(
    event_id: int,
    data: TicketPurchaseRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    ticket_type = db.query(TicketType).filter(
        TicketType.id == data.ticket_type_id,
        TicketType.event_id == event_id,
    ).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")

    # Check sold count
    sold = db.query(Ticket).filter(Ticket.ticket_type_id == ticket_type.id).count()
    if sold >= ticket_type.quantity:
        raise HTTPException(status_code=400, detail="Ticket type sold out")

    # Ensure attendee registration
    attendee = db.query(Attendee).filter(
        Attendee.user_id == current_user.id,
        Attendee.event_id == event_id,
    ).first()
    if not attendee:
        attendee = Attendee(user_id=current_user.id, event_id=event_id)
        db.add(attendee)
        db.flush()

    qr_data = f"ticket-{uuid.uuid4().hex[:12]}"
    qr_image = generate_qr_code(qr_data)

    ticket = Ticket(
        attendee_id=attendee.id,
        ticket_type_id=ticket_type.id,
        qr_code=qr_data,
    )
    db.add(ticket)
    db.flush()

    payment = Payment(
        ticket_id=ticket.id,
        amount=ticket_type.price,
        currency="usd",
        status=PaymentStatus.COMPLETED if ticket_type.price == 0 else PaymentStatus.PENDING,
    )
    db.add(payment)
    db.commit()
    db.refresh(ticket)

    return TicketResponse(
        id=ticket.id,
        attendee_id=ticket.attendee_id,
        ticket_type_id=ticket.ticket_type_id,
        qr_code=ticket.qr_code,
        purchased_at=ticket.purchased_at,
        ticket_type_name=ticket_type.name,
        event_title=event.title,
        payment_status=payment.status.value,
    )


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketResponse(
        id=ticket.id,
        attendee_id=ticket.attendee_id,
        ticket_type_id=ticket.ticket_type_id,
        qr_code=ticket.qr_code,
        purchased_at=ticket.purchased_at,
        ticket_type_name=ticket.ticket_type.name,
        event_title=ticket.attendee.event.title,
        payment_status=ticket.payment.status.value if ticket.payment else "unknown",
    )


@router.get("/users/me/tickets", response_model=list[TicketResponse])
def get_my_tickets(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendee_ids = [a.id for a in current_user.attendee_registrations]
    tickets = db.query(Ticket).filter(Ticket.attendee_id.in_(attendee_ids)).all()
    result = []
    for t in tickets:
        result.append(TicketResponse(
            id=t.id,
            attendee_id=t.attendee_id,
            ticket_type_id=t.ticket_type_id,
            qr_code=t.qr_code,
            purchased_at=t.purchased_at,
            ticket_type_name=t.ticket_type.name,
            event_title=t.attendee.event.title,
            payment_status=t.payment.status.value if t.payment else "unknown",
        ))
    return result
