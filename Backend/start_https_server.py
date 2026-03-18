#!/usr/bin/env python3
"""
Запуск FastAPI сервера с HTTPS (для работы камеры на мобильных устройствах)
"""
import os
import sys
from pathlib import Path

def main():
    cert_dir = Path(__file__).parent / "certs"
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # Проверяем наличие сертификата
    if not cert_file.exists() or not key_file.exists():
        print("❌ SSL-сертификат не найден!")
        print("   Сначала запустите: python generate_cert.py")
        sys.exit(1)
    
    print("[*] Запуск FastAPI сервера с HTTPS...")
    print(f"   Сертификат: {cert_file}")
    print(f"   Ключ: {key_file}")
    print("\n[INFO] Теперь фронтенд и API на одном сервере!")
    print("   Не нужно запускать отдельный фронтенд-сервер.")
    print("\n[MOBILE] Откройте на телефоне:")
    print("   https://192.168.1.188:8000")
    print("\n[PC] Или на компьютере:")
    print("   https://localhost:8000")
    print("   https://127.0.0.1:8000")
    print("\n[!] ВАЖНО: При первом открытии браузер покажет предупреждение")
    print("   о безопасности. Нажмите 'Продолжить' или")
    print("   'Дополнительно' -> 'Перейти на сайт (небезопасно)'")
    print("\n" + "="*60)
    
    # Запускаем uvicorn с SSL
    os.chdir(Path(__file__).parent)
    os.system(
        f'uvicorn app.main:app --host 0.0.0.0 --port 8000 '
        f'--ssl-keyfile "{key_file}" --ssl-certfile "{cert_file}" --reload'
    )

if __name__ == "__main__":
    main()

