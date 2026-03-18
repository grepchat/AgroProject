from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import numpy as np
import cv2

from .detector.registry import ModelRegistry
from .models import DetectionResponse

router = APIRouter()
model_registry = ModelRegistry()


@router.post("/detect", response_model=DetectionResponse)
async def detect_plants(
    image: UploadFile = File(..., description="Изображение участка теплицы"),
    crop_type: Optional[str] = Form(
        None, description="Тип культуры (если известен). Если пусто — автоопределение."
    ),
):
    if image.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Поддерживаются только JPEG/PNG")

    contents = await image.read()
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Не удалось декодировать изображение")

    detector = model_registry.get(crop_type)
    result: DetectionResponse = detector.detect(img, crop_type=crop_type)

    return result
