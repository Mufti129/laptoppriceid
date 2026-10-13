"""
Indeks Disparitas Harga Laptop Antar-Wilayah di Indonesia.
Mengukur deviasi harga laptop bekas di berbagai kota besar terhadap benchmark nasional (DKI Jakarta).
"""
from typing import Dict

REGIONAL_LAPTOP_INDEX: Dict[str, float] = {
    "Jakarta Selatan": 1.00,
    "Jakarta Barat": 0.99,
    "Jakarta Pusat": 1.00,
    "Tangerang": 0.99,
    "Bekasi": 0.98,
    "Bandung": 0.97,
    "Surabaya": 0.98,
    "Semarang": 0.96,
    "Yogyakarta": 0.96,
    "Malang": 0.95,
    "Medan": 1.03,        # Sedikit premium di luar pulau Jawa karena ongkir kargo/ketersediaan
    "Palembang": 1.02,
    "Makassar": 1.04,
    "Denpasar (Bali)": 1.01,
    "Balikpapan": 1.05
}

class RegionalPriceIndex:

    @classmethod
    def get_multiplier(cls, city: str) -> float:
        for known_city, mult in REGIONAL_LAPTOP_INDEX.items():
            if known_city.lower() in city.lower():
                return mult
        return 1.00
