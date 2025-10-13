from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np


Color = Tuple[int, int, int]


def get_color_for_class(class_name: str) -> Color:
    mapping = {
        "healthy": (0, 200, 0),
        "dead": (50, 50, 50),
        "grade_1": (0, 165, 255),
        "grade_2": (0, 69, 255),
        "fruit": (255, 0, 0),
    }
    return mapping.get(class_name, (200, 200, 200))


def draw_detections(
    image_bgr: np.ndarray,
    detections: List[dict],
    show_scores: bool = True,
) -> np.ndarray:
    annotated = image_bgr.copy()
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        cls_name = det.get("class_name", "object")
        score = det.get("score", None)
        color = get_color_for_class(cls_name)

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        label = cls_name
        if show_scores and score is not None:
            label = f"{label} {score:.2f}"

        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        th_total = th + baseline + 4
        cv2.rectangle(annotated, (x1, y1 - th_total), (x1 + tw + 4, y1), color, -1)
        cv2.putText(
            annotated,
            label,
            (x1 + 2, y1 - baseline - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
    return annotated


