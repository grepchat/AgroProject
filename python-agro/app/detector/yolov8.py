from typing import Optional, List
import numpy as np
from ultralytics import YOLO

from .base import BaseDetector
from ..models import PlantInstance, DetectionMeta, DetectionResponse
from ..geometry import pixels_to_greenhouse_coords


class YoloV8SegDetector(BaseDetector):
    def __init__(self, weights_path: str, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version
        self.model = YOLO(weights_path)  # загрузка модели

        # Пороговые значения можно калибровать под требование точности 98%
        self.conf_threshold = 0.4
        self.iou_threshold = 0.5

    def detect(
        self,
        image: np.ndarray,
        crop_type: Optional[str] = None,
    ) -> DetectionResponse:
        """
        Основной метод детекции + сегментации.
        Использует сегментационную версию YOLOv8 (task=segment).
        """

        height, width = image.shape[:2]

        results = self.model.predict(
            source=image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )

        result = results[0]  # один кадр
        boxes = result.boxes  # координаты bbox
        masks = result.masks  # маски (для плотной посадки/перекрытий)

        plants: List[PlantInstance] = []

        # Авто-определение культуры по большинству классов (упрощённо)
        inferred_crop_type: Optional[str] = None
        if len(boxes) > 0 and hasattr(self.model, "names"):
            cls_ids = boxes.cls.cpu().numpy().astype(int)
            name_counts = {}
            for cid in cls_ids:
                name = self.model.names.get(cid, "unknown")
                name_counts[name] = name_counts.get(name, 0) + 1
            if name_counts:
                inferred_crop_type = max(name_counts, key=name_counts.get)

        for idx, box in enumerate(boxes):
            xyxy = box.xyxy[0].cpu().numpy().tolist()  # [xmin, ymin, xmax, ymax]
            conf = float(box.conf[0].cpu().numpy())

            # здесь можно использовать mask = masks.data[idx] для более точных координат,
            # особенно при плотной посадке/перекрытиях; ниже – максимально простая схема

            x_center = (xyxy[0] + xyxy[2]) / 2.0
            y_center = (xyxy[1] + xyxy[3]) / 2.0

            x_m, y_m = pixels_to_greenhouse_coords(
                x_px=x_center,
                y_px=y_center,
                image_width=width,
                image_height=height,
            )

            plants.append(
                PlantInstance(
                    id=idx,
                    x_m=x_m,
                    y_m=y_m,
                    bbox=(xyxy[0], xyxy[1], xyxy[2], xyxy[3]),
                    confidence=conf,
                    crop_type=crop_type or inferred_crop_type,
                )
            )

        meta = DetectionMeta(
            model_name=self.model_name,
            model_version=self.model_version,
            crop_type_input=crop_type,
            crop_type_inferred=inferred_crop_type,
            image_width=width,
            image_height=height,
        )

        return DetectionResponse(
            total_plants=len(plants),
            plants=plants,
            meta=meta,
        )
