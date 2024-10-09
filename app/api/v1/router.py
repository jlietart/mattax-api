from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.api.v1.endpoints import documents, gmail

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(gmail.router, prefix="/gmail", tags=["gmail"])