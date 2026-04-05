from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, events, attendees, sessions, analytics, payments

# Create all tables on startup (for development)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="A comprehensive Event Management System with registration, ticketing, agenda building, and analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(attendees.router)
app.include_router(sessions.router)
app.include_router(analytics.router)
app.include_router(payments.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
