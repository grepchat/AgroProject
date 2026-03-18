from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .api import router as api_router
import os
from pathlib import Path


app = FastAPI(title="Plant Detection & Counting Service", version="0.1.0")

# Путь к фронтенду внутри этого репозитория.
# Структура проекта:
# - AgroProjectWeb/Backend/app/main.py  (этот файл)
# - AgroProjectWeb/Frontend/index.html
_current_file = Path(__file__).resolve()
REPO_ROOT = _current_file.parent.parent.parent  # Backend/app -> Backend -> repo root
FRONTEND_DIR = REPO_ROOT / "Frontend"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на время разработки можно так, потом сузим
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Отдаем статические файлы фронтенда
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def root():
    """Главная страница - отдаем index.html"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(
            str(index_file),
            media_type="text/html",
            headers={"Cache-Control": "no-cache"}
        )
    # Если фронтенд не найден, возвращаем JSON с информацией
    return JSONResponse({
        "service": "Plant Detection & Counting Service",
        "version": "0.1.0",
        "description": "Сервис детекции и подсчета растений в теплицах с использованием YOLOv8",
        "endpoints": {
            "detect": "/api/detect",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "status": "running",
        "error": f"Frontend not found at: {FRONTEND_DIR}",
        "debug": {
            "frontend_dir": str(FRONTEND_DIR),
            "exists": FRONTEND_DIR.exists(),
            "index_file": str(index_file),
            "index_exists": index_file.exists() if FRONTEND_DIR.exists() else False
        },
        "note": "Place index.html in Frontend folder."
    })

# Запуск из папки python-agro: uvicorn app.main:app --reload
# Или из папки app: python -m uvicorn main:app --reload
# Для доступа с телефона: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
