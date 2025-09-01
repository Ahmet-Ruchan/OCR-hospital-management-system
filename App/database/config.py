import os
from dotenv import load_dotenv

load_dotenv()

# Local Windows uyumlu varsayılanlar
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123')
DB_HOST = os.getenv('DB_HOST', 'localhost')  # ← localhost varsayılan
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ocr_hospital_db')

# Database URI (Local'e uygun)
DATABASE_URI = os.environ.get('DATABASE_URL', f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
print(f"🔧 Database URI: {DATABASE_URI}")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    # SQLAlchemy ayarları
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Connection pool ayarları (Local için)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 5,  # Local için daha düşük
        'pool_size': 3      # Local için daha düşük
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    TESTING = False

    # Production için daha yüksek connection pool
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 20,
        'pool_size': 10
    }

class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    TESTING = True

    # Test için ayrı database (Docker uyumlu)
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test"

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}