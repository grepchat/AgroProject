from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from ..models import PlantInstance, DetectionMeta, DetectionResponse


class BaseDetector(ABC):
    @abstractmethod
    def detect(
        self,
        image: np.ndarray,
        crop_type: Optional[str] = None,
    ) -> DetectionResponse:
        ...
