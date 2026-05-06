from pydantic_settings import BaseSettings
from typing import List, Union
import os
from dotenv import load_dotenv

# Load environment variables (but exclude admin credentials)
load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./instance/events.db")

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "")
    admin_username: str = os.getenv("ADMIN_USERNAME", "")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "")

    # CORS - allow override via env CORS_ORIGINS, append production domain automatically if present
    cors_origins: Union[str, List[str]] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    )
    
    # App
    app_name: str = "TechEventRadar API"
    debug: bool = False

    # Email (SMTP)
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")
    smtp_from: str = os.getenv("SMTP_FROM", "noreply@eventradar.dev")

    # Telegram
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS origins if it's a string
        if isinstance(self.cors_origins, str):
            self.cors_origins = [origin.strip() for origin in self.cors_origins.split(",")]
        # Auto-add eventradar.dev if running behind that domain
        if "eventradar.dev" not in "".join(self.cors_origins):
            self.cors_origins.extend([
                "https://eventradar.dev",
                "https://www.eventradar.dev"
            ])

        # Security hardening: refuse to boot with weak/missing credentials by default.
        allow_insecure_defaults = os.getenv("ALLOW_INSECURE_DEFAULTS", "false").lower() == "true"
        if not allow_insecure_defaults:
            if not self.secret_key or len(self.secret_key) < 32:
                raise ValueError("SECRET_KEY is required and must be at least 32 characters.")
            if not self.admin_username:
                raise ValueError("ADMIN_USERNAME is required.")
            if not self.admin_password:
                raise ValueError("ADMIN_PASSWORD is required.")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
