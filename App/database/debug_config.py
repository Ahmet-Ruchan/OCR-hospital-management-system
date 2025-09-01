import os
from dotenv import load_dotenv

load_dotenv()

print("🔧 Environment Variables Debug:")
print(f"   DB_USER: {os.getenv('DB_USER', 'postgres')}")
print(f"   DB_PASSWORD: {os.getenv('DB_PASSWORD', '123')}")
print(f"   DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
print(f"   DB_PORT: {os.getenv('DB_PORT', '5432')}")
print(f"   DB_NAME: {os.getenv('DB_NAME', 'ocr_hospital_db')}")

# Config'i import et
from App.database.config import config, DATABASE_URI

print(f"\n🔧 Global DATABASE_URI: {DATABASE_URI}")

# Development config test
dev_config = config['development']
print(f"\n🔧 DevelopmentConfig test:")
print(f"   Type: {type(dev_config)}")
print(f"   Has SQLALCHEMY_DATABASE_URI: {hasattr(dev_config, 'SQLALCHEMY_DATABASE_URI')}")

if hasattr(dev_config, 'SQLALCHEMY_DATABASE_URI'):
    print(f"   Database URI: {dev_config.SQLALCHEMY_DATABASE_URI}")
    print(f"   Debug: {dev_config.DEBUG}")
else:
    print("   ❌ SQLALCHEMY_DATABASE_URI attribute bulunamadı!")
    print(f"   Available attributes: {[attr for attr in dir(dev_config) if not attr.startswith('_')]}")