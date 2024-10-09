from pydantic import BaseModel
from typing import List, Optional

class Document(BaseModel):
    id: str
    filename: str
    url: str

class SearchQuery(BaseModel):
    q: str
    index: str
    from_: int = 0
    size: int = 10
    filters: Optional[dict] = None

class SearchResponse(BaseModel):
    status: str
    documents: List[Document]
    total: int