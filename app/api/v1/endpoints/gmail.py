from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any
from app.services.gmail_service import GmailService
from app.api.dependencies import get_gmail_service, get_opensearch_service
from app.services.opensearch_service import OpenSearchService
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio

from app.services.storage_service import StorageService

import json

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to the Gmail API"}

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
            yield f"data: {json.dumps({'event': 'start', 'message': 'Starting synchronization...'})}\n\n"
            await asyncio.sleep(0.1)

            attachments = await gmail_service.get_pdf_attachments(year, month, force_sync)
            yield f"data: {json.dumps({'event': 'get_total', 'total': len(attachments)})}\n\n"
            
            attachment_count = 0
            skipped_count = 0
            for attachment in attachments:
                try:
                    # Extracting text from PDF
                    pdf_text = opensearch_service.extract_text_from_pdf(attachment['data'])
                    attachment['content'] = pdf_text

                    sanitized_filename = StorageService.sanitize_filename(attachment['filename'])
                    attachment['filename'] = sanitized_filename
                    result = opensearch_service.index_pdf_attachment(attachment)
                    StorageService.store_on_disk(attachment['data'], sanitized_filename)
                    
                    if result['status'] == 'skipped':
                        skipped_count += 1
                        yield f"data: {json.dumps({'event': 'skipped', 'message': f'File already indexed, skipped: {attachment["filename"]}'})}\n\n"
                    else:
                        attachment_count += 1
                        yield f"data: {json.dumps({'event': 'indexed', 'message': f'Indexing {attachment["filename"]}: {result["status"]}'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'event': 'error', 'message': f'Error while indexing {attachment["filename"]}: {str(e)}'})}\n\n"
                await asyncio.sleep(0.1)

            yield f"data: {json.dumps({'event': 'end', 'message': f'Synchronization completed. {attachment_count} files indexed, {skipped_count} files skipped.'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': f'Error during synchronization: {str(e)}'})}\n\n"
        finally:
            yield "data: [END]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
