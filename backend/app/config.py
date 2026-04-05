from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Event Management System"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://eventuser:eventpass@db:5432/eventdb"

    # JWT
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_placeholder"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_placeholder"

    # Frontend URL for CORS
    FRONTEND_URL: str = "http://localhost:4200"

    class Config:
        env_file = ".env"


settings = Settings()
