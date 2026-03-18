#!/usr/bin/env python3
"""
Простой запуск сервера БЕЗ HTTPS (для тестирования)
Используйте этот скрипт, если HTTPS не нужен или вызывает проблемы
"""
import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("[*] Запуск FastAPI сервера (БЕЗ HTTPS)")
    print("=" * 60)
    print()
    print("[INFO] Теперь фронтенд и API на одном сервере!")
    print("   Не нужно запускать отдельный фронтенд-сервер.")
    print()
    
    # Получаем IP адрес
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '192.168.1.188'
    finally:
        s.close()
    
    print("[MOBILE] Откройте на телефоне:")
    print(f"   http://{local_ip}:8000")
    print()
    print("[PC] Или на компьютере:")
    print("   http://localhost:8000")
    print("   http://127.0.0.1:8000")
    print()
    print("[!] ВАЖНО: Камера на мобильных устройствах НЕ будет работать")
    print("   без HTTPS. Для камеры используйте start_https_server.py")
    print()
    print("=" * 60)
    print()
    
    # Запускаем uvicorn БЕЗ SSL, но с --host 0.0.0.0
    os.chdir(Path(__file__).parent)
    os.system(
        'uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'
    )

if __name__ == "__main__":
    main()

