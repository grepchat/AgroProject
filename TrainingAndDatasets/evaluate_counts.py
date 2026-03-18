import argparse
import os
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from ultralytics import YOLO


def load_data_paths(data_yaml: Path, split: str = "val") -> Tuple[Path, Path]:
    """
    Читает YAML (как flowers_yolo.yaml) и возвращает:
    - путь к images/<split>
    - путь к labels/<split>
    """
    with open(data_yaml, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    base = Path(cfg["path"])
    images_rel = cfg.get(split, "images/val")
    images_dir = base / images_rel
    labels_dir = base / "labels" / split

    if not images_dir.is_dir():
        raise FileNotFoundError(f"Папка с картинками не найдена: {images_dir}")
    if not labels_dir.is_dir():
        raise FileNotFoundError(f"Папка с разметкой не найдена: {labels_dir}")

    return images_dir, labels_dir


def count_gt_objects(label_path: Path) -> int:
    """
    Считает количество строк в .txt файле YOLO-разметки.
    Если файла нет — считаем, что GT = 0.
    """
    if not label_path.is_file():
        return 0
    with open(label_path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]
    return len(lines)


def evaluate_counts(
    weights: Path,
    data_yaml: Path,
    split: str = "val",
    imgsz: int = 640,
    conf: float = 0.25,
    iou: float = 0.45,
    device: str = "",
) -> None:
    """
    Основная функция:
    - грузит модель
    - прогоняет по валидационным картинкам
    - считает MAE и MAPE по количеству объектов.
    """

    print(f"[INFO] Загрузка конфига датасета из {data_yaml} (split='{split}')")
    images_dir, labels_dir = load_data_paths(data_yaml, split=split)
    print(f"[INFO] images_dir = {images_dir}")
    print(f"[INFO] labels_dir = {labels_dir}")

    # собираем список картинок
    exts = (".jpg", ".jpeg", ".png", ".bmp")
    image_paths: List[Path] = sorted(
        [p for p in images_dir.rglob("*") if p.suffix.lower() in exts]
    )

    if not image_paths:
        raise RuntimeError(f"Не найдено ни одной картинки в {images_dir}")

    print(f"[INFO] Найдено {len(image_paths)} изображений для оценки")

    # считаем GT количество объектов
    gt_counts: Dict[Path, int] = {}
    for img_path in image_paths:
        rel_stem = img_path.stem
        label_path = labels_dir / f"{rel_stem}.txt"
        gt_counts[img_path] = count_gt_objects(label_path)

    # загружаем модель
    print(f"[INFO] Загрузка модели из весов: {weights}")
    model = YOLO(str(weights))

    print(
        f"[INFO] Запуск предсказания: imgsz={imgsz}, conf={conf}, iou={iou}, device='{device or 'auto'}'"
    )

    # Прогоняем модель по всем картинкам пачками
    results = model.predict(
        source=str(images_dir),
        imgsz=imgsz,
        conf=conf,
        iou=iou,
        device=device or None,
        stream=True,  # чтобы не кушать всю память
        verbose=False,
    )

    per_image_stats = []  # список кортежей (имя, gt, pred, diff)

    # словарь: путь -> pred_count
    pred_counts: Dict[Path, int] = {}

    for res in results:
        # res.path: полный путь к исходному файлу
        img_path = Path(res.path)
        # количество боксов после NMS
        n_pred = len(res.boxes) if res.boxes is not None else 0
        pred_counts[img_path] = n_pred

    # теперь считаем метрики
    abs_diffs: List[float] = []
    abs_rel_errors: List[float] = []  # для MAPE (по тем, где gt > 0)

    for img_path in image_paths:
        gt = gt_counts.get(img_path, 0)
        pred = pred_counts.get(img_path, 0)
        diff = pred - gt
        abs_diff = abs(diff)
        abs_diffs.append(abs_diff)

        if gt > 0:
            abs_rel = abs_diff / gt
            abs_rel_errors.append(abs_rel)

        per_image_stats.append((img_path.name, gt, pred, diff))

    n = len(image_paths)
    mae = sum(abs_diffs) / n if n > 0 else float("nan")

    if abs_rel_errors:
        mape = (sum(abs_rel_errors) / len(abs_rel_errors)) * 100.0
    else:
        mape = float("nan")

    print("\n=== РЕЗУЛЬТАТЫ ПО КОЛИЧЕСТВУ (COUNT) ===")
    print(f"Всего изображений: {n}")
    print(f"MAE (средняя абсолютная ошибка по count): {mae:.3f}")
    if abs_rel_errors:
        print(f"MAPE (средняя относительная ошибка по count, %): {mape:.2f}%")
    else:
        print("MAPE: нет изображений с GT > 0 (деление на ноль)")

    # показываем несколько примеров
    print("\nПримеры (первые 15 изображений):")
    print(f"{'image':40s} {'gt':>5s} {'pred':>5s} {'diff':>6s}")
    print("-" * 60)
    for name, gt, pred, diff in per_image_stats[:15]:
        print(f"{name:40s} {gt:5d} {pred:5d} {diff:6d}")

    # если хочешь, можно сохранить подробный отчёт в CSV
    out_csv = weights.parent / "count_eval.csv"
    try:
        import csv

        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["image", "gt_count", "pred_count", "diff"])
            for name, gt, pred, diff in per_image_stats:
                writer.writerow([name, gt, pred, diff])
        print(f"\nДетальный отчёт сохранён в {out_csv}")
    except Exception as e:
        print(f"[WARN] Не удалось сохранить CSV-отчёт: {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Оценка точности подсчёта объектов (count) для YOLO-модели"
    )
    parser.add_argument(
        "--weights",
        type=str,
        required=True,
        help="Путь к весам модели (например, runs/detect/train/weights/best.pt)",
    )
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Путь к data.yaml (например, datasets/flowers_yolo/flowers_yolo.yaml)",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="val",
        help="Сплит для оценки (обычно 'val')",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Размер входа (imgsz) для инференса",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Порог по confidence для детекций",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.45,
        help="IoU-порог для NMS",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="",
        help="Устройство: '' (auto), 'cpu', '0' (GPU) и т.п.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    weights_path = Path(args.weights)
    data_yaml_path = Path(args.data)

    if not weights_path.is_file():
        raise FileNotFoundError(f"Файл весов не найден: {weights_path}")
    if not data_yaml_path.is_file():
        raise FileNotFoundError(f"data.yaml не найден: {data_yaml_path}")

    evaluate_counts(
        weights=weights_path,
        data_yaml=data_yaml_path,
        split=args.split,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        device=args.device,
    )
