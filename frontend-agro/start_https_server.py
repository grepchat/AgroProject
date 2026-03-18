#!/usr/bin/env python3
"""
Запуск фронтенд-сервера с HTTPS (для работы камеры на мобильных устройствах)
"""
import http.server
import socketserver
import ssl
import os
import sys
from pathlib import Path

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Добавляем CORS заголовки для работы с API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def log_message(self, format, *args):
        # Упрощенное логирование
        pass

def main():
    # Ищем сертификат в родительской папке python-agro
    cert_dir = Path(__file__).parent.parent / "python-agro" / "certs"
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    if not cert_file.exists() or not key_file.exists():
        print("❌ SSL-сертификат не найден!")
        print("   Сначала запустите: python generate_cert.py (в папке python-agro)")
        sys.exit(1)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        # Настраиваем SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(cert_file), str(key_file))
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"=" * 60)
        print(f"🔐 Фронтенд сервер запущен с HTTPS!")
        print(f"=" * 60)
        print(f"📱 Откройте на телефоне:")
        print(f"   https://192.168.1.188:{PORT}")
        print(f"")
        print(f"💻 Или на компьютере:")
        print(f"   https://localhost:{PORT}")
        print(f"   https://127.0.0.1:{PORT}")
        print(f"=" * 60)
        print(f"⚠️  При первом открытии браузер покажет предупреждение")
        print(f"   о безопасности. Нажмите 'Продолжить' или")
        print(f"   'Дополнительно' → 'Перейти на сайт (небезопасно)'")
        print(f"=" * 60)
        print(f"Нажмите Ctrl+C для остановки")
        print(f"=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nСервер остановлен.")

if __name__ == "__main__":
    main()

