import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    ATTENDEE = "attendee"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ATTENDEE, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    attendee_registrations = relationship("Attendee", back_populates="user")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    venue = Column(String(255))
    date = Column(DateTime, nullable=False)
    capacity = Column(Integer, default=100)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT, nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organizer = relationship("User")
    attendees = relationship("Attendee", back_populates="event")
    ticket_types = relationship("TicketType", back_populates="event")
    sessions = relationship("Session", back_populates="event")


class TicketType(Base):
    __tablename__ = "ticket_types"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    quantity = Column(Integer, nullable=False, default=100)

    event = relationship("Event", back_populates="ticket_types")
    tickets = relationship("Ticket", back_populates="ticket_type")


class Attendee(Base):
    __tablename__ = "attendees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    check_in_status = Column(Boolean, default=False)
    checked_in_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event"),
    )

    user = relationship("User", back_populates="attendee_registrations")
    event = relationship("Event", back_populates="attendees")
    tickets = relationship("Ticket", back_populates="attendee")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    attendee_id = Column(Integer, ForeignKey("attendees.id"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)
    qr_code = Column(String(500))
    purchased_at = Column(DateTime, default=datetime.utcnow)

    attendee = relationship("Attendee", back_populates="tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    payment = relationship("Payment", back_populates="ticket", uselist=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="usd")
    stripe_payment_id = Column(String(255), nullable=True)
    stripe_checkout_session_id = Column(String(255), nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="payment")


class Speaker(Base):
    __tablename__ = "speakers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    bio = Column(Text)
    photo_url = Column(String(500))
    email = Column(String(255))

    sessions = relationship("SessionSpeaker", back_populates="speaker")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    track = Column(String(100))
    room = Column(String(100))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    event = relationship("Event", back_populates="sessions")
    speakers = relationship("SessionSpeaker", back_populates="session")


class SessionSpeaker(Base):
    __tablename__ = "session_speakers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    speaker_id = Column(Integer, ForeignKey("speakers.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("session_id", "speaker_id", name="uq_session_speaker"),
    )

    session = relationship("Session", back_populates="speakers")
    speaker = relationship("Speaker", back_populates="sessions")
