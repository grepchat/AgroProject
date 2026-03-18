#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с подключением
"""
import socket
import subprocess
import sys
from pathlib import Path

def check_port_listening(port=8000):
    """Проверяет, слушается ли порт"""
    print(f"[*] Проверка порта {port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result == 0:
        print(f"[OK] Порт {port} слушается на localhost")
        return True
    else:
        print(f"[ERROR] Порт {port} НЕ слушается на localhost")
        return False

def check_external_access(port=8000):
    """Проверяет, доступен ли порт извне"""
    print(f"[*] Проверка внешнего доступа к порту {port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('0.0.0.0', port))
    sock.close()
    
    if result == 0:
        print(f"[OK] Порт {port} доступен на 0.0.0.0")
        return True
    else:
        print(f"[ERROR] Порт {port} НЕ доступен на 0.0.0.0")
        return False

def get_local_ip():
    """Получает локальный IP адрес"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def check_firewall_rule():
    """Проверяет наличие правила файрвола"""
    print("[*] Проверка правил файрвола...")
    try:
        result = subprocess.run(
            ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if '8000' in result.stdout or 'AgroVision' in result.stdout:
            print("[OK] Найдено правило файрвола для порта 8000")
            return True
        else:
            print("[!] Правило файрвола для порта 8000 не найдено")
            return False
    except Exception as e:
        print(f"[!] Не удалось проверить файрвол: {e}")
        return None

def check_frontend_exists():
    """Проверяет наличие фронтенда"""
    print("[*] Проверка наличия фронтенда...")
    frontend_dir = Path(__file__).parent.parent / "frontend-agro"
    index_file = frontend_dir / "index.html"
    
    if index_file.exists():
        print(f"[OK] Фронтенд найден: {index_file}")
        return True
    else:
        print(f"[ERROR] Фронтенд НЕ найден: {index_file}")
        return False

def main():
    print("=" * 60)
    print("ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ")
    print("=" * 60)
    print()
    
    # Проверки
    port_ok = check_port_listening(8000)
    ext_ok = check_external_access(8000)
    firewall_ok = check_firewall_rule()
    frontend_ok = check_frontend_exists()
    
    local_ip = get_local_ip()
    
    print()
    print("=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)
    print(f"Локальный IP: {local_ip}")
    print(f"Порт слушается: {'ДА' if port_ok else 'НЕТ'}")
    print(f"Внешний доступ: {'ДА' if ext_ok else 'НЕТ'}")
    print(f"Файрвол настроен: {'ДА' if firewall_ok else 'НЕТ' if firewall_ok is not None else 'НЕИЗВЕСТНО'}")
    print(f"Фронтенд найден: {'ДА' if frontend_ok else 'НЕТ'}")
    print()
    
    if not port_ok:
        print("[!] ПРОБЛЕМА: Сервер не запущен или не слушает порт 8000")
        print("   Решение: Запустите сервер командой:")
        print("   python start_https_server.py")
        print("   или")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    if not ext_ok:
        print("[!] ПРОБЛЕМА: Сервер не принимает внешние подключения")
        print("   Решение: Убедитесь, что сервер запущен с --host 0.0.0.0")
        return
    
    if firewall_ok is False:
        print("[!] ПРОБЛЕМА: Файрвол может блокировать подключения")
        print("   Решение: Запустите fix_firewall.ps1 от администратора")
        print("   или настройте файрвол вручную")
    
    if not frontend_ok:
        print("[!] ПРОБЛЕМА: Фронтенд не найден")
        print("   Решение: Убедитесь, что папка frontend-agro существует")
        return
    
    print("[OK] Все проверки пройдены!")
    print()
    print("Попробуйте открыть:")
    print(f"   На компьютере: http://localhost:8000")
    print(f"   На телефоне: http://{local_ip}:8000")
    print()
    print("Если на телефоне не открывается:")
    print("1. Убедитесь, что телефон и компьютер в одной Wi-Fi сети")
    print("2. Проверьте файрвол (запустите fix_firewall.ps1)")
    print("3. Попробуйте другой браузер на телефоне")
    print("4. Проверьте настройки роутера (AP Isolation)")

if __name__ == "__main__":
    main()

