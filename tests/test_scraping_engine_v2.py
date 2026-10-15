import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
from decimal import Decimal
from models.database import SessionLocal, init_db
from models.catalog import ScrapedListing, ListingPriceHistory
from scrapers.adapters.base import BaseScraperAdapter
from scrapers.adapters.carousell_adapter import CarousellAdapter
from scrapers.adapters.tokopedia_adapter import TokopediaAdapter
from scrapers.real_marketplace_scraper import RealMarketplaceScraper
from scrapers.populate_real_data import ingest_real_listings, clean_price_string
from scrapers.daemon import record_telemetry, TELEMETRY_FILE, parse_interval

class TestScrapingEngineV2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_adapter_interfaces(self):
        """Verifikasi bahwa seluruh adapter mengimplementasikan BaseScraperAdapter."""
        c_adapter = CarousellAdapter()
        t_adapter = TokopediaAdapter()

        self.assertIsInstance(c_adapter, BaseScraperAdapter)
        self.assertIsInstance(t_adapter, BaseScraperAdapter)

        # Cek headers
        headers = c_adapter.get_headers()
        self.assertIn("User-Agent", headers)
        self.assertIn("Sec-Ch-Ua", headers)

    def test_price_string_cleaner(self):
        """Verifikasi parsing string harga fleksibel."""
        self.assertEqual(clean_price_string("Rp 8.500.000"), 8500000.0)
        self.assertEqual(clean_price_string("Rp 7,50"), 7500000.0)
        self.assertEqual(clean_price_string("idr 12.000.000"), 12000000.0)
        self.assertEqual(clean_price_string(5000000), 5000000.0)
        self.assertEqual(clean_price_string(None), 0.0)

    def test_daemon_interval_parser(self):
        """Verifikasi parser durasi interval daemon."""
        self.assertEqual(parse_interval("6h"), 21600)
        self.assertEqual(parse_interval("30m"), 1800)
        self.assertEqual(parse_interval("60s"), 60)
        self.assertEqual(parse_interval("invalid"), 21600)

    def test_telemetry_recording(self):
        """Verifikasi perekaman data telemetri kesehatan."""
        record_telemetry(
            status="SUCCESS",
            duration=12.45,
            harvested_count=4000,
            adapters_health={"carousell": {"status": "HEALTHY"}}
        )
        self.assertTrue(os.path.exists(TELEMETRY_FILE))
        with open(TELEMETRY_FILE, "r") as f:
            data = json.load(f)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["items_harvested"], 4000)

    def test_delta_price_tracking_logic(self):
        """Verifikasi pencatatan riwayat penurunan harga di database."""
        # 1. Buat listing uji unik
        test_ext_id = "test_unit_delta_9999"
        existing = self.db.query(ScrapedListing).filter(ScrapedListing.external_id == test_ext_id).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        initial_item = [{
            "source_platform": "carousell",
            "external_id": test_ext_id,
            "url": "https://id.carousell.com/p/test-delta-9999/",
            "title": "Lenovo ThinkPad T480 i5 8GB 256GB Mulus",
            "price": 4000000.0,
            "price_raw": "Rp 4.000.000",
            "raw_description": "Kondisi mulus normal",
            "city": "Jakarta Selatan"
        }]

        # Ingest awal
        ingest_real_listings(initial_item, purge_old=False)
        db_item = self.db.query(ScrapedListing).filter(ScrapedListing.external_id == test_ext_id).first()
        self.assertIsNotNone(db_item)
        self.assertEqual(float(db_item.price), 4000000.0)
        self.assertEqual(db_item.price_drop_count, 0)
        self.assertEqual(db_item.status, "ACTIVE")

        # 2. Simulasikan scraping ulang dengan harga turun Rp 3.600.000 (-400rb)
        dropped_item = [{
            "source_platform": "carousell",
            "external_id": test_ext_id,
            "url": "https://id.carousell.com/p/test-delta-9999/",
            "title": "Lenovo ThinkPad T480 i5 8GB 256GB Mulus (Turun Harga)",
            "price": 3600000.0,
            "price_raw": "Rp 3.600.000"
        }]

        ingest_real_listings(dropped_item, purge_old=False)
        self.db.expire_all()

        updated_item = self.db.query(ScrapedListing).filter(ScrapedListing.external_id == test_ext_id).first()
        self.assertEqual(float(updated_item.price), 3600000.0)
        self.assertEqual(updated_item.price_drop_count, 1)
        self.assertEqual(updated_item.status, "PRICE_DROP")

        # Cek entri riwayat harga
        history_rows = self.db.query(ListingPriceHistory).filter(ListingPriceHistory.listing_id == updated_item.id).all()
        self.assertEqual(len(history_rows), 1)
        h = history_rows[0]
        self.assertEqual(float(h.old_price), 4000000.0)
        self.assertEqual(float(h.new_price), 3600000.0)
        self.assertEqual(float(h.price_delta), -400000.0)
        self.assertEqual(float(h.price_delta_pct), -10.0)

        # Bersihkan data uji
        self.db.delete(updated_item)
        self.db.commit()

if __name__ == "__main__":
    unittest.main()
