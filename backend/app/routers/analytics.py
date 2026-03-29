from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Event, Attendee, Ticket, Payment, PaymentStatus, User
from app.schemas import EventAnalytics

router = APIRouter(prefix="/api/events", tags=["Analytics"])


@router.get("/{event_id}/analytics", response_model=EventAnalytics)
def get_event_analytics(
    event_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    attendees = db.query(Attendee).filter(Attendee.event_id == event_id).all()
    total_registrations = len(attendees)
    total_checked_in = sum(1 for a in attendees if a.check_in_status)
    check_in_rate = (total_checked_in / total_registrations * 100) if total_registrations > 0 else 0

    # Revenue by ticket type
    tickets_by_type = defaultdict(lambda: {"count": 0, "revenue": 0.0})
    attendee_ids = [a.id for a in attendees]
    tickets = db.query(Ticket).filter(Ticket.attendee_id.in_(attendee_ids)).all() if attendee_ids else []

    total_revenue = 0.0
    for ticket in tickets:
        tt_name = ticket.ticket_type.name
        if ticket.payment and ticket.payment.status == PaymentStatus.COMPLETED:
            tickets_by_type[tt_name]["count"] += 1
            tickets_by_type[tt_name]["revenue"] += ticket.payment.amount
            total_revenue += ticket.payment.amount

    tickets_by_type_list = [
        {"type": name, "count": data["count"], "revenue": data["revenue"]}
        for name, data in tickets_by_type.items()
    ]

    # Registrations over time (grouped by date)
    reg_by_date = defaultdict(int)
    for a in attendees:
        date_key = a.registration_date.strftime("%Y-%m-%d")
        reg_by_date[date_key] += 1

    registrations_over_time = [
        {"date": date, "count": count}
        for date, count in sorted(reg_by_date.items())
    ]

    return EventAnalytics(
        event_id=event.id,
        event_title=event.title,
        total_capacity=event.capacity,
        total_registrations=total_registrations,
        total_checked_in=total_checked_in,
        check_in_rate=round(check_in_rate, 2),
        total_revenue=round(total_revenue, 2),
        tickets_by_type=tickets_by_type_list,
        registrations_over_time=registrations_over_time,
    )
