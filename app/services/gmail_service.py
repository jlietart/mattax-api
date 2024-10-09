import base64
from email.utils import parsedate_to_datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List, Dict, Any
from app.core.config import settings
import pytesseract
from pdf2image import convert_from_bytes
import asyncio

class GmailService:
    def __init__(self):
        self.service = None

    def build_service(self, credentials: Credentials):
        if not self.service:
            self.service = build(settings.API_SERVICE_NAME, settings.API_VERSION, credentials=credentials)
        return self.service
    
    def get_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        emails = []
        for message in messages:
            msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
            emails.append({
                'id': msg['id'],
                'snippet': msg['snippet']
            })
        
        return emails

    async def get_pdf_attachments(self, year: int, month: int, force_sync: bool = False):
        query = f"has:attachment filename:pdf after:{year}/{month}/25 before:{year}/{month+1}/01"
        if month == 12:
            query = f"has:attachment filename:pdf after:{year}/12/01 before:{year+1}/01/01"
        
        request = self.service.users().messages().list(userId='me', q=query)
        results = await self.run_in_executor(request)
        messages = results.get('messages', [])
        
        attachments = []
        for message in messages:
            request = self.service.users().messages().get(userId='me', id=message['id'], format='full')
            msg = await self.run_in_executor(request)
            payload = msg['payload']
            headers = payload.get("headers")
            parts = payload.get("parts", [])
            
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            date_str = next((header['value'] for header in headers if header['name'] == 'Date'), None)
    
            date = parsedate_to_datetime(date_str) if date_str else None
       
            for part in parts:
                if part.get("filename") and part.get("filename").lower().endswith('.pdf'):
                    if part.get("body").get("attachmentId"):
                        att_id = part["body"]["attachmentId"]
                        request = self.service.users().messages().attachments().get(userId='me', messageId=message['id'], id=att_id)
                        att = await self.run_in_executor(request)
                        data = att["data"]
                        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        
                        attachments.append({
                            'filename': part.get("filename"),
                            'data': file_data,
                            'subject': subject,
                            'date': date.isoformat(),
                            'force_sync': force_sync
                        })
            await asyncio.sleep(0)  # Permet à d'autres tâches de s'exécuter

        return attachments

    async def run_in_executor(self, request):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, request.execute)

    @staticmethod
    def extract_text_from_pdf(pdf_data: bytes) -> str:
        images = convert_from_bytes(pdf_data)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text
