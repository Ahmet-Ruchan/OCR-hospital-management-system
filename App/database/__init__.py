"""
Database package initialization
SQLAlchemy modelleri ve database manager
"""

from .models import db, OCRResult, BaseModel
from App.database.db_manager import DatabaseManager, setup_database, get_db_manager

__all__ = [
    'db',
    'OCRResult',
    'BaseModel',
    'DatabaseManager',
    'setup_database',
    'get_db_manager'
]