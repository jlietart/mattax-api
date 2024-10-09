from opensearchpy import Field
from pydantic import BaseModel
from typing import List, Dict, Optional

class Document(BaseModel):
    id: str
    content: dict
    index: str

class SearchQuery(BaseModel):
    query: str
    index: str
    from_: int = 0
    size: int = 10
    filters: Optional[dict] = None

class SearchResponse(BaseModel):
    total: int
    hits: List[Document]
    max_score: Optional[float] = Field(None)

class IndexResponse(BaseModel):
    _index: str
    _id: str
    _version: int
    result: str
    _shards: Dict[str, int]
    _seq_no: int
    _primary_term: int

