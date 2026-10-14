import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant, ScrapedListing
from analytics.pricing_engine import LaptopPricingEngine
from analytics.depreciation_engine import LaptopDepreciationEngine

class TestAuditUIAndEngine(unittest.TestCase):

    def setUp(self):
        init_db()
        self.db = SessionLocal()
        self.engine = LaptopPricingEngine(self.db)

    def tearDown(self):
        self.db.close()

    def test_database_catalog_integrity(self):
        brand_count = self.db.query(MasterBrand).count()
        model_count = self.db.query(MasterModel).count()
        variant_count = self.db.query(MasterVariant).count()
        listing_count = self.db.query(ScrapedListing).count()

        self.assertGreaterEqual(brand_count, 10, "Jumlah brand minimal 10")
        self.assertGreaterEqual(model_count, 600, "Jumlah model minimal 600")
        self.assertGreaterEqual(variant_count, 600, "Jumlah varian minimal 600")
        self.assertGreaterEqual(listing_count, 1000, "Jumlah listing riil hasil scraping minimal 1000")

    def test_each_brand_has_at_least_100_models(self):
        brands = self.db.query(MasterBrand).all()
        self.assertGreaterEqual(len(brands), 10)
        for b in brands:
            m_count = self.db.query(MasterModel).filter(MasterModel.brand_id == b.id).count()
            self.assertGreaterEqual(m_count, 100, f"Brand {b.name} harus memiliki minimal 100 model (ditemukan {m_count})")

    def test_all_modules_query_safety(self):
        # 1. Market Overview Query
        query_brand = self.db.query(MasterBrand.name, ScrapedListing.price).join(
            MasterModel, MasterModel.brand_id == MasterBrand.id
        ).join(
            MasterVariant, MasterVariant.model_id == MasterModel.id
        ).join(
            ScrapedListing, ScrapedListing.matched_variant_id == MasterVariant.id
        ).all()
        self.assertGreater(len(query_brand), 0)

        # 2. FMV & Hedonic Calculator Query
        brand = self.db.query(MasterBrand).first()
        model = self.db.query(MasterModel).filter(MasterModel.brand_id == brand.id).first()
        variant = self.db.query(MasterVariant).filter(MasterVariant.model_id == model.id).first()
        
        hedonic_res = self.engine.calculate_hedonic_adjusted_price(
            base_fmv=float(variant.official_msrp_new) * 0.7,
            warranty_type="Resmi Indonesia",
            battery_condition="Normal Awet"
        )
        self.assertIn("adjusted_price", hedonic_res)

        # 3. Spec Matrix ID Mapping Safety
        all_models = self.db.query(MasterModel, MasterBrand).join(MasterBrand, MasterModel.brand_id == MasterBrand.id).all()
        model_choice_map = {f"{b.name} {m.name} ({m.release_year})": m.id for m, b in all_models}
        for key, m_id in model_choice_map.items():
            m_obj = self.db.query(MasterModel).filter(MasterModel.id == m_id).first()
            self.assertIsNotNone(m_obj, f"Model ID {m_id} untuk key {key} harus ditemukan di DB")

        # 4. Arbitrage Scanner
        deals = self.engine.find_hot_deals(discount_threshold_pct=10.0)
        self.assertIsInstance(deals, list)

if __name__ == "__main__":
    unittest.main()
