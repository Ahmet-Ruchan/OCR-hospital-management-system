"""
TESTS MODÜLÜ
════════════

OCR Hospital Management System için test suite'i.

Bu modül tüm test dosyalarını içerir:
- Phase 2 Testleri: Queue sistemi testleri
- Phase 3 Testleri: Worker sistemi testleri
- Unit Testleri: Bileşen testleri
- Integration Testleri: Entegrasyon testleri
- Debug Araçları: Sorun giderme araçları

KULLANIM:
    # Proje kök dizininden çalıştırın:
    python -m tests.test_complete_phase2
    python -m tests.test_workers
    python -m tests.debug_queue_manager

    # Veya pytest ile:
    pytest tests/
"""

__version__ = "1.0.0"
__author__ = "OCR Hospital Team"

import sys
import os

# Proje root'unu Python path'e ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("🧪 Tests modülü yüklendi (v" + __version__ + ")")

# Test kategorileri
TEST_CATEGORIES = {
    'phase2': 'Queue sistemi testleri',
    'phase3': 'Worker sistemi testleri',
    'unit': 'Birim testleri',
    'integration': 'Entegrasyon testleri',
    'debug': 'Debug ve troubleshooting araçları'
}


def print_available_tests():
    """Mevcut testleri listele"""
    print("\n📋 Mevcut Test Kategorileri:")
    for category, description in TEST_CATEGORIES.items():
        print(f"   🔸 {category}: {description}")

    print("\n📝 Test Dosyaları:")
    print("   🧪 test_complete_phase2.py - Phase 2 queue sistemi testi")
    print("   🔧 test_workers.py - Phase 3 worker sistemi testi")
    print("   🔍 debug_queue_manager.py - Queue Manager debug aracı")
    print("   🔴 test_redis_connection.py - Redis bağlantı testi")

    print("\n💡 Kullanım:")
    print("   python -m tests.test_complete_phase2")
    print("   python -m tests.test_workers")
    print("   python -m tests.debug_queue_manager")


# Test modüllerini import et (varsa)
__all__ = []

try:
    from . import test_complete_phase2

    __all__.append('test_complete_phase2')
except ImportError:
    pass

try:
    from . import test_workers

    __all__.append('test_workers')
except ImportError:
    pass

try:
    from . import debug_queue_manager

    __all__.append('debug_queue_manager')
except ImportError:
    pass