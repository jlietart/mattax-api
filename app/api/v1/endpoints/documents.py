from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.api.dependencies import get_opensearch_service
from app.schemas.documents import SearchResponse, Document
from app.services.opensearch_service import OpenSearchService, SearchQuery as OpenSearchQuery

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
async def search(
    q: Optional[str] = None,
    from_: int = 0,
    size: int = 10,
    opensearch_service: OpenSearchService = Depends(get_opensearch_service)
):   
    try:
        search_query = OpenSearchQuery(
            query=q or "",
            index="pdf_documents",
            from_=from_,
            size=size
        )
        
        search_response = opensearch_service.search(search_query)
    
        documents = [Document(id=doc.id, filename=doc.content["filename"]) for doc in search_response.hits]
      
        return SearchResponse(
            status="success",
            total=search_response.total,
            documents=documents
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche : {str(e)}")
