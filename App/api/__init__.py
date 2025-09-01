"""
DOSYA: api/__init__.py
AMAÇ: API modülünü Python paketi haline getirir

AÇIKLAMA:
- API klasörünü Python paketi yapar
- Blueprint'leri dışa aktarır
- API versiyonunu yönetir

KULLANIM:
    from api import ocr_blueprint
    app.register_blueprint(ocr_blueprint)
"""

# API versiyonu
__version__ = '1.0.0'

# API Blueprint'lerini import et
from App.api.ocr_api import ocr_blueprint

# Public API
__all__ = [
    'ocr_blueprint'
]

# Modül yüklendiğinde
print(f"🔌 API Modülü yüklendi (v{__version__})")