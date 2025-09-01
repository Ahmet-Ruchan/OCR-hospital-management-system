from flask import Flask
from flask_migrate import Migrate
from App.database.models import db, OCRResult


class DatabaseManager:

    def __init__(self):
        self.db = db
        self.migrate = None
        self.app = None
        print("DatabaseManager oluşturuldu")

    def init_app(self, app: Flask):

        try:
            self.app = app

            self.db.init_app(app)
            print("✅ SQLAlchemy app'a bağlandı")

            self.migrate = Migrate(app, db)
            print("✅ Migrate initialize edildi")

            if app.config.get('DEBUG'):
                db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')
                print(f"🔗 Database URI: {db_uri}")

            return True

        except Exception as e:
            print(f"❌ Database oluşturulamadı: {e}")
            raise e

    def test_connection(self):
        """Database bağlantısını test et"""
        try:
            with self.app.app_context():
                from sqlalchemy import text
                result = self.db.session.execute(text("SELECT 1"))
                print(f"✅ Database bağlantısı başarılı")
                return True
        except Exception as e:
            print(f"❌ Database bağlantı hatası: {e}")
            return False

    def create_tables(self):

        try:
            with self.app.app_context():
                self.db.create_all()
                print("✅ Database tabloları oluşturuldu")

                inspector = self.db.inspect(self.db.engine)
                tables = inspector.get_table_names()
                print(f"✅ Oluşturulan Database tabloları: {tables}")

                return True

        except Exception as e:
            print(f"❌ Database tabloları oluşturulamadı: {e}")
            return False

    def run_migrations(self):

        try:
            with self.app.app_context():
                from flask_migrate import upgrade
                upgrade()
                print("✅ Database migration basarılı")
                return True

        except Exception as e:
            print(f"❌ Database migration basarısız: {e}")
            return False

    def check_tables_exist(self):

        try:
            with self.app.app_context():
                inspector = self.db.inspect(self.db.engine)
                tables = inspector.get_table_names()

                required_tables = ['ocr_results']
                missing_tables = [table for table in required_tables if table not in tables]

                if missing_tables:
                    print(f"❌ Database tabloları eksik: {missing_tables}")
                    return False
                else:
                    print("✅ Database tabloları kontrol edildi")
                    return True

        except Exception as e:
            print(f"❌ Database tabloları kontrol edilemedi: {e}")
            return False, [str(e)]

    def get_database_info(self):

        try:
            with self.app.app_context():

                inspector = self.db.inspect(self.db.engine)
                tables = inspector.get_table_names()

                ocr_count = OCRResult.query.count()

                return {
                    'database_engine' : str(self.db.engine.dialect.name),
                    'tables' : tables,
                    'ocr_results_count' : ocr_count,
                    'connection_status' : 'connected'
                }

        except Exception as e:
            print(f"❌ Database bilgileri alınamadı: {e}")
            return {
                'connection_status' : 'failed',
                'error' : str(e)
            }


db_manager = DatabaseManager()

def setup_database(app: Flask):
    """Flask app'e database'i setup et"""
    try:
        print(f"\n🗄️ Database Setup Başlatılıyor...")

        db_manager.init_app(app)
        connection_ok = db_manager.test_connection()

        result = db_manager.check_tables_exist()
        if isinstance(result, tuple):
            tables_exist, missing = result
        else:
            tables_exist = result
            missing = []

        if not tables_exist:
            print(f"⚠️ Eksik tablolar oluşturuluyor...")
            db_manager.create_tables()

        db_info = db_manager.get_database_info()
        print(f"📊 Database Info: {db_info}")
        print(f"✅ Database setup tamamlandı!")
        return True

    except Exception as e:
        print(f"❌ Database setup hatası: {e}")
        return False

def get_db_manager():

    return db_manager




























