import os
from fastapi import FastAPI, Request
from app.core.config import settings
from app.api.v1.router import api_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplacez par l'URL de votre frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes HTTP
    allow_headers=["*"],  # Autorise tous les headers
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve attachments statically
attachments_dir = os.path.join(os.getcwd(), settings.ATTACHMENT_DIR)
os.makedirs(attachments_dir, exist_ok=True)
app.mount("/attachments", StaticFiles(directory=attachments_dir), name="attachments")

@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
