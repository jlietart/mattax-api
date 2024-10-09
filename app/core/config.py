from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, ClassVar
import os  # Si vous avez vraiment besoin de os

class Settings(BaseSettings):
    # Si vous avez besoin de os dans la classe, annotez-le comme ClassVar
    os: ClassVar = os

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    CLIENT_SECRETS_FILE: str = "client_secret.json"
    SCOPES: List[str] = ['https://www.googleapis.com/auth/gmail.readonly']
    API_SERVICE_NAME: str = 'gmail'
    API_VERSION: str = 'v1'
    REDIRECT_URI: str = 'http://localhost:8000/api/v1/auth/gmail/oauth2callback'

    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key"

    ATTACHMENT_DIR: str = "attachments"

    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USE_SSL: bool = False
    OPENSEARCH_INDEX: str = "pdf_documents"

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MattaxAPI"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = Settings()

