from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    # Path to YOLO model. For demo, defaults to yolov8n.pt (generic COCO model).
    yolo_model_path: str = os.getenv("AGRO_YOLO_MODEL", "yolov8n.pt")

    # Inference device: "cuda" if available, else "cpu". Can be overridden via env.
    device: str = os.getenv("AGRO_DEVICE", "cuda")

    # Output directory for exports
    output_dir: str = os.getenv("AGRO_OUTPUT_DIR", os.path.join("data", "outputs"))

    # Target classes for the MVP demo. Real model should be trained for these.
    target_classes: tuple[str, ...] = (
        "healthy",
        "dead",
        "grade_1",
        "grade_2",
        "fruit",
    )

    # Эвристика: оставить только один объект (крупнейший и вытянутый)
    heuristic_single_object: bool = True
    heuristic_min_area: int = 1500  # минимальная площадь контура
    heuristic_min_aspect: float = 1.8  # минимальное соотношение сторон (вытянутость)
    heuristic_min_area_ratio: float = 0.003  # доля площади изображения
    heuristic_min_rectangularity: float = 0.55  # area/(w*h)
    heuristic_prefer_vertical: bool = True
    heuristic_vertical_tolerance_deg: float = 25.0


CONFIG = AppConfig()


