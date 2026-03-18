import os
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split

# Маппинг классов в индексы
CLASS_MAP = {
    "daisy": 0,
    "dandelion": 1,
    "rose": 2,
    "sunflower": 3,
    "tulip": 4,
}

# Папки исходного датасета
DATA_ROOT = Path(".")
TRAIN_DIR = DATA_ROOT / "train"

# Папка для нового YOLO-датасета
OUT_ROOT = DATA_ROOT / "datasets" / "flowers_yolo"
IMG_TRAIN = OUT_ROOT / "images" / "train"
IMG_VAL = OUT_ROOT / "images" / "val"
LBL_TRAIN = OUT_ROOT / "labels" / "train"
LBL_VAL = OUT_ROOT / "labels" / "val"

def ensure_dirs():
    for p in [IMG_TRAIN, IMG_VAL, LBL_TRAIN, LBL_VAL]:
        p.mkdir(parents=True, exist_ok=True)

def collect_images():
    """Собираем список (путь к картинке, класс_id)."""
    samples = []
    for class_name, class_id in CLASS_MAP.items():
        class_dir = TRAIN_DIR / class_name
        for img_path in class_dir.glob("*.*"):
            if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                continue
            samples.append((img_path, class_id))
    return samples

def split_train_val(samples, val_size=0.2, random_state=42):
    paths = [s[0] for s in samples]
    labels = [s[1] for s in samples]
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        paths, labels, test_size=val_size, random_state=random_state, stratify=labels
    )
    train_samples = list(zip(train_paths, train_labels))
    val_samples = list(zip(val_paths, val_labels))
    return train_samples, val_samples

def copy_and_create_label(samples, img_out_dir, lbl_out_dir):
    for img_path, class_id in samples:
        # имя файла
        new_name = img_path.name
        dst_img = img_out_dir / new_name
        dst_lbl = lbl_out_dir / (img_path.stem + ".txt")

        # копируем картинку
        shutil.copy2(img_path, dst_img)

        # создаём YOLO-разметку: один bbox = весь кадр
        # class cx cy w h (нормализованные коорды)
        yolo_line = f"{class_id} 0.5 0.5 1.0 1.0\n"
        with open(dst_lbl, "w", encoding="utf-8") as f:
            f.write(yolo_line)

def create_yaml():
    yaml_path = OUT_ROOT / "flowers_yolo.yaml"
    content = f"""path: {OUT_ROOT.as_posix()}
train: images/train
val: images/val

names:
  0: daisy
  1: dandelion
  2: rose
  3: sunflower
  4: tulip
"""
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Создан файл {yaml_path}")

def main():
    ensure_dirs()
    samples = collect_images()
    print(f"Всего картинок: {len(samples)}")
    train_samples, val_samples = split_train_val(samples)

    print(f"Train: {len(train_samples)}, Val: {len(val_samples)}")

    copy_and_create_label(train_samples, IMG_TRAIN, LBL_TRAIN)
    copy_and_create_label(val_samples, IMG_VAL, LBL_VAL)
    create_yaml()
    print("Готово!")

if __name__ == "__main__":
    main()
