from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix=settings.API_V1_STR)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
