import json
import uuid
import datetime
from enum import Enum

class JobStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class JobPriority(Enum):
    LOW = 1
    NORMAL = 4
    HIGH = 7
    URGENT = 10

class OCRJob:

    def __init__(self, pdf_path, searched_name, priority=JobPriority.NORMAL, user_info=None):
        self.job_id = str(uuid.uuid4())
        self.pdf_path = pdf_path
        self.searched_name = searched_name
        self.priority = priority
        self.user_info = user_info or {}

        self.status = JobStatus.PENDING
        self.created_at = datetime.datetime.now()
        self.started_at = None
        self.completed_at = None

        self.result = None
        self.error_message = None
        self.progress = 0

        self.worker_id = None
        self.retry_count = 0
        self.max_retries = 2

    def to_dict(self):
        return {
            'job_id': self.job_id,
            'pdf_path': self.pdf_path,
            'searched_name': self.searched_name,
            'priority': self.priority.value,
            'user_info': self.user_info,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error_message': self.error_message,
            'progress': self.progress,
            'worker_id': self.worker_id,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }

    def to_json(self):
        """Job'ı JSON string'e çevir"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data):
        """Dictionary'den job oluştur"""
        job = cls.__new__(cls)

        job.job_id = data['job_id']
        job.pdf_path = data['pdf_path']
        job.searched_name = data['searched_name']
        job.priority = JobPriority(data['priority'])
        job.user_info = data.get('user_info', {})
        job.status = JobStatus(data['status'])
        job.created_at = datetime.datetime.fromisoformat(data['created_at'])
        job.started_at = datetime.datetime.fromisoformat(data['started_at']) if data['started_at'] else None
        job.completed_at = datetime.datetime.fromisoformat(data['completed_at']) if data['completed_at'] else None
        job.result = data.get('result')
        job.error_message = data.get('error_message')
        job.progress = data.get('progress', 0)
        job.worker_id = data.get('worker_id')
        job.retry_count = data.get('retry_count', 0)
        job.max_retries = data.get('max_retries', 3)

        return job

    @classmethod
    def from_json(cls, json_str):
        """JSON string'den job oluştur"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def mark_processing(self, worker_id):
        """Job'ı processing olarak işaretle"""
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.datetime.now()
        self.worker_id = worker_id
        self.progress = 50

    def mark_completed(self, result):
        """Job'ı completed olarak işaretle"""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.datetime.now()
        self.result = result
        self.progress = 100

    def mark_failed(self, error_message):
        """Job'ı failed olarak işaretle"""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.datetime.now()
        self.error_message = error_message
        self.retry_count += 1

    def can_retry(self):
        """Tekrar denenebilir mi?"""
        return self.retry_count < self.max_retries

    def __repr__(self):
        return f"<OCRJob {self.job_id}: {self.searched_name} - {self.status.value}>"

























