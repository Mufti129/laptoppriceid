import unittest
from analytics.buyback_engine import BuybackPricingEngine, DEFECT_CATALOG

class TestBuybackPricingEngine(unittest.TestCase):

    def test_normal_condition_valuation(self):
        """Verifikasi taksiran laptop normal mulus (Standard vs Gaming vs Apple)."""
        base_fmv = 10000000  # Rp 10.000.000

        # Standard Laptop (25% margin)
        res_std = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="NORMAL",
            is_gaming=False,
            brand_name="Lenovo"
        )
        self.assertTrue(res_std["is_eligible"])
        self.assertEqual(res_std["margin_rate_pct"], 25)
        self.assertLess(res_std["cash_offer_mid"], base_fmv)
        self.assertGreater(res_std["trade_in_credit"], res_std["cash_offer_mid"])

        # Gaming Laptop (28% margin)
        res_game = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="NORMAL",
            is_gaming=True,
            brand_name="ASUS"
        )
        self.assertEqual(res_game["margin_rate_pct"], 28)

        # Apple Laptop (22% margin)
        res_apple = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="NORMAL",
            is_gaming=False,
            brand_name="Apple"
        )
        self.assertEqual(res_apple["margin_rate_pct"], 22)

    def test_tiered_defect_deductions(self):
        """Verifikasi biaya minus berbeda antara Standard, Gaming, dan Apple."""
        cost_std = BuybackPricingEngine.get_defect_deduction("lcd_broken", brand_name="Acer", is_gaming=False)
        cost_game = BuybackPricingEngine.get_defect_deduction("lcd_broken", brand_name="ASUS", is_gaming=True)
        cost_apple = BuybackPricingEngine.get_defect_deduction("lcd_broken", brand_name="Apple", is_gaming=False)

        self.assertGreater(cost_game, cost_std, "Biaya LCD Gaming harus lebih tinggi dari standar")
        self.assertGreater(cost_apple, cost_game, "Biaya LCD Retina Apple harus lebih tinggi dari gaming")

    def test_multiple_defects_accumulation(self):
        """Verifikasi akumulasi multi-minus pada hasil akhir."""
        base_fmv = 8000000
        selected = ["white_spot", "battery_drop", "keyboard_faulty"]
        res = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="NORMAL",
            selected_defects=selected,
            brand_name="HP",
            is_gaming=False
        )

        expected_total = (
            DEFECT_CATALOG["white_spot"]["cost_standard"] +
            DEFECT_CATALOG["battery_drop"]["cost_standard"] +
            DEFECT_CATALOG["keyboard_faulty"]["cost_standard"]
        )
        self.assertEqual(res["total_deductions"], expected_total)
        self.assertEqual(len(res["deductions_breakdown"]), 3)

    def test_mati_total_salvage_value(self):
        """Verifikasi formula kanibalan 12.5% untuk kondisi Mati Total."""
        base_fmv = 12000000
        res = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="MATI_TOTAL",
            selected_defects=["lcd_broken"],  # Harus diabaikan karena status kanibalan
            brand_name="Lenovo",
            is_gaming=False
        )

        self.assertEqual(res["condition_state"], "MATI_TOTAL")
        self.assertEqual(res["total_deductions"], 0)
        expected_raw_salvage = base_fmv * 0.125
        self.assertAlmostEqual(res["cash_offer_low"], round(expected_raw_salvage / 50000) * 50000, delta=100000)

    def test_completeness_and_warranty_bonuses(self):
        """Verifikasi bonus Fullset dan Garansi Resmi Aktif."""
        base_fmv = 10000000
        res = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="NORMAL",
            completeness="Fullset (Dus Buku + Charger Original)",
            warranty_status="Garansi Resmi > 6 Bulan",
            brand_name="Dell"
        )

        self.assertGreater(res["completeness_bonus"], 0)
        self.assertGreater(res["warranty_bonus"], 0)

    def test_minimum_floor_protection(self):
        """Verifikasi perlindungan ambang batas minimal kelayakan komersial."""
        # Laptop tua sangat murah dengan kerusakan parah
        base_fmv = 1000000
        res = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="NORMAL",
            selected_defects=["lcd_broken", "battery_drop", "hinge_broken"],
            brand_name="Lenovo",
            is_gaming=False
        )

        # Total minus (750k + 450k + 450k = 1.65jt) melebihi FMV 1jt
        self.assertFalse(res["is_eligible"])
        self.assertIsNotNone(res["ineligibility_reason"])

if __name__ == "__main__":
    unittest.main()
