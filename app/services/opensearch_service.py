from dateutil import parser
from datetime import timezone
import pytesseract
from opensearchpy import OpenSearch
from typing import List, Dict, Any

from pdf2image import convert_from_bytes
from app.schemas.opensearch import SearchQuery, Document, IndexResponse, SearchResponse
from dateutil import parser
from email.utils import parsedate_to_datetime
from app.core.config import settings

class OpenSearchService:
    def __init__(self, host='localhost', port=9200):
        self.client = OpenSearch(hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}])

    def is_file_indexed(self, filename: str, date: str) -> bool:
        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"filename.keyword": filename}},
                            {"match": {"date": date}}
                        ]
                    }
                }
            }
            result = self.client.search(index=settings.OPENSEARCH_INDEX, body=query)
            return result['hits']['total']['value'] > 0
        except Exception as e:
            print(f"Erreur lors de la vérification de l'indexation : {str(e)}")
            return False

    def index_pdf_attachment(self, attachment):
        if self.is_file_indexed(attachment['filename'], attachment['date']):
            print(f"Le fichier {attachment['filename']} est déjà indexé")
            return {"status": "skipped", "filename": attachment['filename']}
        
        try:
            document = {
                'filename': attachment['filename'],
                'subject': attachment['subject'],
                'date': attachment['date'],
                'content': attachment['content'],
                'url': 'http://localhost:8000/attachments/' + attachment['filename']
            }
            
            print(f"Document à indexer : {document}")
            
            response = self.client.index(
                index=settings.OPENSEARCH_INDEX,
                body=document,
                refresh=True
            )
            print(f"Réponse d'indexation : {response}")
            return {"status": "success", "filename": attachment['filename']}
        except Exception as e:
            print(f"Erreur lors de l'indexation : {str(e)}")
            return {"status": "error", "filename": attachment['filename'], "error": str(e)}

    @staticmethod
    def extract_text_from_pdf(pdf_data: bytes) -> str:
        try:
            images = convert_from_bytes(pdf_data)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""

    def index_document(self, document: Document) -> IndexResponse:
        response = self.client.index(index=document.index, body=document.content, id=document.id)
        return IndexResponse(**response)

    def search(self, query: SearchQuery) -> SearchResponse:
        body = {
            "query": {"match": {"content": query.query}},
            "from": query.from_,
            "size": query.size
        }
        if query.filters:
            body["post_filter"] = query.filters
        
        response = self.client.search(index=settings.OPENSEARCH_INDEX, body=body)
        hits = [Document(id=hit['_id'], content=hit['_source'], index=hit['_index']) for hit in response['hits']['hits']]
        return SearchResponse(
            hits=hits,
            total=response['hits']['total']['value'],
            max_score=response['hits']['max_score']
        )

    def get_document(self, index: str, id: str) -> Document:
        response = self.client.get(index=index, id=id)
        return Document(id=response['_id'], content=response['_source'], index=response['_index'])

    def update_document(self, document: Document) -> IndexResponse:
        response = self.client.update(index=document.index, id=document.id, body={"doc": document.content})
        return IndexResponse(**response)

    def delete_document(self, index: str, id: str) -> Dict[str, Any]:
        return self.client.delete(index=index, id=id)
