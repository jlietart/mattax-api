from functools import lru_cache
from opensearchpy import OpenSearch
from app.core.config import settings
from app.services.gmail_service import GmailService
from app.services.opensearch_service import OpenSearchService

@lru_cache()
def get_opensearch_client() -> OpenSearch:
    return OpenSearch(
        hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
        use_ssl=settings.OPENSEARCH_USE_SSL,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )

@lru_cache()
def get_opensearch_service() -> OpenSearchService:
    client = get_opensearch_client()
    return OpenSearchService(client)

@lru_cache()
def get_gmail_service() -> GmailService:
    return GmailService()
