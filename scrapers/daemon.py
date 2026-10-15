import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import argparse
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from scrapers.real_marketplace_scraper import RealMarketplaceScraper, TARGET_KEYWORDS
from scrapers.populate_real_data import ingest_real_listings, CACHE_FILE
from models.database import SessionLocal, init_db

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ScraperDaemon")

TELEMETRY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "scraper_health.json")

def parse_interval(interval_str: str) -> int:
    """Konversi string interval (misal '6h', '30m', '3600s') ke total detik."""
    s = interval_str.strip().lower()
    if s.endswith("h"):
        return int(float(s[:-1]) * 3600)
    elif s.endswith("m"):
        return int(float(s[:-1]) * 60)
    elif s.endswith("s"):
        return int(s[:-1])
    try:
        return int(s)
    except ValueError:
        logger.warning(f"Format interval '{interval_str}' tidak valid, fallback ke default 6 jam (21600s).")
        return 21600

def record_telemetry(status: str, duration: float, harvested_count: int, adapters_health: Dict[str, Any], next_run_epoch: Optional[float] = None, error_msg: Optional[str] = None):
    """Menyimpan status kesehatan dan telemetri eksekusi daemon ke JSON."""
    os.makedirs(os.path.dirname(TELEMETRY_FILE), exist_ok=True)
    payload = {
        "last_run_timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "duration_seconds": round(duration, 2),
        "items_harvested": harvested_count,
        "adapters_health": adapters_health,
        "next_scheduled_run": datetime.fromtimestamp(next_run_epoch, tz=timezone.utc).isoformat() if next_run_epoch else None,
        "error_message": error_msg
    }
    try:
        with open(TELEMETRY_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info(f"Telemetri kesehatan scraper diperbarui di {TELEMETRY_FILE}")
    except Exception as e:
        logger.error(f"Gagal mencatat telemetri: {e}")

def run_harvest_cycle(max_items: int = 4000) -> Dict[str, Any]:
    """Menjalankan satu siklus penuh harvesting & delta ingestion."""
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("MEMULAI SIKLUS HARVESTING & DELTA MONITORING")
    logger.info("=" * 60)

    scraper = RealMarketplaceScraper(request_delay=0.4)

    # 1. Healthcheck seluruh adapter
    health = scraper.health_check_all()
    logger.info(f"Pemeriksaan kesehatan adapter: {health}")

    # 2. Muat cache riil eksisting
    existing_listings = []
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                existing_listings = json.load(f)
            logger.info(f"Memuat {len(existing_listings)} listing riil sebelumnya dari cache.")
        except Exception as e:
            logger.warning(f"Gagal memuat cache: {e}")

    # 3. Harvesting live dengan multi-selector cascade
    harvested = scraper.harvest_all_keywords(
        max_items=max_items,
        existing_listings=existing_listings
    )

    # 4. Simpan pembaruan cache
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(harvested, f, ensure_ascii=False, indent=2)
        logger.info(f"Cache berhasil diperbarui dengan {len(harvested)} listing.")
    except Exception as e:
        logger.error(f"Gagal menyimpan cache: {e}")

    # 5. Ingesti ke Database dengan Delta Price Tracking (purge_old=False)
    logger.info("Menjalankan ingesti delta ke database...")
    ingest_real_listings(harvested, purge_old=False)

    duration = time.time() - start_time
    logger.info(f"Siklus selesai dengan sukses dalam {duration:.2f} detik. Total item: {len(harvested)}")
    return {
        "status": "SUCCESS",
        "duration": duration,
        "count": len(harvested),
        "health": health
    }

def main():
    parser = argparse.ArgumentParser(description="LaptopPrice ID - Scraping Orchestrator & Autonomous Daemon")
    parser.add_argument("--interval", type=str, default="6h", help="Interval pengulangan (e.g. '6h', '30m', '3600s')")
    parser.add_argument("--run-once", action="store_true", help="Jalankan satu kali siklus lalu keluar (cocok untuk cron job OS)")
    parser.add_argument("--max-items", type=int, default=4500, help="Target kapasitas listing maksimum")
    parser.add_argument("--health-check-only", action="store_true", help="Hanya jalankan tes kesehatan adapter tanpa scraping")
    args = parser.parse_args()

    init_db()

    if args.health_check_only:
        scraper = RealMarketplaceScraper()
        res = scraper.health_check_all()
        print(json.dumps(res, indent=2))
        return

    interval_sec = parse_interval(args.interval)

    if args.run_once:
        logger.info("Mode One-Shot aktif. Menjalankan 1 siklus...")
        try:
            res = run_harvest_cycle(max_items=args.max_items)
            record_telemetry("SUCCESS", res["duration"], res["count"], res["health"])
        except Exception as e:
            logger.error(f"Terjadi kesalahan pada siklus: {e}", exc_info=True)
            record_telemetry("FAILED", 0.0, 0, {}, error_msg=str(e))
            sys.exit(1)
        return

    logger.info(f"Memulai Daemon Scraping Otonom (Interval: {args.interval} / {interval_sec} detik)...")
    logger.info("Tekan Ctrl+C untuk menghentikan daemon.")

    while True:
        cycle_start = time.time()
        next_run = cycle_start + interval_sec
        try:
            res = run_harvest_cycle(max_items=args.max_items)
            record_telemetry("SUCCESS", res["duration"], res["count"], res["health"], next_run_epoch=next_run)
        except Exception as e:
            logger.error(f"Kesalahan pada siklus daemon: {e}", exc_info=True)
            record_telemetry("FAILED", time.time() - cycle_start, 0, {}, next_run_epoch=next_run, error_msg=str(e))

        sleep_duration = max(10, int(next_run - time.time()))
        logger.info(f"Menunggu siklus berikutnya dalam {sleep_duration} detik (Pukul {datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')})...")
        try:
            time.sleep(sleep_duration)
        except KeyboardInterrupt:
            logger.info("Daemon dihentikan oleh pengguna (SIGINT). Selesai.")
            break

if __name__ == "__main__":
    main()
