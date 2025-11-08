from fastapi import APIRouter
from .public import router as public_router
from .admin import router as admin_router

api_router = APIRouter()

api_router.include_router(public_router, prefix="/api", tags=["public"])
api_router.include_router(admin_router, prefix="/api/admin", tags=["admin"])


