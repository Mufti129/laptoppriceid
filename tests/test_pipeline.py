import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from models.database import SessionLocal, init_db
from pipeline.normalizer import LaptopListingNormalizer
from pipeline.scam_detector import LaptopScamDetector
from pipeline.entity_matcher import LaptopEntityMatcher
from analytics.pricing_engine import LaptopPricingEngine
from analytics.depreciation_engine import LaptopDepreciationEngine

class TestLaptopPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = SessionLocal()
        cls.matcher = LaptopEntityMatcher(cls.db)
        cls.pricing_engine = LaptopPricingEngine(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_nlp_normalizer_extraction(self):
        sample_title = "ThinkPad T480 i5 8GB 256GB SSD mulus no minus charger ori baterai awet"
        norm = LaptopListingNormalizer.normalize_listing({
            "title": sample_title,
            "description": "Layar jernih no whitespot engsel kokoh bebas password bios",
            "price": "4.500.000"
        })

        self.assertEqual(norm["price"], 4500000.0)
        self.assertEqual(norm["ram_gb"], 8)
        self.assertEqual(norm["storage_gb"], 256)
        self.assertIn("Resmi Indonesia", norm["warranty_type"])
        self.assertEqual(norm["battery_condition"], "Normal Awet")
        self.assertEqual(norm["completeness"], "Unit + Charger Original")
        self.assertEqual(norm["physical_grade"], "Grade A (Mulus 95%)")
        self.assertEqual(norm["hinge_condition"], "Normal Kokoh")
        self.assertEqual(norm["screen_condition"], "Normal Jernih")
        self.assertEqual(norm["bios_mdm_status"], "Clean")

    def test_dp_scam_detector(self):
        # Test 1: DP Cicilan trap
        is_scam, cat, reason = LaptopScamDetector.evaluate_listing(
            price=1500000,
            title="Lenovo Legion Pro 7i RTX 4080 DP Ringan Angsuran Kredivo",
            description="Promo bayar DP 1.5jt",
            expected_msrp=54999000
        )
        self.assertTrue(is_scam)
        self.assertEqual(cat, "DP_CLICKBAIT")

        # Test 2: Locked BIOS
        is_scam_lock, cat_lock, _ = LaptopScamDetector.evaluate_listing(
            price=3000000,
            title="ThinkPad T14 Gen 4 Ryzen 7 Terkunci Password BIOS Computrace",
            description="Lupa sandi bios"
        )
        self.assertTrue(is_scam_lock)
        self.assertEqual(cat_lock, "LOCKED_OR_BYPASS")

    def test_entity_matcher(self):
        var_id, score, name, msrp = self.matcher.match("MacBook Air 13 M1 8GB 256GB Space Gray", ram_gb=8, storage_gb=256)
        self.assertIsNotNone(var_id, "Harus cocok dengan varian MacBook Air 13 M1 256GB")
        self.assertGreaterEqual(score, 56.0)

    def test_hedonic_pricing_calculation(self):
        res = self.pricing_engine.calculate_hedonic_adjusted_price(
            base_fmv=10_000_000,
            battery_condition="Baterai Drop (Colok Terus)",
            hinge_condition="Engsel Kendor / Patah",
            screen_condition="Whitespot Tipis"
        )
        self.assertLess(res["adjusted_price"], 10_000_000)
        self.assertLess(res["net_adjustment_pct"], 0)

if __name__ == "__main__":
    unittest.main()
