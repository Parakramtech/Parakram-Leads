import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Parakram Lead Intelligence"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://sigma:sigma@localhost:5432/sigma_leads",
    )
    DATABASE_URL_SYNC: str = os.getenv(
        "DATABASE_URL_SYNC",
        "postgresql://sigma:sigma@localhost:5432/sigma_leads",
    )

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    @property
    def is_valid_secret_key(self) -> bool:
        return len(self.SECRET_KEY) >= 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "lead@parakram.co")

    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")

    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

    WHATSAPP_BRIDGE_URL: str = os.getenv("WHATSAPP_BRIDGE_URL", "http://whatsapp-bridge:4000")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    PERSONAL_ALERT_PHONE: str = os.getenv("PERSONAL_ALERT_PHONE", "+917259426670")
    PERSONAL_ALERT_EMAIL: str = os.getenv("PERSONAL_ALERT_EMAIL", "cbvarshini1@gmail.com")

    @property
    def CORS_ORIGINS(self) -> list[str]:
        raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
        return [o.strip() for o in raw.split(",") if o.strip()]

    # Database pooling
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    # Prometheus
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_DEFAULT: int = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))

    # Proxy rotation
    PROXY_LIST: str = os.getenv("PROXY_LIST", "")
    PROXY_ROTATION_ENABLED: bool = os.getenv("PROXY_ROTATION_ENABLED", "false").lower() == "true"

    # SendGrid
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    EMAIL_TRACKING_BASE_URL: str = os.getenv("EMAIL_TRACKING_BASE_URL", "http://localhost:8000")

    # LinkedIn
    LINKEDIN_EMAIL: str = os.getenv("LINKEDIN_EMAIL", "")
    LINKEDIN_PASSWORD: str = os.getenv("LINKEDIN_PASSWORD", "")

    # Razorpay (India payment gateway)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    RAZORPAY_PLAN_ID_EDGE: str = os.getenv("RAZORPAY_PLAN_ID_EDGE", "")
    RAZORPAY_PLAN_ID_FLEET: str = os.getenv("RAZORPAY_PLAN_ID_FLEET", "")

    # Webhook auth
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

    # GDPR
    DATA_RETENTION_DAYS: int = int(os.getenv("DATA_RETENTION_DAYS", "730"))

    # VPS releases / telemetry
    VPS_RELEASE_REPO: str = os.getenv("VPS_RELEASE_REPO", "Parakramtech/Parakram-Leads")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    VPS_HEARTBEAT_INTERVAL_SECONDS: int = int(os.getenv("VPS_HEARTBEAT_INTERVAL_SECONDS", "60"))
    VPS_HEARTBEAT_TTL_SECONDS: int = int(os.getenv("VPS_HEARTBEAT_TTL_SECONDS", "300"))

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
