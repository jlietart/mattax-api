from fastapi import APIRouter, HTTPException, Query, Depends
from starlette.responses import RedirectResponse
from typing import List, Dict, Any
from app.services.gmail_service import GmailService
from app.core.config import settings
from app.api.dependencies import get_gmail_service, get_opensearch_service
from app.services.opensearch_service import OpenSearchService
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Gmail"}

@router.get("/authorize")
async def authorize(gmail_service: GmailService = Depends(get_gmail_service)):
    authorization_url = gmail_service.get_authorization_url(settings.REDIRECT_URI)
    return RedirectResponse(authorization_url)

@router.get("/oauth2callback")
async def oauth2callback(code: str, gmail_service: GmailService = Depends(get_gmail_service)):
    gmail_service.fetch_token(code, settings.REDIRECT_URI)
    return {"message": "Authentification réussie"}

@router.get("/emails", response_model=List[Dict[str, Any]])
async def get_emails(gmail_service: GmailService = Depends(get_gmail_service)):
    try:
        return gmail_service.get_emails()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/synchronize")
async def get_pdf_attachments_route(
    year: int = Query(...),
    month: int = Query(...),
    force_sync: bool = Query(False),
    gmail_service: GmailService = Depends(get_gmail_service),
    opensearch_service: OpenSearchService = Depends(get_opensearch_service)
):
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            yield "data: Début de la synchronisation...\n\n"
            await asyncio.sleep(0.1)

            attachment_count = 0
            skipped_count = 0
            async for attachment in gmail_service.get_pdf_attachments(year, month, force_sync):
                try:
                    # Extraction du texte du PDF
                    pdf_text = opensearch_service.extract_text_from_pdf(attachment['data'])
                    attachment['content'] = pdf_text

                    result = opensearch_service.index_pdf_attachment(attachment)
                    if result['status'] == 'skipped':
                        skipped_count += 1
                        yield f"data: Fichier déjà indexé, ignoré : {attachment['filename']}\n\n"
                    else:
                        attachment_count += 1
                        yield f"data: Indexation de {attachment['filename']} : {result['status']}\n\n"
                except Exception as e:
                    yield f"data: Erreur lors de l'indexation de {attachment['filename']} : {str(e)}\n\n"
                await asyncio.sleep(0.1)

            yield f"data: Synchronisation terminée. {attachment_count} fichiers indexés, {skipped_count} fichiers ignorés.\n\n"
        except Exception as e:
            yield f"data: Erreur lors de la synchronisation : {str(e)}\n\n"
        finally:
            yield "data: [END]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
