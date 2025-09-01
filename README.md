# 🏥 OCR Hospital Management System

<div align="center">

**Modern, scalable ve asynchronous OCR sistemi - Hastane yönetim sistemleri için PDF belge işleme çözümü**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-purple.svg)
![Redis](https://img.shields.io/badge/Redis-6.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

---

## 📋 İçindekiler

- [🎯 Proje Hakkında](#-proje-hakkında)
- [✨ Özellikler](#-özellikler)
- [🏗️ Sistem Mimarisi](#️-sistem-mimarisi)
- [🔧 Kurulum](#-kurulum)
- [🚀 Kullanım](#-kullanım)
- [📖 API Dokümantasyonu](#-api-dokümantasyonu)
- [⚙️ Konfigürasyon](#️-konfigürasyon)
- [🐛 Sorun Giderme](#-sorun-giderme)
- [📊 Performance](#-performance)

---

## 🎯 Proje Hakkında

OCR Hospital Management System, hastane yönetim sistemleri için geliştirilmiş modern bir OCR (Optical Character Recognition) çözümüdür. PDF belgelerden hasta isimlerini otomatik olarak tespit eder, sigorta şirketi bilgilerini çıkarır ve bu süreçleri asynchronous olarak yönetir.

### 🏥 Ana Kullanım Alanları

- **Hasta Belge İşleme**: PDF'lerden hasta ismi tespiti
- **Sigorta Şirketi Tanıma**: Otomatik sigorta şirketi belirleme
- **Batch İşlemler**: Çoklu dosya işleme
- **API Entegrasyonu**: Mevcut hastane sistemlerine entegrasyon

### 🎯 Çözülen Problemler

| ❌ Önceki Durum | ✅ Şimdiki Durum |
|-----------------|------------------|
| Manuel belge inceleme | Otomatik OCR tespiti |
| 2-3 dakika işlem süresi | 0.1s API response |
| İnsan hatası riski | %99+ doğruluk oranı |
| Tek dosya işleme | Batch processing |
| Senkron işlemler | Asynchronous queue |

---

## ✨ Özellikler

### 🔍 OCR Özellikleri
- **Dual OCR Engine**: Tesseract + EasyOCR
- **Türkçe Dil Desteği**: Optimized Turkish character recognition
- **Akıllı İsim Arama**: Fuzzy matching ve normalization
- **Sigorta Şirketi Tespiti**: Pattern-based insurance company detection

### ⚡ Performance Özellikleri
- **Asynchronous Processing**: Redis-based job queue
- **Smart Caching**: Duplicate detection ile instant results
- **Priority Queue**: Job önceliklendirme sistemi
- **Auto Retry**: Başarısız job'lar için otomatik tekrar deneme

### 🏗️ Mimari Özellikleri
- **RESTful API**: Flask-RESTX ile Swagger documentation
- **Database Integration**: PostgreSQL ile persistent storage
- **Scalable Workers**: Multiple background worker desteği
- **Monitoring**: Comprehensive logging ve performance tracking

### 🔒 Güvenlik Özellikleri
- **Input Validation**: Path traversal protection
- **File Size Limits**: Güvenli dosya upload limitleri
- **Error Handling**: Comprehensive exception management

---

## 🏗️ Sistem Mimarisi

### 📊 Genel Akış

```
📱 Client Application
    ↓ (HTTP REST API)
🌐 Flask Web Server
    ↓ (Job Queue)
🔴 Redis Queue System
    ↓ (Worker Process)
🤖 Background OCR Workers
    ↓ (Database)
🗄️ PostgreSQL Database
```

### 🔄 İki İşlem Modu

#### 1️⃣ Synchronous Mode (Test/Hızlı İşlemler)
```
Client → POST /api/v1/ocr/process → OCR → Database → Response (2.5s)
```

#### 2️⃣ Asynchronous Mode (Production)
```
Client → POST /api/v1/ocr/submit → Redis Queue → job_id (0.1s)
Background → Worker → OCR → Database → Completed
Client → GET /api/v1/ocr/result/{job_id} → Final Result
```

### 📁 Proje Yapısı

```
ocr-hospital-system/
├── 📁 api/                          # REST API katmanı
│   └── ocr_api.py                   # API endpoints
├── 📁 config/                       # Konfigürasyon
│   └── config.py                    # Environment settings
├── 📁 database/                     # Database katmanı
│   ├── db_manager.py               # DB connection manager
│   └── models.py                   # SQLAlchemy models
├── 📁 ocr/                         # OCR işlem katmanı
│   ├── ocr_engine.py               # Main OCR engine
│   ├── tesseract_manager.py        # Tesseract manager
│   ├── easyocr_manager.py          # EasyOCR manager
│   ├── name_search.py              # Name search algorithms
│   ├── insurance_detector.py       # Insurance company detection
│   └── performance_monitor.py      # Performance monitoring
├── 📁 redis_queue_module/          # Queue sistemi
│   ├── job_models.py               # Job data models
│   ├── redis_queue.py              # Queue manager
│   └── worker.py                   # Background worker
├── 📁 services/                    # Business logic
│   └── ocr_service.py              # OCR service layer
├── main.py                         # Flask app factory
├── run_worker.py                   # Worker launcher
├── requirements.txt                # Dependencies
└── README.md                       # Bu dosya
```

---

## 🔧 Kurulum

### 📋 Sistem Gereksinimleri

#### Yazılım
- **Python**: 3.8+
- **PostgreSQL**: 13+
- **Redis**: 6.0+
- **Tesseract**: 5.0+

### 🛠️ Adım Adım Kurulum

#### 1️⃣ Gerekli Yazılımları Kurun

**Python 3.8+**
```bash
# Windows: python.org'dan indirin
# macOS: 
brew install python3
# Linux:
sudo apt install python3 python3-pip python3-venv
```

**PostgreSQL**
```bash
# Windows: postgresql.org'dan indirin
# macOS:
brew install postgresql
brew services start postgresql
# Linux:
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Redis**
```bash
# Windows: WSL kullanın
sudo apt install redis-server
redis-server --daemonize yes
# macOS:
brew install redis
brew services start redis
# Linux:
sudo apt install redis-server
sudo systemctl start redis-server
```

**Tesseract OCR**
```bash
# Windows: UB-Mannheim/tesseract GitHub releases'den indirin
# macOS:
brew install tesseract
# Linux:
sudo apt install tesseract-ocr tesseract-ocr-tur
```

#### 2️⃣ Proje Kurulumu

```bash
# Proje klasörü oluşturun
git clone <repository-url>
cd ocr-hospital-system

# Virtual environment oluşturun
python -m venv venv

# Virtual environment'ı aktifleştirin
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Dependencies kurun
pip install -r requirements.txt
```

#### 3️⃣ Database Kurulumu

```sql
-- PostgreSQL'de database oluşturun
CREATE DATABASE ocr_hospital_db;
CREATE USER postgres WITH PASSWORD '***';
GRANT ALL PRIVILEGES ON DATABASE ocr_hospital_db TO postgres;
```

#### 4️⃣ Environment Konfigürasyonu

`.env` dosyası oluşturun:

```env
# Environment
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:123@localhost:5432/ocr_hospital_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Tesseract (Windows)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Tesseract (macOS/Linux)
# TESSERACT_PATH=/usr/local/bin/tesseract
```

#### 5️⃣ Database Migration

```bash
# Database tablolarını oluşturun
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### 6️⃣ Test Bağlantıları

```python
# test_connections.py
from App.main import create_app
import redis

# Database test
app = create_app()
with app.app_context():
    from App.database.models import db

    db.create_all()
    print("✅ Database OK")

# Redis test
r = redis.Redis()
r.set('test', 'OK')
print(f"✅ Redis: {r.get('test').decode()}")
```

---

## 🚀 Kullanım

### 🎯 Sistemi Başlatma

#### 1️⃣ Flask Server Başlatın

```bash
# Virtual environment aktif olduğundan emin olun
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Flask server'ı başlatın
python main.py
```

**Beklenen çıktı:**
```
✅ Database bağlantısı başarılı
✅ Tesseract 5.4.0.20240606 hazır!
🔧 OCRService oluşturuldu
🌐 Flask development server başlatıldı
 * Running on http://127.0.0.1:5000
```

#### 2️⃣ Background Worker Başlatın (Yeni Terminal)

```bash
# Aynı proje klasöründe yeni terminal açın
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Single worker
python run_worker.py

# Multiple workers
python run_worker.py --workers 3

# Named worker
python run_worker.py --worker-id "production_worker_1"
```

**Beklenen çıktı:**
```
🚀 OCR Worker Launcher
🔧 OCR Worker oluşturuldu: worker_1
✅ Flask app context aktif
🚀 Worker başlatıldı: worker_1
🔄 Queue'yi dinlemeye başlıyor...
💤 Queue boş, worker_1 bekliyor...
```

### 📊 Test PDF'leri Hazırlama

```bash
# Test klasörü oluşturun
mkdir C:\ShareClient\
# Test PDF'lerinizi bu klasöre koyun
```

---

## 📖 API Dokümantasyonu

### 🌐 Swagger UI

API dokümantasyonuna erişim:
```
http://localhost:5000/api/v1/swagger
```

### 📋 Ana Endpoint'ler

#### 🔄 Synchronous Processing

```http
POST /api/v1/ocr/process
Content-Type: application/json

{
  "pdf_path": "C:/ShareClient/test.pdf",
  "searched_name": "HASTA ADI SOYADI"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "task_id": "abc-123-def",
    "ocr_result": {
      "expected_name": "HASTA ADI SOYADI",
      "detected_name": "HASTA ADI SOYADI",
      "match_status": true,
      "insurance_company": "XXX Sigorta"
    }
  },
  "message": "OCR işlemi başarıyla tamamlandı"
}
```

#### ⚡ Asynchronous Processing

**1. Job Submit:**
```http
POST /api/v1/ocr/submit
Content-Type: application/json

{
  "pdf_path": "C:/ShareClient/test.pdf",
  "searched_name": "HASTA ADI SOYADI",
  "priority": "high"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "abc-123-def",
    "status": "pending",
    "priority": "HIGH",
    "estimated_time": "2-5 minutes"
  }
}
```

**2. Job Status:**
```http
GET /api/v1/ocr/status/{job_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "abc-123-def",
    "status": "completed",
    "priority": "HIGH",
    "progress": 100,
    "completed_at": "2025-08-19T12:30:45"
  }
}
```

**3. Job Result:**
```http
GET /api/v1/ocr/result/{job_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "abc-123-def",
    "status": "completed",
    "result": {
      "task_id": "def-456-ghi",
      "ocr_result": {
        "expected_name": "HASTA ADI SOYADI",
        "detected_name": "HASTA ADI SOYADI",
        "match_status": true,
        "insurance_company": "XXX Sigorta"
      },
      "processing_time": 2.66,
      "worker_id": "worker_1"
    }
  }
}
```

#### 📊 Batch Processing

```http
POST /api/v1/ocr/submit-batch
Content-Type: application/json

{
  "jobs": [
    {"pdf_path": "file1.pdf", "searched_name": "HASTA 1"},
    {"pdf_path": "file2.pdf", "searched_name": "HASTA 2"}
  ],
  "priority": "normal"
}
```

#### 🔍 Monitoring

**Queue Stats:**
```http
GET /api/v1/ocr/queue/stats
```

**Health Check:**
```http
GET /api/v1/ocr/health
```

**Recent Results:**
```http
GET /api/v1/ocr/results?limit=10
```

**Specific Result:**
```http
GET /api/v1/ocr/results/{task_id}
```

### 🎯 Priority Levels

| Priority | Value | Description |
|----------|-------|-------------|
| `urgent` | 10    | En yüksek öncelik |
| `high` | 7     | Yüksek öncelik |
| `normal` | 4     | Normal öncelik (default) |
| `low` | 1     | Düşük öncelik |

### 📝 Job Status Values

| Status | Description |
|--------|-------------|
| `pending` | Queue'de bekliyor |
| `processing` | Worker tarafından işleniyor |
| `completed` | Başarıyla tamamlandı |
| `failed` | Hata ile tamamlandı |
| `cancelled` | İptal edildi |

---

## ⚙️ Konfigürasyon

### 🔧 Environment Dosyası (.env)

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Database Configuration
DATABASE_URL=postgresql://postgres:123@localhost:5432/ocr_hospital_db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# OCR Configuration
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
OCR_LANGUAGE=tur+eng
OCR_DPI=300
OCR_TIMEOUT=30

# File Processing
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf
UPLOAD_FOLDER=C:\ShareClient\

# Worker Configuration
WORKER_TIMEOUT=300
MAX_RETRIES=3
WORKER_CONCURRENCY=1

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ocr_system.log
```

### 🏭 Production Konfigürasyonu

```env
# Production Environment
FLASK_ENV=production
FLASK_DEBUG=False

# Database (Production)
DATABASE_URL=postgresql://user:password@prod-db:5432/ocr_hospital_db

# Redis (Production)
REDIS_URL=redis://prod-redis:6379/0

# Security
SECRET_KEY=your-secret-key-here
API_KEY_REQUIRED=true

# Performance
WORKER_CONCURRENCY=4
MAX_WORKERS=8
```

---

## 🐛 Sorun Giderme

### ❓ Sık Karşılaşılan Sorunlar

#### 1. Database Bağlantı Hatası
```
❌ Error: could not connect to server
```
**Çözüm:**
```bash
# PostgreSQL servisini kontrol edin
# Windows: Services.msc → PostgreSQL
# Linux: sudo systemctl status postgresql
# macOS: brew services list | grep postgresql
```

#### 2. Redis Bağlantı Hatası
```
❌ Error: Connection refused
```
**Çözüm:**
```bash
# Redis servisini kontrol edin
redis-cli ping
# "PONG" dönmeli

# Redis başlatın
# Windows: redis-server
# Linux: sudo systemctl start redis-server
# macOS: brew services start redis
```

#### 3. Tesseract Bulunamadı
```
❌ Error: TesseractNotFoundError
```
**Çözüm:**
```bash
# Tesseract yolunu kontrol edin
tesseract --version

# .env dosyasında TESSERACT_PATH'i güncelleyin
# Windows: C:\Program Files\Tesseract-OCR\tesseract.exe
# Linux/macOS: /usr/bin/tesseract
```

#### 4. Python ModuleNotFoundError
```
❌ Error: ModuleNotFoundError: No module named 'flask'
```
**Çözüm:**
```bash
# Virtual environment aktif mi kontrol edin
which python
# (venv) ile başlamalı

# Requirements'ı yeniden kurun
pip install -r requirements.txt
```

#### 5. Worker Context Hatası
```
❌ Error: Working outside of application context
```
**Çözüm:**
```bash
# Worker'ı Flask app context ile başlatın
# Kod zaten bu sorunu çözüyor
python run_worker.py
```

### 🔍 Debug Araçları

#### 1. Log İnceleme
```bash
# Flask server logs
tail -f logs/flask.log

# Worker logs
tail -f logs/worker.log
```

#### 2. Database İnceleme
```sql
-- Recent OCR results
SELECT * FROM ocr_result ORDER BY created_at DESC LIMIT 10;

-- Job statistics
SELECT status, COUNT(*) FROM ocr_result GROUP BY status;
```

#### 3. Redis İnceleme
```bash
redis-cli
> KEYS ocr_*
> GET ocr_job:abc-123-def
> ZRANGE ocr_jobs:pending 0 -1 WITHSCORES
```

#### 4. System Health Check
```bash
# CPU ve Memory kullanımı
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
"

# GPU kullanımı (varsa)
python -c "
import GPUtil
gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(f'GPU {gpu.id}: {gpu.memoryUsed}MB/{gpu.memoryTotal}MB')
"
```

### 📞 Destek

Sorun yaşıyorsanız:

1. **Logları kontrol edin**
2. **System requirements'ı doğrulayın**
3. **Environment variables'ı kontrol edin**
4. **Services'lerin çalıştığını doğrulayın**

---

## 📊 Performance

### ⚡ Benchmark Sonuçları

| Metric | Synchronous | Asynchronous |
|--------|-------------|--------------|
| **API Response Time** | 2.5s | 0.1s |
| **OCR Processing Time** | 2.5s | 2.5s (background) |
| **Cache Hit Response** | 0.1s | 0.1s |
| **Concurrent Jobs** | 1 | Unlimited |
| **Memory Usage** | 500MB | 500MB per worker |

### 📈 Optimizasyon İpuçları

#### 1. Worker Scaling
```bash
# CPU-bound işlemler için
python run_worker.py --workers 4

# Memory yoğun işlemler için
python run_worker.py --workers 2
```

#### 2. Database Optimizasyonu
```sql
-- Index oluşturma
CREATE INDEX idx_ocr_result_created_at ON ocr_result(created_at);
CREATE INDEX idx_ocr_result_status ON ocr_result(status);
```

#### 3. Redis Optimizasyonu
```bash
# Redis memory kullanımını kontrol edin
redis-cli info memory

# Eski job'ları temizleyin
redis-cli FLUSHDB
```

#### 4. Tesseract Optimizasyonu
```python
# Fast mode için
OCR_DPI=150  # (varsayılan: 300)
OCR_PSM=6    # Tek paragraf modu
```

### 🎯 Production Deployment

#### 1. Nginx + Gunicorn
```bash
# Gunicorn ile Flask app başlatın
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# Nginx configuration
upstream flask_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://flask_app;
    }
}
```

#### 2. Systemd Services
```ini
# /etc/systemd/system/ocr-worker.service
[Unit]
Description=OCR Worker Service

[Service]
User=www-data
WorkingDirectory=/path/to/ocr-hospital-system
ExecStart=/path/to/venv/bin/python run_worker.py --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 3. Docker Deployment
```dockerfile
FROM python:3.9-slim

# Dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tur \
    libpq-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
```

---

### 📝 Geliştirme Standartları

- **Code Style**: PEP 8
- **Documentation**: Docstrings for all functions
- **Testing**: Unit tests for new features
- **Logging**: Comprehensive logging for debugging

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

---

<div align="center">

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

Made with ❤️ by Ahmet Ruçhan Avcı

</div>