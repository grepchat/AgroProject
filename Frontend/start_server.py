#!/usr/bin/env python3
"""
Простой HTTP сервер для фронтенда.
Запускает сайт на всех интерфейсах, чтобы можно было открыть с телефона.
"""
import http.server
import socketserver
import os

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

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        print(f"=" * 60)
        print(f"🌐 HTTP сервер запущен!")
        print(f"=" * 60)
        print(f"📱 Откройте на телефоне:")
        print(f"   http://192.168.1.188:{PORT}")
        print(f"")
        print(f"💻 Или на компьютере:")
        print(f"   http://localhost:{PORT}")
        print(f"   http://127.0.0.1:{PORT}")
        print(f"=" * 60)
        print(f"⚠️  ВАЖНО: Камера не будет работать по HTTP!")
        print(f"   Для работы камеры используйте HTTPS сервер:")
        print(f"   python start_server_https.py")
        print(f"=" * 60)
        print(f"Нажмите Ctrl+C для остановки")
        print(f"=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nСервер остановлен.")

