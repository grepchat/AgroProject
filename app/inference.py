from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from .config import CONFIG


@dataclass
class Detection:
    bbox: List[float]  # [x1, y1, x2, y2]
    class_name: str
    score: float


class InferenceEngine:
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        self.model_path = model_path or CONFIG.yolo_model_path
        self.device = device or CONFIG.device
        self._yolo_model = None
        self._yolo_available_error: Optional[str] = None

        self._try_load_yolo()

    # --- Public API ---
    def analyze_image(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("Пустое изображение для анализа")

        if self._yolo_model is not None:
            try:
                return self._run_yolo(image_bgr)
            except Exception as e:  # Резерв к эвристике
                self._yolo_available_error = f"Ошибка инференса YOLO: {e}"

        return self._run_heuristic(image_bgr)

    def yolo_status(self) -> str:
        if self._yolo_model is not None:
            return f"YOLO загружена: {self.model_path} на {self.device}"
        if self._yolo_available_error:
            return f"YOLO недоступна: {self._yolo_available_error}"
        return "YOLO не загружена"

    # --- Private helpers ---
    def _try_load_yolo(self) -> None:
        try:
            from ultralytics import YOLO  # Lazy import

            self._yolo_model = YOLO(self.model_path)
            # Device selection is in predict call; store preferred device
        except Exception as e:
            self._yolo_model = None
            self._yolo_available_error = str(e)

    def _run_yolo(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        # Ultralytics ожидает RGB
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        results = self._yolo_model.predict(
            source=image_rgb, device=self.device, verbose=False
        )

        detections: List[Detection] = []
        # Берём первый результат из батча
        if results and len(results) > 0:
            r = results[0]
            # Координаты боксов в xyxy
            if hasattr(r, "boxes") and r.boxes is not None:
                for b in r.boxes:
                    xyxy = b.xyxy[0].tolist()
                    score = float(b.conf[0]) if hasattr(b, "conf") else 0.0
                    cls_id = int(b.cls[0]) if hasattr(b, "cls") else -1
                    cls_name = (
                        r.names.get(cls_id, str(cls_id)) if hasattr(r, "names") else str(cls_id)
                    )
                    detections.append(
                        Detection(bbox=[float(v) for v in xyxy], class_name=cls_name, score=score)
                    )

        # Агрегируем количество по классам
        counts: Dict[str, int] = {}
        for d in detections:
            counts[d.class_name] = counts.get(d.class_name, 0) + 1

        return {
            "engine": "yolo",
            "model_path": self.model_path,
            "device": self.device,
            "detections": [d.__dict__ for d in detections],
            "counts": counts,
        }

    def _run_heuristic(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        # Простая эвристика Excess Green для поиска «зелени»
        image = image_bgr.copy()
        b, g, r = cv2.split(image)
        exg = 2 * g.astype(np.int16) - r.astype(np.int16) - b.astype(np.int16)
        exg = np.clip(exg, 0, 255).astype(np.uint8)
        exg = cv2.GaussianBlur(exg, (5, 5), 0)

        # Адаптивный порог
        thr = cv2.adaptiveThreshold(
            exg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, -5
        )
        # Морфологическая очистка
        kernel = np.ones((3, 3), np.uint8)
        opened = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel, iterations=2)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Поиск контуров
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h_img, w_img = image_bgr.shape[:2]
        img_area = float(max(1, w_img * h_img))

        raw_detections: List[Detection] = []
        # (det, area, aspect, vertical_factor, rectangularity, score)
        candidates: List[tuple[Detection, float, float, float, float, float]] = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < max(1, CONFIG.heuristic_min_area):
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            short_side = max(1, min(w, h))
            aspect = max(w, h) / float(short_side)
            area_ratio = float(area) / img_area
            rectangularity = float(area) / float(max(1, w * h))

            if area_ratio < CONFIG.heuristic_min_area_ratio:
                continue
            if rectangularity < CONFIG.heuristic_min_rectangularity:
                continue

            # Оценка вертикальности по эллипсу (если доступно)
            vertical_factor = 1.0
            if CONFIG.heuristic_prefer_vertical and len(cnt) >= 5:
                try:
                    (cx, cy), (ma, Mi), angle = cv2.fitEllipse(cnt)
                    # угол 0-180 относительно оси X; близость к 90 — вертикаль
                    diff = abs(angle - 90.0)
                    if diff > 90.0:
                        diff = 180.0 - diff
                    tol = max(1e-6, CONFIG.heuristic_vertical_tolerance_deg)
                    vertical_factor = max(0.0, 1.0 - diff / tol)
                except Exception:
                    vertical_factor = 1.0
            det = Detection(
                bbox=[float(x), float(y), float(x + w), float(y + h)],
                class_name="healthy",
                score=0.5,
            )
            raw_detections.append(det)
            if aspect >= CONFIG.heuristic_min_aspect:
                # Комбинированный скор: размер * вытянутость * вертикальность * прямоугольность
                score = float(area) * float(aspect) * float(1.0 + vertical_factor) * float(1.0 + rectangularity)
                candidates.append((det, float(area), float(aspect), float(vertical_factor), float(rectangularity), float(score)))

        detections: List[Detection]
        if CONFIG.heuristic_single_object:
            best: Optional[Detection] = None
            if candidates:
                candidates.sort(key=lambda t: t[-1], reverse=True)
                best = candidates[0][0]
            elif raw_detections:
                # если нет вытянутых — возьмём крупнейший
                raw_detections.sort(
                    key=lambda d: (d.bbox[2] - d.bbox[0]) * (d.bbox[3] - d.bbox[1]),
                    reverse=True,
                )
                best = raw_detections[0]

            if best is not None:
                best.class_name = "fruit"
                best.score = 0.9
                detections = [best]
            else:
                detections = []
        else:
            detections = raw_detections

        counts: Dict[str, int] = {}
        for d in detections:
            counts[d.class_name] = counts.get(d.class_name, 0) + 1

        return {
            "engine": "heuristic",
            "model_path": None,
            "device": self.device,
            "detections": [d.__dict__ for d in detections],
            "counts": counts,
            "note": "Использована эвристика (по зелени) как резерв",
        }


