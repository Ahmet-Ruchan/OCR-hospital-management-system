"""
DOSYA: utils/config.py
AMAÇ: Uygulama konfigürasyon yönetimi

AÇIKLAMA:
- .env dosyasından konfigürasyonları okur
- Varsayılan değerleri yönetir
- Konfigürasyon validasyonu yapar
- Farklı ortamlar için ayarları düzenler

KULLANIM:
    from utils.config import Config
    pdf_folder = Config.PDF_FOLDER
    db_url = Config.get_database_url()
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class Config:
    """
    SINIF: Config
    AMAÇ: Merkezi konfigürasyon yönetimi sınıfı

    Tüm uygulama ayarları bu sınıftan okunur.
    Environment variable'lar yoksa varsayılan değerler kullanılır.
    """

    # ============ FLASK AYARLARI ============
    # Flask framework konfigürasyonları
    FLASK_APP = os.getenv('FLASK_APP', 'main.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))

    # ============ API AYARLARI ============
    # REST API konfigürasyonları
    API_VERSION = os.getenv('API_VERSION', 'v1')
    API_KEY = os.getenv('API_KEY', 'default-api-key')
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', 100))
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 300))

    # ============ VERİTABANI AYARLARI ============
    # PostgreSQL bağlantı bilgileri
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'ocr_hospital_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 20))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 40))

    # ============ REDIS AYARLARI ============
    # Redis cache ve queue konfigürasyonları
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_MAX_CONNECTIONS = int(os.getenv('REDIS_MAX_CONNECTIONS', 50))

    # ============ DOSYA YOLU AYARLARI ============
    # Dosya ve klasör yolları
    PDF_FOLDER = os.getenv('PDF_FOLDER', '/mnt/shared/pdfs')
    TEMP_FOLDER = os.getenv('TEMP_FOLDER', '/tmp/ocr_temp')
    LOG_FOLDER = os.getenv('LOG_FOLDER', './logs')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')

    # ============ DOSYA LİMİTLERİ ============
    # Dosya boyutu ve uzantı kısıtlamaları
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))  # 50 MB
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', '.pdf,.jpg,.jpeg,.png').split(',')

    # ============ OCR AYARLARI ============
    # OCR motoru konfigürasyonları
    OCR_LANGUAGES = os.getenv('OCR_LANGUAGES', 'tr,en').split(',')
    OCR_GPU_ENABLED = os.getenv('OCR_GPU_ENABLED', 'True').lower() == 'true'
    OCR_OPTIMIZATION = os.getenv('OCR_OPTIMIZATION', 'True').lower() == 'true'
    OCR_DPI = int(os.getenv('OCR_DPI', 100))
    OCR_CROP_RATIO = float(os.getenv('OCR_CROP_RATIO', 0.5))
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv('OCR_CONFIDENCE_THRESHOLD', 0.5))

    # ============ PERFORMANS AYARLARI ============
    # Sistem performans parametreleri
    WORKER_THREADS = int(os.getenv('WORKER_THREADS', 4))
    WORKER_TIMEOUT = int(os.getenv('WORKER_TIMEOUT', 300))
    QUEUE_MAX_SIZE = int(os.getenv('QUEUE_MAX_SIZE', 300))
    CACHE_TTL = int(os.getenv('CACHE_TTL', 86400))  # 24 saat

    # ============ GÜVENLİK AYARLARI ============
    # Güvenlik ve CORS konfigürasyonları
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    # ============ LOG AYARLARI ============
    # Loglama konfigürasyonları
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')
    LOG_FILE = os.getenv('LOG_FILE', 'ocr_system.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))  # 10 MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

    @classmethod
    def get_database_url(cls) -> str:
        """
        PostgreSQL bağlantı URL'ini oluştur

        DÖNEN DEĞER:
            str: PostgreSQL connection string

        ÖRNEK:
            postgresql://user:password@localhost:5432/dbname
        """
        # Önce DATABASE_URL environment variable'ı kontrol et
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            return db_url

        # Yoksa parçalardan oluştur
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def get_redis_url(cls) -> str:
        """
        Redis bağlantı URL'ini oluştur

        DÖNEN DEĞER:
            str: Redis connection string

        ÖRNEK:
            storage://:password@localhost:6379/0
        """
        if cls.REDIS_PASSWORD:
            return f"storage://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        else:
            return f"storage://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"

    @classmethod
    def validate_config(cls) -> bool:
        """
        Konfigürasyon değerlerini doğrula

        DÖNEN DEĞER:
            bool: Konfigürasyon geçerli mi?

        KONTROLLER:
            - Kritik değerlerin varlığı
            - Dosya yollarının geçerliliği
            - Port numaralarının uygunluğu
        """
        errors = []

        # Secret key kontrolü
        if cls.SECRET_KEY == 'dev-secret-key' and cls.FLASK_ENV == 'production':
            errors.append("❌ Production'da SECRET_KEY değiştirilmeli!")

        # API key kontrolü
        if cls.API_KEY == 'default-api-key' and cls.FLASK_ENV == 'production':
            errors.append("❌ Production'da API_KEY değiştirilmeli!")

        # Port kontrolü
        if not 1 <= cls.PORT <= 65535:
            errors.append(f"❌ Geçersiz port numarası: {cls.PORT}")

        # Klasör kontrolleri
        required_folders = [cls.TEMP_FOLDER, cls.LOG_FOLDER, cls.UPLOAD_FOLDER]
        for folder in required_folders:
            path = Path(folder)
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Klasör oluşturuldu: {folder}")
                except Exception as e:
                    errors.append(f"❌ Klasör oluşturulamadı: {folder} - {e}")

        # PDF klasörü erişim kontrolü
        pdf_path = Path(cls.PDF_FOLDER)
        if not pdf_path.exists():
            errors.append(f"⚠️ PDF klasörü bulunamadı: {cls.PDF_FOLDER}")

        # Hata varsa göster
        if errors:
            print("\n🚨 KONFİGÜRASYON HATALARI:")
            for error in errors:
                print(f"  {error}")
            return False

        return True

    @classmethod
    def print_config(cls):
        """
        Mevcut konfigürasyonu konsola yazdır (Debug için)
        Hassas bilgileri maskeler
        """
        print("\n" + "=" * 60)
        print("📋 UYGULAMA KONFİGÜRASYONU")
        print("=" * 60)

        print("\n🔧 Flask Ayarları:")
        print(f"  • Environment: {cls.FLASK_ENV}")
        print(f"  • Debug: {cls.DEBUG}")
        print(f"  • Host: {cls.HOST}:{cls.PORT}")

        print("\n🗄️ Veritabanı:")
        print(f"  • PostgreSQL: {cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
        print(f"  • Kullanıcı: {cls.DB_USER}")
        print(f"  • Şifre: {'*' * len(cls.DB_PASSWORD) if cls.DB_PASSWORD else 'YOK'}")

        print("\n📦 Redis:")
        print(f"  • Host: {cls.REDIS_HOST}:{cls.REDIS_PORT}")
        print(f"  • DB: {cls.REDIS_DB}")

        print("\n📁 Dosya Yolları:")
        print(f"  • PDF Klasörü: {cls.PDF_FOLDER}")
        print(f"  • Temp Klasörü: {cls.TEMP_FOLDER}")
        print(f"  • Log Klasörü: {cls.LOG_FOLDER}")

        print("\n🔍 OCR Ayarları:")
        print(f"  • Diller: {', '.join(cls.OCR_LANGUAGES)}")
        print(f"  • GPU: {'Aktif' if cls.OCR_GPU_ENABLED else 'Kapalı'}")
        print(f"  • DPI: {cls.OCR_DPI}")

        print("=" * 60 + "\n")


# Uygulama başlarken konfigürasyonu doğrula
if __name__ != "__main__":
    if Config.validate_config():
        print("✅ Konfigürasyon başarıyla yüklendi")
    else:
        print("⚠️ Konfigürasyon hataları var, devam ediliyor...")