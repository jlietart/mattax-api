from functools import lru_cache
from opensearchpy import OpenSearch
from app.core.config import settings
from app.services.gmail_service import GmailService
from app.services.opensearch_service import OpenSearchService
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError


@lru_cache()
def get_opensearch_client() -> OpenSearch:
    return OpenSearch(
        hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
        use_ssl=settings.OPENSEARCH_USE_SSL,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme), refresh: str = Header(None)):
    try:
        credentials = Credentials(token=token, refresh_token=refresh, client_id=settings.GOOGLE_CLIENT_ID, client_secret=settings.GOOGLE_CLIENT_SECRET,scopes=['https://www.googleapis.com/auth/gmail.readonly']
    )

        if not credentials.valid:
            raise GoogleAuthError("Token is invalid and cannot be refreshed")
        return credentials
    except GoogleAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: Credentials = Depends(verify_token)):
    return credentials

@lru_cache()
def get_opensearch_service() -> OpenSearchService:
    client = get_opensearch_client()
    return OpenSearchService(client)

@lru_cache()
def get_gmail_service(credentials: Credentials = Depends(get_current_user)) -> GmailService:
    gmail_service = GmailService()
    gmail_service.build_service(credentials)
    return gmail_service