"""
DOSYA: queue/redis_queue.py
AMAÇ: Redis ile queue işlemlerini yönetir
Job'ları ekler, çeker, günceller
"""

import redis
from datetime import datetime, timedelta
from App.services.redis_queue_module.job_models import OCRJob, JobStatus


class RedisQueueManager:
    """
    Redis tabanlı queue yöneticisi
    Job'ları priority'ye göre sıralar ve işler
    """

    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        """Redis bağlantısını başlat"""
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )

            # Bağlantı testi
            self.redis_client.ping()
            print(f"✅ Redis'e bağlanıldı: {redis_host}:{redis_port}")

        except Exception as e:
            print(f"❌ Redis bağlantı hatası: {e}")
            raise e

        # Queue isimleri
        self.PENDING_QUEUE = "ocr_jobs:pending"
        self.PROCESSING_QUEUE = "ocr_jobs:processing"
        self.COMPLETED_SET = "ocr_jobs:completed"
        self.FAILED_SET = "ocr_jobs:failed"
        self.JOB_HASH_PREFIX = "ocr_job:"

    def add_job(self, job):
        """
        Job'ı pending queue'ye ekle
        Priority'ye göre sıralama yapar
        """
        try:
            # Job'ı Redis hash olarak kaydet
            job_key = f"{self.JOB_HASH_PREFIX}{job.job_id}"
            job_data = job.to_json()

            # Job detaylarını kaydet
            self.redis_client.set(job_key, job_data)

            # Priority queue'ye ekle (ZADD - sorted set)
            # Yüksek priority = düşük score (önce işlenir)
            score = -job.priority.value  # Negative çünkü düşük score önce gelir
            self.redis_client.zadd(self.PENDING_QUEUE, {job.job_id: score})

            print(f"✅ Job queue'ye eklendi: {job.job_id} (priority: {job.priority.name})")
            return True

        except Exception as e:
            print(f"❌ Job ekleme hatası: {e}")
            return False

    def get_next_job(self, worker_id):
        """
        En yüksek priority'li job'ı al ve processing'e taşı
        Eski Redis versiyonları için uyumlu
        """
        try:
            # En düşük score'lu job'ı al (en yüksek priority)
            result = self.redis_client.zrange(self.PENDING_QUEUE, 0, 0, withscores=True)

            if not result:
                return None  # Queue boş

            job_id, score = result[0]

            # Job'ı pending queue'den çıkar
            removed = self.redis_client.zrem(self.PENDING_QUEUE, job_id)
            if not removed:
                # Başka worker almış olabilir, tekrar dene
                return None

            # Job detaylarını Redis'ten al
            job_key = f"{self.JOB_HASH_PREFIX}{job_id}"
            job_data = self.redis_client.get(job_key)

            if not job_data:
                print(f"⚠️ Job data bulunamadı: {job_id}")
                return None

            # Job'ı deserialize et
            job = OCRJob.from_json(job_data)

            # Job'ı processing olarak işaretle
            job.mark_processing(worker_id)

            # Processing queue'ye ekle
            self.redis_client.sadd(self.PROCESSING_QUEUE, job_id)

            # Job'ı güncelle
            self.redis_client.set(job_key, job.to_json())

            print(f"🔄 Job alındı: {job_id} by worker {worker_id}")
            return job

        except Exception as e:
            print(f"❌ Job alma hatası: {e}")
            return None

    def update_job_status(self, job_id, status, result=None, error_message=None):
        """
        Job'ın durumunu güncelle
        """
        try:
            job_key = f"{self.JOB_HASH_PREFIX}{job_id}"
            job_data = self.redis_client.get(job_key)

            if not job_data:
                print(f"⚠️ Job bulunamadı: {job_id}")
                return False

            # Job'ı deserialize et
            job = OCRJob.from_json(job_data)

            # Status'ü güncelle
            if status == JobStatus.COMPLETED:
                job.mark_completed(result)
                # Processing'den çıkar, completed'a ekle
                self.redis_client.srem(self.PROCESSING_QUEUE, job_id)
                self.redis_client.sadd(self.COMPLETED_SET, job_id)

            elif status == JobStatus.FAILED:
                job.mark_failed(error_message)
                # Processing'den çıkar
                self.redis_client.srem(self.PROCESSING_QUEUE, job_id)

                # Retry edebilir mi?
                if job.can_retry():
                    print(f"🔄 Job retry edilecek: {job_id} (attempt {job.retry_count})")
                    # Pending queue'ye geri ekle
                    score = -job.priority.value
                    self.redis_client.zadd(self.PENDING_QUEUE, {job_id: score})
                else:
                    print(f"❌ Job max retry'a ulaştı: {job_id}")
                    self.redis_client.sadd(self.FAILED_SET, job_id)

            # Job'ı güncelle
            self.redis_client.set(job_key, job.to_json())

            print(f"📊 Job status güncellendi: {job_id} → {status.value}")
            return True

        except Exception as e:
            print(f"❌ Status güncelleme hatası: {e}")
            return False

    def get_job_status(self, job_id):
        """
        Job'ın mevcut durumunu getir
        """
        try:
            job_key = f"{self.JOB_HASH_PREFIX}{job_id}"
            job_data = self.redis_client.get(job_key)

            if not job_data:
                return None

            job = OCRJob.from_json(job_data)
            return job

        except Exception as e:
            print(f"❌ Job status alma hatası: {e}")
            return None

    def get_queue_stats(self):
        """
        Queue istatistiklerini getir
        """
        try:
            stats = {
                'pending_jobs': self.redis_client.zcard(self.PENDING_QUEUE),
                'processing_jobs': self.redis_client.scard(self.PROCESSING_QUEUE),
                'completed_jobs': self.redis_client.scard(self.COMPLETED_SET),
                'failed_jobs': self.redis_client.scard(self.FAILED_SET),
                'total_jobs_in_system': 0
            }

            # Toplam job sayısı
            all_job_keys = self.redis_client.keys(f"{self.JOB_HASH_PREFIX}*")
            stats['total_jobs_in_system'] = len(all_job_keys)

            return stats

        except Exception as e:
            print(f"❌ Stats alma hatası: {e}")
            return {}

    def cleanup_old_jobs(self, days=7):
        """
        Eski job'ları temizle
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Tüm job'ları kontrol et
            all_job_keys = self.redis_client.keys(f"{self.JOB_HASH_PREFIX}*")
            cleaned_count = 0

            for job_key in all_job_keys:
                job_data = self.redis_client.get(job_key)
                if job_data:
                    job = OCRJob.from_json(job_data)
                    if job.created_at < cutoff_date and job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                        # Job'ı sil
                        self.redis_client.delete(job_key)
                        # Set'lerden de çıkar
                        self.redis_client.srem(self.COMPLETED_SET, job.job_id)
                        self.redis_client.srem(self.FAILED_SET, job.job_id)
                        cleaned_count += 1

            print(f"🧹 {cleaned_count} eski job temizlendi")
            return cleaned_count

        except Exception as e:
            print(f"❌ Cleanup hatası: {e}")
            return 0


# Global instance
queue_manager = RedisQueueManager()


def get_queue_manager():
    """Global queue manager instance'ını döndür"""
    return queue_manager