"""
DOSYA: api/ocr_api.py
AMAÇ: OCR işlemleri için REST API endpoint'lerini sağlayan modül
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from App.services.ocr_service import get_ocr_service
from flask import Blueprint, request
from flask_restx import Api, Resource, fields, Namespace
import os
import uuid
from datetime import datetime
import traceback

# ============ BLUEPRINT VE API TANIMLARI ============
ocr_blueprint = Blueprint('ocr_api', __name__)

# Flask-RESTX API dokümantasyonu için
api = Api(
    ocr_blueprint,
    version='1.0',
    title='OCR Hospital Management API',
    description='Hastane yönetim sistemi için OCR servisi',
    doc='/swagger'
)

# Namespace
ocr_ns = Namespace('ocr', description='OCR işlemleri')

# ============ API MODEL TANIMLARI ============
ocr_request_model = api.model('OCRRequest', {
    'pdf_path': fields.String(
        required=True,
        description='PDF dosyasının sunucudaki tam yolu',
        example='C:/ShareClient/...'
    ),
    'searched_name': fields.String(
        required=True,
        description='PDF içinde aranacak hasta ismi',
        example='Hasta Adı Soyadı'
    )
})

# Batch model tanımı
batch_request_model = api.model('BatchOCRRequest', {
    'jobs': fields.List(
        fields.Nested(ocr_request_model),
        required=True,
        description='OCR job listesi',
        example=[
            {"pdf_path": "C:/ShareClient/file1.pdf", "searched_name": "..."},
            {"pdf_path": "C:/ShareClient/file2.pdf", "searched_name": "..."}
        ]
    ),
    'priority': fields.String(
        default='normal',
        description='Batch priority',
        enum=['low', 'normal', 'high', 'urgent']
    )
})


@ocr_ns.route('/submit-batch')
class OCRSubmitBatch(Resource):
    """
    ENDPOINT: /api/v1/ocr/submit-batch
    METHOD: POST
    AMAÇ: Çoklu job'ı queue'ye ekle
    """

    @api.expect(batch_request_model)
    def post(self):
        """Birden fazla PDF'i queue'ye ekle"""
        try:
            data = request.get_json()
            jobs_data = data.get('jobs', [])
            batch_priority = data.get('priority', 'normal')

            if not jobs_data:
                return {
                    'success': False,
                    'error': 'En az 1 job gerekli',
                    'timestamp': datetime.now().isoformat()
                }, 400

            if len(jobs_data) > 300:  # Batch limit
                return {
                    'success': False,
                    'error': 'Maksimum 300 job işlenebilir',
                    'timestamp': datetime.now().isoformat()
                }, 400

            from App.services.redis_queue_module.job_models import OCRJob, JobPriority
            from App.services.redis_queue_module.redis_queue import get_queue_manager

            # Priority mapping
            priority_map = {
                'low': JobPriority.LOW,
                'normal': JobPriority.NORMAL,
                'high': JobPriority.HIGH,
                'urgent': JobPriority.URGENT
            }
            priority = priority_map.get(batch_priority, JobPriority.NORMAL)

            queue_manager = get_queue_manager()
            job_ids = []
            failed_jobs = []

            # Her job'ı ekle
            for i, job_data in enumerate(jobs_data):
                try:
                    pdf_path = job_data.get('pdf_path')
                    searched_name = job_data.get('searched_name')

                    # Validasyon
                    if not pdf_path or not searched_name:
                        failed_jobs.append({
                            'index': i,
                            'error': 'pdf_path ve searched_name gerekli'
                        })
                        continue

                    is_valid, error_msg = validate_pdf_path(pdf_path)
                    if not is_valid:
                        failed_jobs.append({
                            'index': i,
                            'error': error_msg
                        })
                        continue

                    # Job oluştur
                    job = OCRJob(
                        pdf_path=pdf_path,
                        searched_name=searched_name,
                        priority=priority
                    )

                    # Queue'ye ekle
                    success = queue_manager.add_job(job)
                    if success:
                        job_ids.append(job.job_id)
                    else:
                        failed_jobs.append({
                            'index': i,
                            'error': 'Queue\'ye eklenemedi'
                        })

                except Exception as e:
                    failed_jobs.append({
                        'index': i,
                        'error': str(e)
                    })

            return {
                'success': True,
                'data': {
                    'batch_id': f"batch_{int(datetime.time())}",
                    'job_ids': job_ids,
                    'successful_jobs': len(job_ids),
                    'failed_jobs': len(failed_jobs),
                    'failures': failed_jobs if failed_jobs else None,
                    'estimated_time': f"{len(job_ids) * 3} minutes"
                },
                'message': f'{len(job_ids)} job başarıyla queue\'ye eklendi',
                'timestamp': datetime.now().isoformat()
            }, 200

        except Exception as e:
            return {
                'success': False,
                'error': f'Batch submit hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500

# ============ YARDIMCI FONKSİYONLAR ============
def validate_pdf_path(pdf_path):
    """
    PDF dosya yolunu doğrula
    """
    # Path traversal koruması
    if '..' in pdf_path or '~' in pdf_path:
        return False, "Güvenlik: Geçersiz dosya yolu"

    # Dosya uzantısı kontrolü
    if not pdf_path.lower().endswith('.pdf'):
        return False, "Sadece PDF dosyaları desteklenir"

    # Dosya varlığı kontrolü
    if not os.path.exists(pdf_path):
        return False, f"Dosya bulunamadı: {pdf_path}"

    # Dosya okunabilirlik kontrolü
    if not os.access(pdf_path, os.R_OK):
        return False, "Dosya okuma izni yok"

    # Dosya boyutu kontrolü (maksimum 50 MB)
    file_size = os.path.getsize(pdf_path)
    max_size = 50 * 1024 * 1024  # 50 MB
    if file_size > max_size:
        return False, f"Dosya çok büyük: {file_size / 1024 / 1024:.2f} MB (Max: 50 MB)"

    return True, None

# ============ API ENDPOINT'LERİ ============
@ocr_ns.route('/process')
class OCRProcess(Resource):
    """
    ENDPOINT: /api/v1/ocr/process
    METHOD: POST
    AMAÇ: Senkron OCR işlemi
    """

    @api.expect(ocr_request_model)
    def post(self):
        """
        PDF dosyasını OCR ile işle ve sonucu döndür
        """
        try:
            # Request verilerini al
            data = request.get_json()

            # Zorunlu parametreleri kontrol et
            if not data:
                return {
                    'success': False,
                    'error': 'Request body boş olamaz',
                    'timestamp': datetime.now().isoformat()
                }, 400

            pdf_path = data.get('pdf_path')
            searched_name = data.get('searched_name')

            # Zorunlu alan kontrolü
            if not pdf_path:
                return {
                    'success': False,
                    'error': "'pdf_path' alanı zorunludur",
                    'timestamp': datetime.now().isoformat()
                }, 400

            if not searched_name:
                return {
                    'success': False,
                    'error': "'searched_name' alanı zorunludur",
                    'timestamp': datetime.now().isoformat()
                }, 400

            # Dosya yolu validasyonu
            is_valid, error_msg = validate_pdf_path(pdf_path)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                }, 400

            task_id = str(uuid.uuid4())

            print(f"\n{'='*60}")
            print(f"📋 YENİ OCR İSTEĞİ")
            print(f"{'='*60}")
            print(f"Task ID: {task_id}")
            print(f"Dosya: {pdf_path}")
            print(f"Aranan İsim: {searched_name}")
            print(f"{'='*60}\n")

            ocr_service = get_ocr_service()
            service_result = ocr_service.process_pdf(
                pdf_path=pdf_path,
                searched_name=searched_name
            )


            if service_result is None:
                return {
                    'success': False,
                    'error': 'OCR service işlemi başarısız oldu',
                    'timestamp': datetime.now().isoformat()
                }, 500

            if not service_result.get('success', False):
                return {
                    'success': False,
                    'error': service_result.get('error', 'OCR service hatası'),
                    'timestamp': datetime.now().isoformat()
                }, 500


            ocr_result = service_result.get('ocr_result')
            task_id = service_result.get('task_id')

            # Başarılı yanıt
            return {
                'success': True,
                'data': {
                    'task_id': task_id,
                    'ocr_result': ocr_result
                },
                'message': 'OCR işlemi başarıyla tamamlandı ve database\'e kaydedildi',  # ← Güncellendi
                'timestamp': datetime.now().isoformat()
            }, 200

        except Exception as e:

            error_trace = traceback.format_exc()
            print(f"❌ OCR API Hatası: {str(e)}")
            print(f"Detaylı Hata:\n{error_trace}")

            return {
                'success': False,
                'error': f'Sunucu hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500



@ocr_ns.route('/health')
class HealthCheck(Resource):
    """
    ENDPOINT: /api/v1/ocr/health
    METHOD: GET
    AMAÇ: API sağlık kontrolü
    """

    def get(self):
        """
        API'nin çalışıp çalışmadığını kontrol et
        """
        try:
            import torch
            import psutil

            health_data = {
                'status': 'healthy',
                'version': '1.0.0',
                'gpu_available': torch.cuda.is_available(),
                'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'memory_percent': psutil.virtual_memory().percent,
                'timestamp': datetime.now().isoformat()
            }

            if torch.cuda.is_available() and torch.cuda.device_count() > 0:
                health_data['gpu_name'] = torch.cuda.get_device_name(0)

            return {
                'success': True,
                'data': health_data,
                'message': 'API sağlıklı çalışıyor'
            }, 200

        except Exception as e:
            return {
                'success': False,
                'error': f'Health check hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500


@ocr_ns.route('/results/<task_id>')
class OCRResultByTaskId(Resource):
    """
    ENDPOINT: /api/v1/ocr/results/{task_id}
    METHOD: GET
    AMAÇ: Task ID ile sonuç sorgulama
    """

    def get(self, task_id):
        """Task ID ile OCR sonucunu getir"""
        try:
            from App.services.ocr_service import OCRService

            result = OCRService.get_result_by_task_id(task_id)

            if result:
                return {
                    'success': True,
                    'data': result,
                    'message': 'Sonuç bulundu'
                }, 200
            else:
                return {
                    'success': False,
                    'error': f'Task ID bulunamadı: {task_id}',
                    'timestamp': datetime.now().isoformat()
                }, 404

        except Exception as e:
            return {
                'success': False,
                'error': f'Sorgulama hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500


@ocr_ns.route('/results')
class OCRResultsList(Resource):
    """
    ENDPOINT: /api/v1/ocr/results
    METHOD: GET
    AMAÇ: Son sonuçları listeleme
    """

    def get(self):
        """Son OCR sonuçlarını listele"""
        try:
            from App.services.ocr_service import OCRService
            from flask import request

            # Query parametresi
            limit = int(request.args.get('limit', 10))

            results = OCRService.get_recent_results(limit)

            return {
                'success': True,
                'data': {
                    'results': results,
                    'count': len(results),
                    'limit': limit
                },
                'message': f'{len(results)} sonuç bulundu'
            }, 200

        except Exception as e:
            return {
                'success': False,
                'error': f'Listeleme hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500


# ============ QUEUE-BASED API ENDPOINTS ============

@ocr_ns.route('/submit')
class OCRSubmit(Resource):
    """
    ENDPOINT: /api/v1/ocr/submit
    METHOD: POST
    AMAÇ: Job'ı queue'ye ekle (asenkron)
    """

    @api.expect(ocr_request_model)
    def post(self):
        """PDF'i queue'ye ekle - anında response"""
        try:
            data = request.get_json()


            pdf_path = data.get('pdf_path')
            searched_name = data.get('searched_name')

            if not pdf_path or not searched_name:
                return {
                    'success': False,
                    'error': 'pdf_path ve searched_name gereklidir',
                    'timestamp': datetime.now().isoformat()
                }, 400

            is_valid, error_msg = validate_pdf_path(pdf_path)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                }, 400

            # Job oluştur
            from App.services.redis_queue_module.job_models import OCRJob, JobPriority
            from App.services.redis_queue_module.redis_queue import get_queue_manager

            priority = JobPriority.NORMAL
            if data.get('priority') == 'high':
                priority = JobPriority.HIGH
            elif data.get('priority') == 'urgent':
                priority = JobPriority.URGENT
            elif data.get('priority') == 'low':
                priority = JobPriority.LOW

            job = OCRJob(
                pdf_path=pdf_path,
                searched_name=searched_name,
                priority=priority,
                user_info=data.get('user_info', {})
            )

            # Queue'ye ekle
            queue_manager = get_queue_manager()
            success = queue_manager.add_job(job)

            if success:
                return {
                    'success': True,
                    'data': {
                        'job_id': job.job_id,
                        'status': 'pending',
                        'priority': priority.name,
                        'estimated_time': '2-5 minutes'
                    },
                    'message': 'Job queue\'ye eklendi',
                    'timestamp': datetime.now().isoformat()
                }, 200
            else:
                return {
                    'success': False,
                    'error': 'Job queue\'ye eklenemedi',
                    'timestamp': datetime.now().isoformat()
                }, 500

        except Exception as e:
            return {
                'success': False,
                'error': f'Submit hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500


@ocr_ns.route('/status/<job_id>')
class OCRJobStatus(Resource):
    """
    ENDPOINT: /api/v1/ocr/status/{job_id}
    METHOD: GET
    AMAÇ: Job durumunu sorgula
    """

    def get(self, job_id):
        """Job'ın mevcut durumunu getir"""
        try:
            from App.services.redis_queue_module.redis_queue import get_queue_manager

            queue_manager = get_queue_manager()
            job = queue_manager.get_job_status(job_id)

            if not job:
                return {
                    'success': False,
                    'error': f'Job bulunamadı: {job_id}',
                    'timestamp': datetime.now().isoformat()
                }, 404

            # Response hazırla
            response_data = {
                'job_id': job.job_id,
                'status': job.status.value,
                'priority': job.priority.name,
                'created_at': job.created_at.isoformat(),
                'progress': job.progress
            }

            # Status'e göre ek bilgiler
            if job.status.value == 'processing':
                response_data['worker_id'] = job.worker_id
                response_data['started_at'] = job.started_at.isoformat() if job.started_at else None

            elif job.status.value == 'completed':
                response_data['completed_at'] = job.completed_at.isoformat() if job.completed_at else None
                response_data['result_available'] = True

            elif job.status.value == 'failed':
                response_data['error_message'] = job.error_message
                response_data['retry_count'] = job.retry_count
                response_data['can_retry'] = job.can_retry()

            return {
                'success': True,
                'data': response_data,
                'message': f'Job durumu: {job.status.value}',
                'timestamp': datetime.now().isoformat()
            }, 200

        except Exception as e:
            return {
                'success': False,
                'error': f'Status sorgulama hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500


@ocr_ns.route('/result/<job_id>')
class OCRJobResult(Resource):
    """
    ENDPOINT: /api/v1/ocr/result/{job_id}
    METHOD: GET
    AMAÇ: Job sonucunu getir
    """

    def get(self, job_id):
        """Job'ın sonucunu getir"""
        try:
            from App.services.redis_queue_module.redis_queue import get_queue_manager

            queue_manager = get_queue_manager()
            job = queue_manager.get_job_status(job_id)

            if not job:
                return {
                    'success': False,
                    'error': f'Job bulunamadı: {job_id}',
                    'timestamp': datetime.now().isoformat()
                }, 404

            if job.status.value != 'completed':
                return {
                    'success': False,
                    'error': f'Job henüz tamamlanmadı. Durum: {job.status.value}',
                    'current_status': job.status.value,
                    'timestamp': datetime.now().isoformat()
                }, 400

            return {
                'success': True,
                'data': {
                    'job_id': job.job_id,
                    'status': job.status.value,
                    'result': job.result,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'processing_info': {
                        'worker_id': job.worker_id,
                        'created_at': job.created_at.isoformat(),
                        'started_at': job.started_at.isoformat() if job.started_at else None
                    }
                },
                'message': 'Job sonucu başarıyla alındı',
                'timestamp': datetime.now().isoformat()
            }, 200

        except Exception as e:
            return {
                'success': False,
                'error': f'Result alma hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500


@ocr_ns.route('/queue/stats')
class QueueStats(Resource):
    """
    ENDPOINT: /api/v1/ocr/queue/stats
    METHOD: GET
    AMAÇ: Queue istatistikleri
    """

    def get(self):
        """Queue durumunu ve istatistikleri getir"""
        try:
            from App.services.redis_queue_module.redis_queue import get_queue_manager

            queue_manager = get_queue_manager()
            stats = queue_manager.get_queue_stats()

            return {
                'success': True,
                'data': {
                    'queue_stats': stats,
                    'health': 'healthy' if stats.get('pending_jobs', 0) < 100 else 'busy',
                    'timestamp': datetime.now().isoformat()
                },
                'message': 'Queue istatistikleri başarıyla alındı',
                'timestamp': datetime.now().isoformat()
            }, 200

        except Exception as e:
            return {
                'success': False,
                'error': f'Stats alma hatası: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500

api.add_namespace(ocr_ns, path='/ocr')