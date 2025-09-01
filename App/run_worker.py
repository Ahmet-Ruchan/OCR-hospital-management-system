"""
DOSYA: run_worker.py
AMAÇ: Production'da worker'ları başlatmak için
Background OCR worker launcher
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import time
from App.services.redis_queue_module.worker import create_worker

def main():
    parser = argparse.ArgumentParser(description='OCR Background Worker')
    parser.add_argument('--worker-id', type=str, help='Worker ID (opsiyonel)')
    parser.add_argument('--workers', type=int, default=1, help='Worker sayısı (default: 1)')
    parser.add_argument('--verbose', action='store_true', help='Detaylı log')

    args = parser.parse_args()

    print(f"🚀 OCR Worker Launcher")
    print(f"Worker sayısı: {args.workers}")

    workers = []

    try:
        # Multiple worker başlat
        for i in range(args.workers):
            worker_id = args.worker_id or f"worker_{i + 1}"
            if args.workers > 1:
                worker_id = f"{worker_id}_proc_{i + 1}"

            worker = create_worker(worker_id)
            workers.append(worker)

            if args.workers == 1:
                # Single worker - main thread'de çalıştır
                print(f"🔄 Single worker mode: {worker_id}")
                worker.start()
            else:
                # Multiple worker - thread'lerde çalıştır
                import threading
                def run_worker(w):
                    w.start()

                thread = threading.Thread(target=run_worker, args=(worker,), daemon=True)
                thread.start()
                print(f"✅ Worker başlatıldı: {worker_id}")

        if args.workers > 1:
            print(f"🔄 {args.workers} worker çalışıyor. Ctrl+C ile durdurun.")
            # Ana thread'i canlı tut
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n⌨️ Ctrl+C alındı - Worker'lar durduruluyor...")
        for worker in workers:
            worker.stop()
        print(f"✅ Tüm worker'lar durduruldu")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Worker hatası: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()