"""
DOSYA: database/models.py
AMAÇ: SQLAlchemy ORM modelleri - OCR sonuçları için database tabloları
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def save(self):

        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Kayıt hatası: {e}")
            raise e

    def delete(self):

        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Silme hatası: {e}")
            raise e

    def update(self):

        try:
            from torch.utils._cxx_pytree import kwargs
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Güncelleme hatası: {e}")
            raise e

    def to_dict(self):
        """Model'i dictionary'ye çevir"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.key)
            if isinstance(value, datetime):
                result[column.key] = value.isoformat()
            else:
                result[column.key] = value
        return result

class OCRResult(BaseModel):

    __tablename__ = 'ocr_result'

    task_id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False, index=True)
    expected_name = db.Column(db.String(255), nullable=False)
    detected_name = db.Column(db.String(255), nullable=True)
    match_status = db.Column(db.Boolean, nullable=False, default=False, index=True)
    insurance_company = db.Column(db.String(255), nullable=True, index=True)

    file_path = db.Column(db.Text, nullable=True)


    status = db.Column(db.String(50), default='processing', nullable=False, index=True)

    def __repr__(self):
        return f"<OCRResult(task_id='{self.task_id}', expected_name='{self.expected_name}', detected_name='{self.detected_name}', status='{self.status}')>"

    @classmethod
    def create_processing_record(cls, task_id, expected_name, file_path=None):

        try:
            ocr_result = cls(
                task_id=task_id,
                expected_name=expected_name,
                file_path=file_path,
                status='processing'
            )
            ocr_result.save()
            print(f"✅ Processing record oluşturuldu: {task_id}")
            return ocr_result
        except Exception as e:
            print(f"❌ Processing record oluşturulamadı: {e}")
            raise e

    @classmethod
    def find_by_task_id(cls, task_id):

        return cls.query.filter_by(task_id=task_id).first()

    @classmethod
    def get_recent_results(cls, limit=10):

        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def find_recent_duplicate(cls, file_path, expected_name):

        duplicate = cls.query.filter(
            cls.file_path == file_path,
            cls.expected_name == expected_name,
            cls.status == 'completed',
        ).order_by(cls.created_at.desc()).first()

        return duplicate

    @classmethod
    def find_duplicate(cls, file_path, expected_name):
        """
        Tüm zamanlar için aynı dosya+isim kombinasyonu arar
        """
        duplicate = cls.query.filter(
            cls.file_path == file_path,
            cls.expected_name == expected_name,
            cls.status == 'completed'
        ).order_by(cls.created_at.desc()).first()

        return duplicate

    def update_with_ocr_result(self, ocr_data):
        """
        OCR sonucu ile kaydı güncelle
        Mevcut run_ocr_with_monitoring çıktısı ile uyumlu
        """
        try:
            self.detected_name = ocr_data.get('detected_name')
            self.match_status = ocr_data.get('match_status', False)
            self.insurance_company = ocr_data.get('insurance_company')
            self.status = 'completed'

            processing_info = ocr_data.get('processing_info', {})
            if processing_info:
                timing = processing_info.get('timing', {})
                self.processing_time_seconds = timing.get('total_time_seconds')
                self.pages_processed = processing_info.get('pages_processed', 1)
                self.text_length = processing_info.get('text_length')
                self.language_used = processing_info.get('language_used')

                self.performance_metrics = {
                    'timing': timing,
                    'fast_mode': processing_info.get('fast_mode', True)
                }

            self.save()
            print(f"✅ OCR result güncellendi: {self.task_id}")
            return True

        except Exception as e:
            self.mark_as_failed(str(e))
            raise e

    def mark_as_failed(self, error_message):
        """Başarısız olarak işaretle"""
        try:
            self.status = 'failed'
            self.error_message = error_message
            self.save()
            print(f"❌ Task failed olarak işaretlendi: {self.task_id}")
        except Exception as e:
            print(f"❌ Failed marking hatası: {e}")
















