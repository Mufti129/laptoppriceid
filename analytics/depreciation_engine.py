"""
Model Depresiasi Laptop Multi-Tier Indonesia.
Menghitung laju penyusutan nilai laptop sekunder terhadap harga peluncuran baru (MSRP OTR).
Berbasis riset ekonometrik depresiasi komputer & laptop di pasar sekunder Indonesia:
- Tier Apple Silicon (M1/M2/M3/M4): Retensi nilai sangat tinggi (~15% th-1, ~7% th berikutnya, cap 65%)
- Tier Apple Intel Legacy: Depresiasi curam (~28% th-1, ~12% th berikutnya, cap 85%)
- Tier Business Enterprise (ThinkPad X1/T, Dell XPS/Latitude, HP EliteBook): Depresiasi kokoh (~20% th-1, ~9% th berikutnya)
- Tier Gaming High-End (ROG, Legion Pro, Alienware, Predator): Depresiasi moderat (~24% th-1, ~11% th berikutnya)
- Tier Consumer Mainstream / Entry (IdeaPad, Vivobook, Aspire, Pavilion, LOQ, Victus, Axioo): Depresiasi cepat (~30% th-1, ~14% th berikutnya)
"""

class LaptopDepreciationEngine:

    TIER_RATES = {
        "Apple_Silicon": {"year_1": 0.15, "annual_decay": 0.07, "max_cap": 0.65},
        "Apple_Intel": {"year_1": 0.28, "annual_decay": 0.12, "max_cap": 0.85},
        "Business_Enterprise": {"year_1": 0.20, "annual_decay": 0.09, "max_cap": 0.75},
        "Gaming_HighEnd": {"year_1": 0.24, "annual_decay": 0.11, "max_cap": 0.78},
        "Consumer_Mainstream": {"year_1": 0.30, "annual_decay": 0.14, "max_cap": 0.82},
    }

    @classmethod
    def get_tier_for_model(cls, brand_name: str, model_name: str, processor_model: str = "") -> str:
        brand_low = brand_name.lower()
        model_low = model_name.lower()
        proc_low = processor_model.lower()

        if "apple" in brand_low or "macbook" in model_low:
            if any(m in proc_low or m in model_low for m in ["m1", "m2", "m3", "m4"]):
                return "Apple_Silicon"
            return "Apple_Intel"

        if any(kw in model_low for kw in ["thinkpad", "xps", "latitude", "elitebook", "surface"]):
            return "Business_Enterprise"

        if any(kw in model_low for kw in ["rog", "zephyrus", "strix", "legion pro", "alienware", "predator", "raider", "titan"]):
            return "Gaming_HighEnd"

        return "Consumer_Mainstream"

    @classmethod
    def calculate_theoretical_retention(
        cls,
        brand_name: str,
        model_name: str,
        release_year: int,
        current_year: int = 2026,
        processor_model: str = ""
    ) -> float:
        """
        Menghitung persentase retensi nilai teoritis (0.0 - 1.0).
        """
        tier = cls.get_tier_for_model(brand_name, model_name, processor_model)
        params = cls.TIER_RATES.get(tier, cls.TIER_RATES["Consumer_Mainstream"])

        age = max(0, current_year - release_year)
        if age == 0:
            total_depreciation = params["year_1"] * 0.5  # Model tahun berjalan
        else:
            total_depreciation = params["year_1"] + ((age - 1) * params["annual_decay"])

        total_depreciation = min(params["max_cap"], total_depreciation)
        retention_rate = 1.0 - total_depreciation
        return retention_rate

    @classmethod
    def calculate_real_depreciation(
        cls,
        msrp_new: float,
        current_market_price: float
    ) -> float:
        """
        Menghitung persentase depresiasi riil dari MSRP Baru ke Harga Pasar Saat Ini.
        """
        if msrp_new <= 0:
            return 0.0
        depr = ((msrp_new - current_market_price) / msrp_new) * 100.0
        return max(0.0, round(depr, 2))
