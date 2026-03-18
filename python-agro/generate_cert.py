#!/usr/bin/env python3
"""
Генерация самоподписанного SSL-сертификата для локальной сети.
Это позволит использовать камеру через HTTPS на мобильных устройствах.
"""
import os
import subprocess
import sys
from pathlib import Path

def generate_cert():
    """Генерирует самоподписанный SSL-сертификат"""
    cert_dir = Path(__file__).parent / "certs"
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # Проверяем, есть ли уже сертификат
    if cert_file.exists() and key_file.exists():
        print("[OK] SSL-сертификат уже существует!")
        print(f"   Сертификат: {cert_file}")
        print(f"   Ключ: {key_file}")
        return str(cert_file), str(key_file)
    
    print("[*] Генерация самоподписанного SSL-сертификата...")
    print("   Это может занять несколько секунд...")
    
    try:
        # Используем OpenSSL через subprocess
        # Генерируем приватный ключ
        subprocess.run([
            "openssl", "genrsa", "-out", str(key_file), "2048"
        ], check=True, capture_output=True)
        
        # Генерируем самоподписанный сертификат
        # Включаем IP адреса для локальной сети
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", str(key_file),
            "-out", str(cert_file), "-days", "365",
            "-subj", "/C=RU/ST=Local/L=Local/O=AgroVision/CN=localhost"
        ], check=True, capture_output=True)
        
        print("[OK] SSL-сертификат успешно создан!")
        print(f"   Сертификат: {cert_file}")
        print(f"   Ключ: {key_file}")
        print("\n[!] ВАЖНО: При первом открытии сайта на телефоне")
        print("   браузер покажет предупреждение о безопасности.")
        print("   Нажмите 'Продолжить' или 'Дополнительно' -> 'Перейти на сайт'")
        
        return str(cert_file), str(key_file)
        
    except subprocess.CalledProcessError as e:
        print("[!] Ошибка при генерации сертификата через OpenSSL")
        print("   Пробую альтернативный метод...")
        return generate_cert_python(cert_file, key_file)
    except FileNotFoundError:
        print("[!] OpenSSL не найден. Использую Python для генерации...")
        return generate_cert_python(cert_file, key_file)

def generate_cert_python(cert_file, key_file):
    """Генерация сертификата через Python (cryptography)"""
    try:
        import ipaddress
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from datetime import datetime, timedelta
        
        # Генерируем приватный ключ
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Создаем самоподписанный сертификат
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AgroVision"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Сохраняем ключ
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Сохраняем сертификат
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print("[OK] SSL-сертификат успешно создан через Python!")
        print(f"   Сертификат: {cert_file}")
        print(f"   Ключ: {key_file}")
        
        return str(cert_file), str(key_file)
        
    except ImportError:
        print("[ERROR] Необходима библиотека cryptography")
        print("   Установите: pip install cryptography")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Ошибка при генерации сертификата: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cert_path, key_path = generate_cert()
    print(f"\n[INFO] Пути к файлам:")
    print(f"   CERT: {cert_path}")
    print(f"   KEY: {key_path}")

