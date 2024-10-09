from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse
from app.services.gmail_service import GmailService
from app.core.config import settings
from app.api.dependencies import get_gmail_service
router = APIRouter()

@router.get("/gmail")
async def authorize(gmail_service: GmailService = Depends(get_gmail_service)):
    authorization_url = gmail_service.get_authorization_url(settings.REDIRECT_URI)
    return RedirectResponse(authorization_url)

@router.get("/gmail/oauth2callback")
async def oauth2callback(code: str, gmail_service: GmailService = Depends(get_gmail_service)):
    return gmail_service.fetch_token(code, settings.REDIRECT_URI)