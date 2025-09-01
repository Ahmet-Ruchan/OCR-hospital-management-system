"""
DOSYA: main.py
...
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from App.database.config import config
from App.database.db_manager import setup_database
from flask import Flask, jsonify

try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️ Flask-CORS not available, continuing without CORS")
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# API Blueprint'leri import et
from App.api.ocr_api import ocr_blueprint

load_dotenv()

def create_app():

    app = Flask(__name__)

    config_name = os.getenv('FLASK_ENV', 'development')
    print(f"📋 Config Environment: {config_name}")

    try:
        app.config.from_object(config[config_name])
        print(f"✅ Config yüklendi: {config[config_name].__name__}")
    except KeyError:
        print(f"⚠️ Geçersiz config: {config_name}, default kullanılıyor")
        app.config.from_object(config['default'])

    try:
        setup_database(app)
        print(f"✅ Database entegrasyonu tamamlandı")
    except Exception as e:
        print(f"❌ Database setup hatası: {e}")
        print(f"⚠️ Uygulama database olmadan devam ediyor")

    # ============ UYGULAMA YAPILANDIRMASI ============
    # Gizli anahtar (session ve güvenlik için)
    #app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # JSON ayarları
    #app.config['JSON_AS_ASCII'] = False  # Türkçe karakterler için
    #app.config['JSON_SORT_KEYS'] = False  # Key'leri sıralama

    # Upload ayarları
    #app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Maksimum 50 MB

    # Debug modu (production'da False olmalı)
    #app.config['DEBUG'] = os.getenv('FLASK_ENV', 'development') == 'development'

    # ============ CORS YAPILANDIRMASI ============
    # Cross-Origin Resource Sharing - C# client'ın API'ye erişmesi için

    if CORS_AVAILABLE:
        CORS(app, resources={
            r"/api/*": {
                "origins": ["*"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
                "expose_headers": ["Content-Type", "X-Total-Count"],
                "supports_credentials": True,
                "max_age": 3600
            }
        })
        print("✅ CORS enabled")
    else:
        print("ℹ️ CORS disabled (not needed for Docker)")

    # ============ BLUEPRINT KAYDI ============
    try:
        # Sync OCR API
        app.register_blueprint(ocr_blueprint, url_prefix='/api/v1')
        print("✅ Sync OCR Blueprint kaydedildi")

    except Exception as e:
        print(f"❌ Blueprint kayıt hatası: {e}")
        import traceback
        traceback.print_exc()

    # ============ ANA ROUTE'LAR ============
    @app.route('/')
    def index():
        """Ana sayfa - API bilgileri ve sistem durumu"""

        # Sistem durumlarını kontrol et
        redis_status = app.config.get('REDIS_AVAILABLE', False)
        async_status = app.config.get('ASYNC_PROCESSING', False)
        queue_manager = app.config.get('QUEUE_MANAGER', None)

        return jsonify({
            'name': 'OCR Hospital Management System',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'endpoints': {
                'api': '/api/v1',
                'sync_ocr': '/api/v1/ocr/process',
                'swagger': '/api/v1/swagger',
                'health': '/health',
            },
            'description': 'Hastane yönetim sistemi için OCR servisi',
            'features': {
                'sync_processing': True,
            }
        })

    @app.route('/health')
    def health():

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })

    # ============ ERROR HANDLER'LAR ============
    @app.errorhandler(404)
    def not_found(error):
        """
        404 Not Found hatası için özel handler
        """
        return jsonify({
            'success': False,
            'error': 'Endpoint bulunamadı',
            'status_code': 404,
            'timestamp': datetime.now().isoformat()
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """
        500 Internal Server Error için özel handler
        """
        return jsonify({
            'success': False,
            'error': 'Sunucu hatası',
            'status_code': 500,
            'timestamp': datetime.now().isoformat()
        }), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """
        413 Request Entity Too Large hatası için handler
        """
        return jsonify({
            'success': False,
            'error': 'Dosya çok büyük. Maksimum: 50 MB',
            'status_code': 413,
            'timestamp': datetime.now().isoformat()
        }), 413

    # ============ REQUEST HOOKS ============
    @app.before_request
    def before_request():
        """
        Her request'ten önce çalışır
        Loglama, authentication vb. için kullanılabilir
        """
        from flask import request
        print(f"📨 İstek: {request.method} {request.path}")

    @app.after_request
    def after_request(response):

        # Güvenlik header'ları ekle
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Cache kontrolü
        if 'Cache-Control' not in response.headers:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'

        return response

    # ============ SHUTDOWN HOOK ============
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """
        Uygulama context'i kapanırken çalışır
        Redis bağlantısını temizler
        """
        pass

    return app


# ============ ANA ÇALIŞTIRMA BLOĞU ============
if __name__ == '__main__':

    # Uygulama bilgilerini göster
    print("\n" + "=" * 60)
    print("🏥 OCR HOSPITAL MANAGEMENT SYSTEM v2.0")
    print("=" * 60)
    print("📌 Version: 1.0.0")
    print("🐍 Python Flask Backend")
    print("📝 OCR Engine: EasyOCR + Tesseract")
    print("🗄️ Database: PostgreSQL + SQLAlchemy")
    print("=" * 60)

    try:
        # Flask uygulamasını oluştur
        app = create_app()

        # Çalıştırma parametreleri
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_ENV', 'development') == 'development'

        print(f"\n🚀 Sunucu başlatılıyor...")
        print(f"📍 Adres: http://{host}:{port}")
        print(f"📊 Swagger UI: http://localhost:{port}/api/v1/swagger")
        print(f"💚 Health Check: http://localhost:{port}/health")
        print(f"🗄️ Database: PostgreSQL")  # ← YENİ
        print(f"🔧 Debug Modu: {'AÇIK' if debug else 'KAPALI'}")
        print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")

        # Flask uygulamasını başlat
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )

    except KeyboardInterrupt:
        print("\n⚠️ Uygulama kapatılıyor...")
    except Exception as e:
        print(f"\n❌ Uygulama hatası: {e}")
        raise