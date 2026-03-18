from typing import Dict, Optional
from .yolov8 import YoloV8SegDetector


class ModelRegistry:
    """
    Реестр моделей по типу культуры.
    Можно подменить конфигом/БД.
    """

    def __init__(self):
        # Пример: разные веса для разных культур
        '''self._models: Dict[str, YoloV8SegDetector] = {
            "tomato": YoloV8SegDetector(
                weights_path="weights/yolov8_tomato_seg.pt",
                model_name="yolov8_tomato_seg",
                model_version="1.0.0",
            ),
            "cucumber": YoloV8SegDetector(
                weights_path="weights/yolov8_cucumber_seg.pt",
                model_name="yolov8_cucumber_seg",
                model_version="1.0.0",
            ),
        }'''
        # универсальная модель "на всё"
        import os
        # Путь к весам относительно текущего файла: app/detector/registry.py -> ../weights/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        weights_path = os.path.join(base_dir, "weights", "yolov8_flowers.pt")
        self._default = YoloV8SegDetector(
            weights_path=weights_path,
            model_name="yolov8_flowers",
            model_version="1.0.0",)

    def get(self, crop_type: Optional[str]) -> YoloV8SegDetector:
        # if crop_type and crop_type in self._models:
        #    return self._models[crop_type]
        return self._default
