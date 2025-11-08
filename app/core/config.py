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
    secret_key: str = os.getenv("SECRET_KEY", "default_dev_secret_key_change_this!")
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "password")

    # CORS - allow override via env CORS_ORIGINS, append production domain automatically if present
    cors_origins: Union[str, List[str]] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    )
    
    # App
    app_name: str = "TechEventRadar API"
    debug: bool = False
    
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
    
    class Config:
        env_file = ".env"

settings = Settings()

