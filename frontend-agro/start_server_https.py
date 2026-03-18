#!/usr/bin/env python3
"""
HTTPS сервер для фронтенда (для работы камеры с телефона).
Требует SSL сертификат. Используйте для доступа к камере с мобильных устройств.
"""
import http.server
import socketserver
import os
import ssl
import socket

PORT = 8443

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Добавляем CORS заголовки для работы с API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def log_message(self, format, *args):
        pass

def create_self_signed_cert():
    """Создает самоподписанный SSL сертификат (только для разработки!)"""
    try:
        import subprocess
        import sys
        
        cert_file = "server.crt"
        key_file = "server.key"
        
        if os.path.exists(cert_file) and os.path.exists(key_file):
            return cert_file, key_file
        
        print("Создание самоподписанного SSL сертификата...")
        # Используем OpenSSL для создания сертификата
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", key_file, "-out", cert_file,
            "-days", "365", "-nodes", "-subj",
            "/C=RU/ST=State/L=City/O=Organization/CN=localhost"
        ], check=True, capture_output=True)
        
        return cert_file, key_file
    except Exception as e:
        print(f"⚠️ Не удалось создать SSL сертификат: {e}")
        print("Установите OpenSSL или используйте HTTP сервер (камера не будет работать)")
        return None, None

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    cert_file, key_file = create_self_signed_cert()
    
    if not cert_file or not key_file:
        print("❌ Не удалось настроить HTTPS. Используйте start_server.py для HTTP.")
        sys.exit(1)
    
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        # Настраиваем SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"=" * 60)
        print(f"🔒 HTTPS сервер запущен!")
        print(f"=" * 60)
        print(f"📱 Откройте на телефоне (для работы камеры):")
        print(f"   https://192.168.1.188:{PORT}")
        print(f"   ⚠️ Браузер покажет предупреждение о сертификате - нажмите 'Продолжить'")
        print(f"")
        print(f"💻 Или на компьютере:")
        print(f"   https://localhost:{PORT}")
        print(f"   https://127.0.0.1:{PORT}")
        print(f"=" * 60)
        print(f"Нажмите Ctrl+C для остановки")
        print(f"=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nСервер остановлен.")

