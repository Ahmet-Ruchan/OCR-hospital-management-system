"""
DOSYA: redis_queue_module/worker.py
...
"""

import time
import signal
import sys
from datetime import datetime
import uuid
from App.main import create_app

from App.services.redis_queue_module.job_models import JobStatus
from App.services.redis_queue_module.redis_queue import get_queue_manager
from App.services.ocr_service import OCRService


class OCRWorker:

    def __init__(self, worker_id=None):
        self.worker_id = worker_id or f"worker_{str(uuid.uuid4())[:8]}"
        self.queue_manager = get_queue_manager()

        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.ocr_service = OCRService()
        self.running = False
        self.current_job = None

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print(f"🔧 OCR Worker oluşturuldu: {self.worker_id}")
        print(f"✅ Flask app context aktif")

    def start(self):
        """Worker'ı başlat - ana loop"""
        self.running = True
        print(f"🚀 Worker başlatıldı: {self.worker_id}")
        print(f"⏱️ Zaman: {datetime.now()}")
        print(f"🔄 Queue'yi dinlemeye başlıyor...")

        while self.running:
            try:
                # Queue'den job al
                job = self.queue_manager.get_next_job(self.worker_id)

                if job:
                    self.current_job = job
                    print(f"\n{'=' * 60}")
                    print(f"📋 YENİ JOB İŞLENİYOR")
                    print(f"{'=' * 60}")
                    print(f"Worker: {self.worker_id}")
                    print(f"Job ID: {job.job_id}")
                    print(f"PDF: {job.pdf_path}")
                    print(f"Searched Name: {job.searched_name}")
                    print(f"Priority: {job.priority.name}")
                    print(f"{'=' * 60}")

                    # Job'ı işle
                    self._process_job(job)
                    self.current_job = None

                else:
                    # Queue boş, biraz bekle
                    print(f"💤 Queue boş, {self.worker_id} bekliyor... ({datetime.now().strftime('%H:%M:%S')})")
                    time.sleep(5)  # 5 saniye bekle

            except Exception as e:
                print(f"❌ Worker loop hatası: {e}")
                time.sleep(10)  # Hata durumunda biraz daha bekle

        print(f"🛑 Worker durdu: {self.worker_id}")

    def _process_job(self, job):
        """Tek bir job'ı işle"""
        start_time = time.time()

        try:
            print(f"🚀 OCR işlemi başlatılıyor...")

            # YENİ: Her job için fresh app context
            with self.app.app_context():
                # Mevcut OCR Service'i kullan
                result = self.ocr_service.process_pdf(
                    pdf_path=job.pdf_path,
                    searched_name=job.searched_name
                )

            processing_time = time.time() - start_time
            print(f"⏱️ İşlem süresi: {processing_time:.2f} saniye")

            if result and result.get('success'):
                # Başarılı
                print(f"✅ OCR başarılı!")

                # Result'ı Redis format'ına çevir
                redis_result = {
                    'task_id': result.get('task_id'),
                    'ocr_result': result.get('ocr_result'),
                    'duplicate': result.get('duplicate', False),
                    'processing_time': processing_time,
                    'worker_id': self.worker_id,
                    'completed_at': datetime.now().isoformat()
                }

                # Redis'te job'ı completed olarak işaretle
                self.queue_manager.update_job_status(
                    job.job_id,
                    JobStatus.COMPLETED,
                    result=redis_result
                )

                print(f"📊 Sonuç:")
                ocr_result = result.get('ocr_result', {})
                print(f"   Expected: {ocr_result.get('expected_name')}")
                print(f"   Detected: {ocr_result.get('detected_name')}")
                print(f"   Match: {ocr_result.get('match_status')}")
                print(f"   Insurance: {ocr_result.get('insurance_company', 'N/A')}")
                print(f"   Duplicate: {result.get('duplicate', False)}")

            else:
                # Hata
                error_msg = result.get('error', 'Bilinmeyen hata') if result else 'OCR service None döndürdü'
                print(f"❌ OCR başarısız: {error_msg}")

                # Redis'te job'ı failed olarak işaretle
                self.queue_manager.update_job_status(
                    job.job_id,
                    JobStatus.FAILED,
                    error_message=error_msg
                )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Worker exception: {str(e)}"
            print(f"❌ Job işleme hatası: {error_msg}")

            # Redis'te job'ı failed olarak işaretle
            self.queue_manager.update_job_status(
                job.job_id,
                JobStatus.FAILED,
                error_message=error_msg
            )

        print(f"🏁 Job tamamlandı: {job.job_id}")

    def stop(self):
        """Worker'ı durdur"""
        print(f"\n🛑 Worker durduruluyor: {self.worker_id}")
        self.running = False

        # YENİ: Flask app context'i temizle
        try:
            self.app_context.pop()
            print(f"✅ Flask app context temizlendi")
        except:
            pass

        # Eğer şu anda bir job işleniyorsa bekle
        if self.current_job:
            print(f"⏳ Mevcut job tamamlanana kadar bekleniyor: {self.current_job.job_id}")

    def _signal_handler(self, signum, frame):
        """Signal handler - Graceful shutdown"""
        print(f"\n📡 Signal alındı: {signum}")
        self.stop()
        sys.exit(0)

    def get_status(self):
        """Worker durumunu getir"""
        return {
            'worker_id': self.worker_id,
            'running': self.running,
            'current_job': self.current_job.job_id if self.current_job else None,
            'uptime': time.time() - getattr(self, 'start_time', time.time())
        }


def create_worker(worker_id=None):
    """Worker factory function"""
    return OCRWorker(worker_id)


if __name__ == "__main__":
    """Worker'ı direkt çalıştırmak için"""
    worker = create_worker()
    try:
        worker.start()
    except KeyboardInterrupt:
        print(f"\n⌨️ Ctrl+C ile durduruldu")
        worker.stop()