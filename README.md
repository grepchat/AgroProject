AgroProject — MVP мониторинга растений (Desktop)

Описание
Однодневный демо‑прототип для мониторинга растений в теплицах. Приложение загружает изображение с диска, выполняет анализ готовой моделью YOLO (Ultralytics) и отображает детекции и счётчики в настольном GUI. Результаты можно экспортировать в CSV/JSON для последующей выгрузки на сайт.

Функции MVP
- Загрузка изображения с ПК
- Анализ с YOLOv8 (или эвристический фолбэк, если модель недоступна)
- Визуализация детекций (рамки + подписи)
- Счёт по классам: `healthy`, `dead`, `grade_1`, `grade_2`, `fruit`
- Экспорт результатов в CSV/JSON

Технологический стек
- Python 3.10+
- Ultralytics YOLOv8
- PyQt5
- OpenCV, NumPy, Pandas, Pillow
- Опционально: GPU (CUDA), если установлена CUDA‑сборка PyTorch

Быстрый старт (Windows PowerShell)
1) Создать и активировать виртуальное окружение:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2) Установить зависимости:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```
Опционально (ускорение на GPU): установить CUDA‑сборку PyTorch под вашу версию CUDA, например для CUDA 12.1:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
3) Запуск приложения:
```powershell
python -m app.main
```
4) В интерфейсе загрузите изображение и нажмите Analyze — появятся рамки и счётчики. Кнопкой Export сохраните JSON/CSV в `data/outputs/`.

Модель
- По умолчанию приложение пытается загрузить YOLOv8 модель `yolov8n.pt`. Это COCO‑модель без специализированных классов растений — подходит для демонстрации связки.
- Для целевых классов (`healthy`, `dead`, `grade_1`, `grade_2`, `fruit`) укажите путь к своей модели `.pt` в `app/config.py` (поле `yolo_model_path`) или через переменные окружения `AGRO_YOLO_MODEL` и `AGRO_DEVICE`.
- Если YOLO недоступна или возникает ошибка, запускается эвристический «зелёный» фолбэк (Excess Green + контуры) для демонстрации подсчёта.

Данные
- Поместите тестовые изображения в папку `sample_images/` или выберите файл через GUI во время работы.
- Экспорты сохраняются в `data/outputs/`.

Где взять изображения/датасеты (для демо)
- Roboflow Universe — наборы по запросу «cucumber» (пример: `workspace/project`, выберите YOLOv8 формат).
- Kaggle — «cucumber», «greenhouse top view», «PlantVillage».
- Google Images — снимки теплиц сверху для быстрой демонстрации.

Скрипт загрузки датасетов
Для удобства добавлен `scripts/download_datasets.py` (Kaggle/Roboflow):

1) Установите дополнительные зависимости:
```powershell
pip install kaggle roboflow
```

2) Kaggle: настройте API ключ (скачайте `kaggle.json` в `%USERPROFILE%\.kaggle\kaggle.json`). Затем:
```powershell
python scripts\download_datasets.py kaggle owner/dataset --out data\datasets\kaggle
```

3) Roboflow: передайте ключ или задайте `ROBOFLOW_API_KEY`.
```powershell
# Пример: workspace=my-org, project=cucumber-detection, version=1, формат yolov8
$env:ROBOFLOW_API_KEY="<YOUR_KEY>"
python scripts\download_datasets.py roboflow my-org cucumber-detection 1 --format yolov8 --out data\datasets\roboflow
```

Настройки
- Путь к модели и устройство задаются в `app/config.py` или переменными окружения:
  - `AGRO_YOLO_MODEL` — путь к `.pt`
  - `AGRO_DEVICE` — `cuda` или `cpu`
  - `AGRO_OUTPUT_DIR` — каталог для экспорта (по умолчанию `data/outputs`)

Структура проекта
- `app/main.py` — точка входа (PyQt5)
- `app/gui.py` — главное окно и действия UI
- `app/inference.py` — инференс YOLO + эвристика
- `app/annotator.py` — отрисовка рамок/меток
- `app/io_utils.py` — сохранение JSON/CSV
- `app/config.py` — конфигурация
- `sample_images/` — примеры изображений (опционально)
- `data/outputs/` — результаты (создаются при запуске)

Известные ограничения MVP
- Базовая модель `yolov8n.pt` не распознаёт классы растений из коробки (COCO). Для «здоровое/погибшее/сорт/плоды» нужна специализированная модель.
- Эвристика подсчитывает «зелёные области» и служит для демонстрации, а не для продакшн‑точности.

Дорожная карта (после MVP)
- Пакетная обработка папки для имитации «движения камеры»
- Тепловые карты и карты плотности посадки
- Дообучение модели на тепличных данных (первыми — огурцы)
- Интеграция с оборудованием и управлением рельсовой системой

Лицензия
Демо/внутренняя оценка.


