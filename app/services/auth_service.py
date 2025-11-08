from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from ..core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    def __init__(self):
        pass
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials.

        Priority:
        1. Use ADMIN_USERNAME / ADMIN_PASSWORD from environment (via settings).
           If password looks like a bcrypt hash (starts with "$2"), verify with hash.
           Otherwise compare plain text for backward compatibility.
        2. Fallback to legacy hardcoded (admin/password) if env vars missing.
        """
        env_user = settings.admin_username
        env_pass = settings.admin_password

        if env_user and env_pass:
            # Support hashed password if provided
            if env_pass.startswith("$2"):
                return username == env_user and self.verify_password(password, env_pass)
            else:
                return username == env_user and password == env_pass

        # Legacy fallback
        return (username == "admin" and password == "password")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None

