from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables (but exclude admin credentials)
load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./instance/events.db")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "default_dev_secret_key_change_this!")
    admin_username: str = "admin"  # Hardcoded for development
    admin_password: str = "password"  # Hardcoded for development
    
    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # App
    app_name: str = "TechEventRadar API"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()

