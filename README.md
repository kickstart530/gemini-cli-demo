# Event Management System

A comprehensive web-based Event Management System built to demonstrate Gemini CLI capabilities. Features event creation, attendee management, multi-track agenda building, real-time analytics, and Stripe payment integration.

## Tech Stack

- **Frontend:** Angular 17 with Angular Material
- **Backend:** Python FastAPI
- **Database:** PostgreSQL
- **Payments:** Stripe
- **Infrastructure:** Docker Compose

## Features

1. **Event Creation/Management** - Create, edit, publish, and manage events with details (title, description, venue, date, capacity)
2. **Attendee Management** - Registration, ticket purchasing, QR code check-in, and attendee profile management
3. **Agenda Builder** - Build multi-track schedules with speakers and sessions, with conflict detection
4. **Analytics Dashboard** - Real-time data on registrations, revenue, and check-in status
5. **Event Website** - Public-facing application for attendees to discover and register for events
6. **Payment Integration** - Stripe checkout for ticket purchases with webhook support

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Node.js 20+ and Python 3.11+ for local development

### Run with Docker Compose

```bash
docker compose up --build
```

This starts:
- **Frontend:** http://localhost:4200
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Database:** PostgreSQL on port 5432

### Default Users (Seed Data)

| Email | Password | Role |
|-------|----------|------|
| admin@events.com | admin123 | Admin |
| organizer@events.com | org123 | Organizer |
| alice@example.com | pass123 | Attendee |
| bob@example.com | pass123 | Attendee |

## Project Structure

```
.
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── config.py        # Configuration and settings
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py          # JWT authentication
│   │   ├── seed.py          # Database seed data
│   │   └── routers/         # API route handlers
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── events.py    # Event CRUD endpoints
│   │       ├── attendees.py # Registration & ticket endpoints
│   │       ├── sessions.py  # Session & speaker endpoints
│   │       ├── analytics.py # Analytics endpoints
│   │       └── payments.py  # Stripe payment endpoints
│   ├── tests/               # Backend tests
│   ├── alembic/             # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── pages/       # Page components
│   │   │   ├── services/    # API services
│   │   │   ├── models/      # TypeScript interfaces
│   │   │   └── interceptors/# HTTP interceptors
│   │   └── environments/    # Environment configs
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml        # Docker Compose configuration
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

### Events
- `POST /api/events` - Create event
- `GET /api/events` - List events (with search/filter)
- `GET /api/events/{id}` - Get event details
- `PUT /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event
- `POST /api/events/{id}/publish` - Publish event

### Attendees & Tickets
- `POST /api/events/{id}/register` - Register for event
- `GET /api/events/{id}/attendees` - List attendees
- `POST /api/attendees/{id}/check-in` - QR code check-in
- `POST /api/events/{id}/tickets/purchase` - Purchase ticket
- `GET /api/tickets/{id}` - Get ticket with QR code
- `GET /api/users/me/tickets` - Get my tickets

### Sessions & Speakers
- `POST /api/events/{id}/sessions` - Create session
- `GET /api/events/{id}/sessions` - List sessions (agenda)
- `PUT /api/sessions/{id}` - Update session
- `POST /api/speakers` - Create speaker
- `GET /api/speakers` - List speakers

### Analytics
- `GET /api/events/{id}/analytics` - Event analytics

### Payments
- `POST /api/payments/checkout/{ticket_id}` - Create Stripe checkout
- `POST /api/payments/webhook` - Stripe webhook
- `POST /api/payments/refund/{ticket_id}` - Refund ticket

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
ng serve
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## Stripe Integration

To enable real Stripe payments:

1. Get your Stripe API keys from https://dashboard.stripe.com
2. Set environment variables:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_WEBHOOK_SECRET`

Without Stripe keys, the system runs in mock mode where payments are auto-completed.

## Database Schema

The system uses the following core tables:
- `users` - User accounts with roles (admin, organizer, attendee)
- `events` - Event details with status management
- `ticket_types` - Different ticket tiers per event
- `attendees` - Event registrations
- `tickets` - Purchased tickets with QR codes
- `payments` - Payment records linked to Stripe
- `sessions` - Agenda sessions with tracks and rooms
- `speakers` - Speaker profiles
- `session_speakers` - Many-to-many session-speaker links

## License

MIT
