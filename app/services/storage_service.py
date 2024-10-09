import os
import re
from app.core.config import settings

class StorageService:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        # Remplace les espaces par des tirets bas
        filename = filename.replace(' ', '_')
        # Supprime tous les caractères non alphanumériques (sauf les tirets bas et les points)
        filename = re.sub(r'[^\w\-_\.]', '', filename)
        return filename
    
    @staticmethod
    def store_on_disk(file_data: bytes, filename: str) -> str:
        os.makedirs(settings.ATTACHMENT_DIR, exist_ok=True)
        file_path = os.path.join(settings.ATTACHMENT_DIR, filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        return file_path
