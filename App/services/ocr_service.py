import uuid
import pytesseract
import os
from App.ocr.ocr_engine import run_ocr_with_monitoring
from App.database.models import OCRResult
from App.database.db_manager import get_db_manager

class OCRService:

    def __init__(self):
        self.db_manager = get_db_manager()
        print("🔧 OCRService oluşturuldu")

        # Tesseract path'ini environment'tan al veya varsayılan kullan
        tesseract_path = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')

        # pytesseract'a path'i set et
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"🔧 Tesseract path set: {tesseract_path}")

        # Test et
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract {version} başarıyla test edildi!")
            self.tesseract_available = True
        except Exception as e:
            print(f"❌ Tesseract test hatası: {e}")

            # Alternative paths dene
            alt_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]

            self.tesseract_available = False
            for alt_path in alt_paths:
                try:
                    pytesseract.pytesseract.tesseract_cmd = alt_path
                    version = pytesseract.get_tesseract_version()
                    print(f"✅ Tesseract bulundu: {alt_path}")
                    self.tesseract_available = True
                    break
                except:
                    continue

            if not self.tesseract_available:
                print(f"❌ Tesseract bulunamadı. Lütfen kurun: https://github.com/UB-Mannheim/tesseract/wiki")

    def process_pdf(self, pdf_path, searched_name, user_info=None):
        # ============ TESSERACT KONTROL ============
        if not self.tesseract_available:
            print("❌ Tesseract kullanılamıyor!")
            return {
                'task_id': str(uuid.uuid4()),
                'success': False,
                'error': 'Tesseract OCR not available. Please install Tesseract.',
                'ocr_result': None
            }

        # ============ YENİ: DUPLICATE KONTROLÜ ============
        print(f"\n{'=' * 60}")
        print(f"🔍 OCR SERVİS İŞLEMİ BAŞLADI")
        print(f"{'=' * 60}")
        print(f"Dosya: {pdf_path}")
        print(f"Aranan İsim: {searched_name}")

        # Duplicate kontrol et
        print(f"🔍 Duplicate kontrol ediliyor...")
        duplicate_record = OCRResult.find_duplicate(
            file_path=pdf_path,
            expected_name=searched_name
        )

        if duplicate_record:
            print(f"✅ DUPLICATE BULUNDU!")
            print(f"   Mevcut Task ID: {duplicate_record.task_id}")
            print(f"   İlk İşlem Zamanı: {duplicate_record.created_at}")
            print(f"🚀 Cache'den sonuç döndürülüyor...")

            return {
                'task_id': duplicate_record.task_id,
                'success': True,
                'duplicate': True,
                'ocr_result': {
                    'expected_name': duplicate_record.expected_name,
                    'detected_name': duplicate_record.detected_name,
                    'match_status': duplicate_record.match_status,
                    'insurance_company': duplicate_record.insurance_company,
                    'processing_info': {
                        'cached': True,
                        'original_processing_time': getattr(duplicate_record, 'processing_time_seconds', None),
                        'cache_hit': True
                    }
                }
            }

        print(f"✅ Yeni kombinasyon, OCR işlemi başlatılıyor...")
        # ============ DUPLICATE KONTROL BİTTİ ============

        task_id = str(uuid.uuid4())

        print(f"Task ID: {task_id}")
        print(f"{'=' * 60}")

        # Dosya boyutunu hesapla
        file_size_mb = None
        if os.path.exists(pdf_path):
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            print(f"📁 Dosya boyutu: {file_size_mb:.2f} MB")

        ocr_record = None
        try:
            ocr_record = OCRResult.create_processing_record(
                task_id=task_id,
                expected_name=searched_name,
                file_path=pdf_path
            )

            # Dosya boyutunu kaydet
            if file_size_mb:
                ocr_record.file_size_mb = file_size_mb
                ocr_record.save()

            print(f"✅ Database'e processing record oluşturuldu")

        except Exception as e:
            print(f"❌ Database'e processing record oluşturulamadı: {e}")

        # OCR işlemi
        ocr_result = None
        try:
            print(f"🚀 OCR Engine başlatılıyor...")

            # Tesseract path'ini tekrar force et (safety)
            print(f"🔧 Tesseract path kontrol: {pytesseract.pytesseract.tesseract_cmd}")

            ocr_result = run_ocr_with_monitoring(
                expected_name=searched_name,
                pdf_path=pdf_path
            )

            print(f"✅ OCR işlemi tamamlandı")

        except Exception as e:
            error_msg = f"OCR işlemi hatası: {str(e)}"
            print(f"❌ {error_msg}")

            # Detaylı hata bilgisi
            import traceback
            traceback.print_exc()

            if ocr_record:
                ocr_record.mark_as_failed(error_msg)

            return {
                'task_id': task_id,
                'success': False,
                'error': str(e),
                'ocr_result': None
            }

        # ============ DATABASE GÜNCELLEME ============
        try:
            if ocr_record and ocr_result:
                print(f"🔧 Database güncelleme başlatılıyor...")
                ocr_record.update_with_ocr_result(ocr_result)
                print(f"✅ Database kaydı güncellendi")

                # Task ID'yi OCR sonucuna ekle
                ocr_result['task_id'] = task_id

                print(f"📊 İşlem Özeti:")
                print(f"   Task ID: {task_id}")
                print(f"   Expected: {ocr_result.get('expected_name')}")
                print(f"   Detected: {ocr_result.get('detected_name')}")
                print(f"   Match: {ocr_result.get('match_status')}")
                print(f"   Insurance: {ocr_result.get('insurance_company', 'N/A')}")

                return {
                    'task_id': task_id,
                    'success': True,
                    'ocr_result': ocr_result
                }

        except Exception as e:
            error_msg = f"Database güncelleme hatası: {str(e)}"
            print(f"❌ {error_msg}")

            # OCR başarılı ama database hatası - yine de sonuç döndür
            if ocr_result:
                ocr_result['task_id'] = task_id
                ocr_result['database_warning'] = error_msg

                return {
                    'task_id': task_id,
                    'success': True,
                    'ocr_result': ocr_result,
                    'warning': 'OCR başarılı ama database güncellenemedi'
                }

        # Beklenmeyen durum
        return {
            'task_id': task_id,
            'success': False,
            'error': 'Bilinmeyen hata oluştu'
        }

    def get_result_by_task_id(task_id):

        try:
            ocr_record = OCRResult.find_by_task_id(task_id)

            if ocr_record:
                print(f"✅ Task bulundu: {task_id}")
                return ocr_record.to_dict()
            else:
                print(f"❌ Task bulunamadı: {task_id}")
                return None

        except Exception as e:
            print(f"❌ Task bulunamadı: {task_id}")
            return None

    def get_recent_results(limit=10):

        try:
            records = OCRResult.get_recent_results(limit)
            results = [record.to_dict() for record in records]
            print(f"✅ {len(results)} son sonuç getirildi")
            return results

        except Exception as e:
            print(f"❌ Son sonuç getirilemedi: {e}")
            return []

ocr_service = OCRService()

def get_ocr_service():
    return ocr_service
























