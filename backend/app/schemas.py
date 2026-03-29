from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = "attendee"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Events ---
class TicketTypeCreate(BaseModel):
    name: str
    price: float = 0.0
    quantity: int = 100


class TicketTypeResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    venue: Optional[str] = None
    date: datetime
    capacity: int = 100
    image_url: Optional[str] = None
    ticket_types: list[TicketTypeCreate] = []


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    venue: Optional[str] = None
    date: Optional[datetime] = None
    capacity: Optional[int] = None
    image_url: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    venue: Optional[str]
    date: datetime
    capacity: int
    status: str
    organizer_id: int
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    ticket_types: list[TicketTypeResponse] = []

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    id: int
    title: str
    venue: Optional[str]
    date: datetime
    capacity: int
    status: str
    image_url: Optional[str]
    attendee_count: int = 0

    class Config:
        from_attributes = True


# --- Attendees ---
class AttendeeResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registration_date: datetime
    check_in_status: bool
    checked_in_at: Optional[datetime]
    user_name: str = ""
    user_email: str = ""

    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    qr_code: str


# --- Tickets ---
class TicketPurchaseRequest(BaseModel):
    ticket_type_id: int


class TicketResponse(BaseModel):
    id: int
    attendee_id: int
    ticket_type_id: int
    qr_code: Optional[str]
    purchased_at: datetime
    ticket_type_name: str = ""
    event_title: str = ""
    payment_status: str = ""

    class Config:
        from_attributes = True


# --- Sessions ---
class SessionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    track: Optional[str] = None
    room: Optional[str] = None
    start_time: datetime
    end_time: datetime
    speaker_ids: list[int] = []


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    track: Optional[str] = None
    room: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    speaker_ids: Optional[list[int]] = None


class SpeakerBrief(BaseModel):
    id: int
    name: str
    photo_url: Optional[str]

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: int
    event_id: int
    title: str
    description: Optional[str]
    track: Optional[str]
    room: Optional[str]
    start_time: datetime
    end_time: datetime
    speakers: list[SpeakerBrief] = []

    class Config:
        from_attributes = True


# --- Speakers ---
class SpeakerCreate(BaseModel):
    name: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    email: Optional[str] = None


class SpeakerResponse(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    photo_url: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True


# --- Analytics ---
class EventAnalytics(BaseModel):
    event_id: int
    event_title: str
    total_capacity: int
    total_registrations: int
    total_checked_in: int
    check_in_rate: float
    total_revenue: float
    tickets_by_type: list[dict]
    registrations_over_time: list[dict]


# --- Payments ---
class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class PaymentResponse(BaseModel):
    id: int
    ticket_id: int
    amount: float
    currency: str
    status: str
    stripe_payment_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
