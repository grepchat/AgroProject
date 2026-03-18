from typing import List, Optional, Tuple
from pydantic import BaseModel, Field


class PlantInstance(BaseModel):
    id: int = Field(..., description="Локальный ID растения внутри ответа")
    x_m: float = Field(..., description="X-координата растения в метрах в системе теплицы")
    y_m: float = Field(..., description="Y-координата растения в метрах в системе теплицы")
    bbox: Tuple[float, float, float, float] = Field(
        ..., description="(xmin, ymin, xmax, ymax) в пикселях исходного изображения"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность модели")
    crop_type: Optional[str] = Field(None, description="Определённая/указанная культура")


class DetectionMeta(BaseModel):
    model_name: str
    model_version: str
    crop_type_input: Optional[str]
    crop_type_inferred: Optional[str]
    image_width: int
    image_height: int


class DetectionResponse(BaseModel):
    total_plants: int
    plants: List[PlantInstance]
    meta: DetectionMeta
