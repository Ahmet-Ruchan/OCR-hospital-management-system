"""
DOSYA: utils/__init__.py
AMAÇ: Utils modülünü Python paketi haline getirir

AÇIKLAMA:
- Yardımcı fonksiyonları içeren paketi tanımlar
- Config sınıfını dışa aktarır
- Ortak kullanılan utility fonksiyonları sağlar

KULLANIM:
    from utils import Config
    from utils.config import Config
"""

# Config sınıfını import et
from App.utils.config import Config

# Public API
__all__ = [
    'Config'
]

# Modül yüklendiğinde
print(f"🛠️ Utils Modülü yüklendi")