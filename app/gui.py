from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from .annotator import draw_detections
from .config import CONFIG
from .inference import InferenceEngine
from .io_utils import ensure_dir, save_csv, save_json, timestamp


def np_to_qimage(image_bgr: np.ndarray) -> QtGui.QImage:
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = image_rgb.shape
    bytes_per_line = ch * w
    return QtGui.QImage(
        image_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888
    ).copy()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AgroProject — Мониторинг растений (MVP)")
        self.resize(1200, 800)

        # State
        self.current_image_bgr: Optional[np.ndarray] = None
        self.last_result: Optional[Dict[str, Any]] = None
        ensure_dir(CONFIG.output_dir)

        # Inference engine
        self.engine = InferenceEngine()

        # UI
        self._init_ui()

    def _init_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)

        # Информация о статусе
        self.status_label = QtWidgets.QLabel(self.engine.yolo_status())
        layout.addWidget(self.status_label)

        # Image display
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(480)
        self.image_label.setStyleSheet("background-color: #222; color: #ddd;")
        layout.addWidget(self.image_label, stretch=1)

        # Controls
        controls = QtWidgets.QHBoxLayout()
        layout.addLayout(controls)

        self.btn_load = QtWidgets.QPushButton("Загрузить изображение…")
        self.btn_load.clicked.connect(self.on_load_image)
        controls.addWidget(self.btn_load)

        self.btn_analyze = QtWidgets.QPushButton("Анализ")
        self.btn_analyze.clicked.connect(self.on_analyze)
        self.btn_analyze.setEnabled(False)
        controls.addWidget(self.btn_analyze)

        self.btn_export_json = QtWidgets.QPushButton("Экспорт JSON")
        self.btn_export_json.clicked.connect(self.on_export_json)
        self.btn_export_json.setEnabled(False)
        controls.addWidget(self.btn_export_json)

        self.btn_export_csv = QtWidgets.QPushButton("Экспорт CSV")
        self.btn_export_csv.clicked.connect(self.on_export_csv)
        self.btn_export_csv.setEnabled(False)
        controls.addWidget(self.btn_export_csv)

        controls.addStretch(1)

        # Таблица счётчиков
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Класс", "Количество"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setFixedHeight(180)
        layout.addWidget(self.table)

    # --- Slots ---
    def on_load_image(self) -> None:
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите изображение", os.getcwd(), "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if not fname:
            return

        image_bgr = cv2.imread(fname, cv2.IMREAD_COLOR)
        if image_bgr is None:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
            return

        self.current_image_bgr = image_bgr
        self.last_result = None
        self._display_image(image_bgr)
        self._set_actions_enabled(analyze=True, export=False)

    def on_analyze(self) -> None:
        if self.current_image_bgr is None:
            return
        try:
            result = self.engine.analyze_image(self.current_image_bgr)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка инференса", str(e))
            return

        self.last_result = result

        detections: List[dict] = result.get("detections", [])
        annotated = draw_detections(self.current_image_bgr, detections)
        self._display_image(annotated)

        counts = result.get("counts", {})
        self._populate_table(counts)
        self._set_actions_enabled(analyze=True, export=True)

    def on_export_json(self) -> None:
        if not self.last_result:
            return
        base = f"result_{timestamp()}"
        out = save_json(self.last_result, CONFIG.output_dir, base)
        self.statusBar().showMessage(f"Сохранено: {out}", 5000)

    def on_export_csv(self) -> None:
        if not self.last_result:
            return
        base = f"result_{timestamp()}"
        rows = self._rows_for_csv(self.last_result)
        out = save_csv(rows, CONFIG.output_dir, base)
        self.statusBar().showMessage(f"Сохранено: {out}", 5000)

    # --- Helpers ---
    def _display_image(self, image_bgr: np.ndarray) -> None:
        qimg = np_to_qimage(image_bgr)
        pix = QtGui.QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pix.scaled(
            self.image_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation
        ))

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self.current_image_bgr is not None:
            # Re-render current pixmap to fit label
            showing = self.image_label.pixmap()
            if showing is not None:
                self._display_image(self.current_image_bgr if self.last_result is None else draw_detections(self.current_image_bgr, self.last_result.get("detections", [])))

    def _populate_table(self, counts: Dict[str, int]) -> None:
        items = sorted(counts.items(), key=lambda x: x[0])
        self.table.setRowCount(len(items))
        for i, (cls_name, cnt) in enumerate(items):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(cls_name)))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(cnt)))

    def _rows_for_csv(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        detections = result.get("detections", [])
        for det in detections:
            row = {
                "engine": result.get("engine"),
                "class_name": det.get("class_name"),
                "score": det.get("score"),
                "x1": det.get("bbox", [None, None, None, None])[0],
                "y1": det.get("bbox", [None, None, None, None])[1],
                "x2": det.get("bbox", [None, None, None, None])[2],
                "y2": det.get("bbox", [None, None, None, None])[3],
            }
            rows.append(row)
        # If there are no detections, still write aggregates
        if not rows:
            for k, v in (result.get("counts") or {}).items():
                rows.append({"engine": result.get("engine"), "class_name": k, "score": None, "x1": None, "y1": None, "x2": None, "y2": None, "count": v})
        return rows

    def _set_actions_enabled(self, analyze: bool, export: bool) -> None:
        self.btn_analyze.setEnabled(analyze)
        self.btn_export_json.setEnabled(export)
        self.btn_export_csv.setEnabled(export)


