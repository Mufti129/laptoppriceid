import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant, ScrapedListing
from analytics.pricing_engine import LaptopPricingEngine
from analytics.depreciation_engine import LaptopDepreciationEngine

class TestAllSidebarMenus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = SessionLocal()
        cls.engine = LaptopPricingEngine(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_menu_1_market_overview(self):
        total_listings = self.db.query(ScrapedListing).count()
        valid_cash = self.db.query(ScrapedListing).filter(ScrapedListing.is_dp_price == False).count()
        self.assertGreater(total_listings, 0)
        self.assertGreater(valid_cash, 0)

        query_brand = self.db.query(
            MasterBrand.name,
            ScrapedListing.price
        ).join(MasterModel, MasterModel.brand_id == MasterBrand.id)\
         .join(MasterVariant, MasterVariant.model_id == MasterModel.id)\
         .join(ScrapedListing, ScrapedListing.matched_variant_id == MasterVariant.id)\
         .filter(ScrapedListing.is_dp_price == False).all()
        self.assertGreater(len(query_brand), 0)

    def test_menu_2_fmv_calculator(self):
        brands = [b.name for b in self.db.query(MasterBrand).order_by(MasterBrand.name).all()]
        for b_name in brands:
            brand_obj = self.db.query(MasterBrand).filter(MasterBrand.name == b_name).first()
            models = self.db.query(MasterModel).filter(MasterModel.brand_id == brand_obj.id).all()
            for m_obj in models:
                variants = self.db.query(MasterVariant).filter(MasterVariant.model_id == m_obj.id).all()
                for v_obj in variants:
                    stats = self.engine.calculate_variant_pricing_stats(v_obj.id)
                    msrp = float(v_obj.official_msrp_new)
                    base_fmv = stats["price_median"] if stats else msrp * 0.7
                    
                    hedonic = self.engine.calculate_hedonic_adjusted_price(
                        base_fmv=base_fmv,
                        warranty_type="Resmi Indonesia",
                        battery_condition="Normal Awet"
                    )
                    self.assertGreater(hedonic["adjusted_price"], 0)

    def test_menu_3_price_corridors(self):
        stats_map = self.engine.get_all_variant_stats_map()
        self.assertIsInstance(stats_map, dict)
        self.assertGreater(len(stats_map), 0)

    def test_menu_4_arbitrage_radar(self):
        deals = self.engine.find_hot_deals(discount_threshold_pct=12.0)
        self.assertIsInstance(deals, list)
        self.assertGreater(len(deals), 0)

    def test_menu_5_spec_matrix(self):
        all_models = self.db.query(MasterModel, MasterBrand).join(MasterBrand, MasterModel.brand_id == MasterBrand.id).all()
        model_choice_map = {f"{b.name} {m.name} ({m.release_year})": m.id for m, b in all_models}
        
        for key, m_id in model_choice_map.items():
            model = self.db.query(MasterModel).filter(MasterModel.id == m_id).first()
            self.assertIsNotNone(model)
            self.assertIsNotNone(model.name)

    def test_menu_6_master_catalog_data(self):
        records = self.db.query(
            MasterModel,
            MasterBrand.name.label("brand_name"),
            MasterVariant.official_msrp_new
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).outerjoin(
            MasterVariant, MasterVariant.model_id == MasterModel.id
        ).all()
        self.assertGreaterEqual(len(records), 1000)

    def test_menu_7_data_explorer(self):
        valid_items = self.db.query(ScrapedListing).filter(ScrapedListing.is_dp_price == False).limit(50).all()
        scam_items = self.db.query(ScrapedListing).filter(ScrapedListing.is_dp_price == True).limit(50).all()
        self.assertGreater(len(valid_items), 0)
        self.assertGreater(len(scam_items), 0)

    def test_menu_8_tradein_calculator(self):
        from analytics.buyback_engine import BuybackPricingEngine
        # Test sample model/variant buyback
        first_variant = self.db.query(MasterVariant).join(MasterModel).filter(MasterModel.brand_id.isnot(None)).first()
        self.assertIsNotNone(first_variant)
        
        # 1. Normal condition
        offer_normal = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=10000000.0,
            condition_state="NORMAL",
            brand_name=first_variant.model.brand.name,
            selected_defects=[],
            completeness="Fullset (Dus + Charger Original)",
            warranty_status="Garansi Resmi > 6 Bulan"
        )
        self.assertTrue(offer_normal["is_eligible"])
        self.assertGreater(offer_normal["cash_offer_low"], 0)
        self.assertGreaterEqual(offer_normal["trade_in_credit"], offer_normal["cash_offer_low"])

        # 2. Defect condition
        offer_defect = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=10000000.0,
            condition_state="NORMAL",
            brand_name=first_variant.model.brand.name,
            selected_defects=["lcd_lines", "battery_drop"],
            completeness="Batangan (Unit Saja)",
            warranty_status="Tidak Ada Garansi"
        )
        self.assertLess(offer_defect["cash_offer_low"], offer_normal["cash_offer_low"])

        # 3. Mati Total condition
        offer_dead = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=10000000.0,
            condition_state="MATI_TOTAL",
            brand_name=first_variant.model.brand.name,
            selected_defects=[],
            completeness="Unit + Charger",
            warranty_status="Tidak Ada Garansi"
        )
        self.assertEqual(offer_dead["condition_state"], "MATI_TOTAL")
        self.assertTrue(offer_dead["is_eligible"])
        self.assertIn("Kanibalan", offer_dead["deductions_breakdown"][0]["name"])

if __name__ == "__main__":
    unittest.main()
