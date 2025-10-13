from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def download_kaggle(dataset: str, out_dir: str) -> str:
    """Download a Kaggle dataset by slug "owner/dataset" and unzip to out_dir.

    Requires: kaggle API configured (~/.kaggle/kaggle.json with API token).
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except Exception as e:
        raise RuntimeError(
            "Библиотека kaggle не установлена. Установите: pip install kaggle"
        ) from e

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as e:
        raise RuntimeError(
            "Не удалось аутентифицироваться в Kaggle. Проверьте ~/.kaggle/kaggle.json"
        ) from e

    ensure_dir(out_dir)
    api.dataset_download_files(dataset, path=out_dir, unzip=True)
    return str(Path(out_dir).resolve())


def download_roboflow(
    workspace: str,
    project: str,
    version: int,
    fmt: str,
    api_key: str | None,
    out_root: str,
) -> str:
    """Download a Roboflow dataset using the official SDK.

    Requires: roboflow API key in argument or ROBOFLOW_API_KEY env var.
    """
    key = api_key or os.getenv("ROBOFLOW_API_KEY")
    if not key:
        raise RuntimeError(
            "Не задан ROBOFLOW_API_KEY. Передайте --api-key или задайте переменную окружения."
        )
    try:
        from roboflow import Roboflow
    except Exception as e:
        raise RuntimeError(
            "Библиотека roboflow не установлена. Установите: pip install roboflow"
        ) from e

    rf = Roboflow(api_key=key)
    ws = rf.workspace(workspace)
    proj = ws.project(project)
    ver = proj.version(version)
    ensure_dir(out_root)
    dataset_dir = ver.download(fmt, location=out_root)
    return str(Path(dataset_dir).resolve())


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Скрипт загрузки датасетов (Kaggle, Roboflow) для AgroProject",
    )
    sub = p.add_subparsers(dest="provider", required=True)

    pk = sub.add_parser("kaggle", help="Скачать датасет с Kaggle")
    pk.add_argument("dataset", help="Идентификатор в формате owner/dataset")
    pk.add_argument(
        "--out",
        default=str(Path("data/datasets/kaggle").as_posix()),
        help="Каталог для распаковки (по умолчанию data/datasets/kaggle)",
    )

    pr = sub.add_parser("roboflow", help="Скачать датасет с Roboflow")
    pr.add_argument("workspace", help="workspace (организация) в Roboflow")
    pr.add_argument("project", help="project (slug) в Roboflow")
    pr.add_argument("version", type=int, help="версия датасета (число)")
    pr.add_argument(
        "--format",
        default="yolov8",
        help="формат экспорта (например, yolov5, yolov8, coco, voc)",
    )
    pr.add_argument(
        "--api-key",
        default=None,
        help="Roboflow API key (или используйте переменную окружения ROBOFLOW_API_KEY)",
    )
    pr.add_argument(
        "--out",
        default=str(Path("data/datasets/roboflow").as_posix()),
        help="Корневой каталог для загрузки (по умолчанию data/datasets/roboflow)",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.provider == "kaggle":
        out = download_kaggle(args.dataset, args.out)
        print(f"Kaggle датасет скачан в: {out}")
        return 0

    if args.provider == "roboflow":
        out = download_roboflow(
            workspace=args.workspace,
            project=args.project,
            version=args.version,
            fmt=args.format,
            api_key=args.api_key,
            out_root=args.out,
        )
        print(f"Roboflow датасет скачан в: {out}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


