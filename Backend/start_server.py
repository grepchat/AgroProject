#!/usr/bin/env python3
"""
Запуск FastAPI сервера БЕЗ HTTPS (для быстрого тестирования)
Для работы камеры на мобильных устройствах используйте start_https_server.py
"""
import os
import sys
from pathlib import Path

def main():
    print("[*] Запуск FastAPI сервера БЕЗ HTTPS...")
    print("\n[INFO] Теперь фронтенд и API на одном сервере!")
    print("   Не нужно запускать отдельный фронтенд-сервер.")
    print("\n[MOBILE] Откройте на телефоне:")
    print("   http://192.168.1.188:8000")
    print("\n[PC] Или на компьютере:")
    print("   http://localhost:8000")
    print("   http://127.0.0.1:8000")
    print("\n[!] ВНИМАНИЕ: Камера на мобильных устройствах")
    print("   может не работать без HTTPS!")
    print("\n" + "="*60)
    
    # Запускаем uvicorn БЕЗ SSL
    os.chdir(Path(__file__).parent)
    os.system(
        'uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'
    )

if __name__ == "__main__":
    main()

