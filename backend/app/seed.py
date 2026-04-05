"""Seed data for development and testing."""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session as DBSession

from app.auth import hash_password
from app.database import SessionLocal
from app.models import (
    User, UserRole, Event, EventStatus, TicketType,
    Speaker, Session, SessionSpeaker, Attendee, Ticket, Payment, PaymentStatus,
)


def seed_database():
    db: DBSession = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded.")
            return

        # --- Users ---
        admin = User(email="admin@events.com", name="Admin User", role=UserRole.ADMIN, password_hash=hash_password("admin123"))
        organizer = User(email="organizer@events.com", name="Jane Organizer", role=UserRole.ORGANIZER, password_hash=hash_password("org123"))
        attendee1 = User(email="alice@example.com", name="Alice Smith", role=UserRole.ATTENDEE, password_hash=hash_password("pass123"))
        attendee2 = User(email="bob@example.com", name="Bob Johnson", role=UserRole.ATTENDEE, password_hash=hash_password("pass123"))
        db.add_all([admin, organizer, attendee1, attendee2])
        db.flush()

        # --- Events ---
        event1 = Event(
            title="Tech Conference 2025",
            description="A premier technology conference featuring the latest in AI, cloud, and web development.",
            venue="Convention Center, San Francisco",
            date=datetime.utcnow() + timedelta(days=30),
            capacity=500,
            status=EventStatus.PUBLISHED,
            organizer_id=organizer.id,
            image_url="https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800",
        )
        event2 = Event(
            title="Startup Pitch Night",
            description="Watch innovative startups pitch their ideas to a panel of investors.",
            venue="Innovation Hub, Austin",
            date=datetime.utcnow() + timedelta(days=45),
            capacity=200,
            status=EventStatus.PUBLISHED,
            organizer_id=organizer.id,
            image_url="https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800",
        )
        event3 = Event(
            title="Workshop: Building with AI",
            description="Hands-on workshop on integrating AI APIs into your applications.",
            venue="TBD",
            date=datetime.utcnow() + timedelta(days=60),
            capacity=50,
            status=EventStatus.DRAFT,
            organizer_id=organizer.id,
        )
        db.add_all([event1, event2, event3])
        db.flush()

        # --- Ticket Types ---
        tt1 = TicketType(event_id=event1.id, name="General Admission", price=99.00, quantity=400)
        tt2 = TicketType(event_id=event1.id, name="VIP", price=249.00, quantity=100)
        tt3 = TicketType(event_id=event2.id, name="Free Entry", price=0.00, quantity=200)
        db.add_all([tt1, tt2, tt3])
        db.flush()

        # --- Speakers ---
        speaker1 = Speaker(name="Dr. Sarah Chen", bio="AI researcher and author of 'Deep Learning in Practice'", email="sarah@example.com")
        speaker2 = Speaker(name="Mike Rivera", bio="CTO at CloudScale, 15 years in distributed systems", email="mike@example.com")
        speaker3 = Speaker(name="Lisa Park", bio="Full-stack developer and open source contributor", email="lisa@example.com")
        db.add_all([speaker1, speaker2, speaker3])
        db.flush()

        # --- Sessions ---
        base_date = event1.date.replace(hour=9, minute=0)
        s1 = Session(event_id=event1.id, title="Keynote: The Future of AI", description="Opening keynote on AI trends", track="Main Stage", room="Hall A", start_time=base_date, end_time=base_date + timedelta(hours=1))
        s2 = Session(event_id=event1.id, title="Building Scalable APIs", description="Best practices for API design", track="Backend", room="Room 201", start_time=base_date + timedelta(hours=1, minutes=30), end_time=base_date + timedelta(hours=2, minutes=30))
        s3 = Session(event_id=event1.id, title="Modern Frontend Architecture", description="Angular, React, and beyond", track="Frontend", room="Room 202", start_time=base_date + timedelta(hours=1, minutes=30), end_time=base_date + timedelta(hours=2, minutes=30))
        db.add_all([s1, s2, s3])
        db.flush()

        # --- Session-Speaker Links ---
        db.add_all([
            SessionSpeaker(session_id=s1.id, speaker_id=speaker1.id),
            SessionSpeaker(session_id=s2.id, speaker_id=speaker2.id),
            SessionSpeaker(session_id=s3.id, speaker_id=speaker3.id),
        ])

        # --- Sample Attendee + Ticket ---
        att1 = Attendee(user_id=attendee1.id, event_id=event1.id)
        db.add(att1)
        db.flush()
        ticket1 = Ticket(attendee_id=att1.id, ticket_type_id=tt1.id, qr_code="ticket-seed-001")
        db.add(ticket1)
        db.flush()
        payment1 = Payment(ticket_id=ticket1.id, amount=99.00, status=PaymentStatus.COMPLETED, stripe_payment_id="mock_seed_001")
        db.add(payment1)

        db.commit()
        print("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
