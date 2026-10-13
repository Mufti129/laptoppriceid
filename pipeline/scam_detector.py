import re
from typing import Optional, Tuple
from pipeline.slang_dictionary import DP_SCAM_PATTERNS, BIOS_SECURITY_PATTERNS

class LaptopScamDetector:
    """
    Detektor Iklan Penipuan, Perangkap DP/Cicilan, Spek Palsu/Disamarkan, dan Unit Terkunci BIOS/MDM pada Pasar Laptop.
    """

    MIN_PLAUSIBLE_CASH_PRICE = 800_000  # Di bawah 800rb untuk laptop modern adalah rongsokan/part mati/DP semu
    
    FAKE_SPEC_PATTERNS = [
        r"\bi7\s*gen\s*1\b", r"\bi7\s*620m\b", r"\bi7\s*720qm\b", r"\bcore\s*2\s*duo\b",
        r"\breplika\b", r"\bdummy\b", r"\bclone\b"
    ]

    LOCKED_PATTERNS = [
        r"\bbios\s*(?:lock|terkunci|password)\b",
        r"\b(?:password|lock|terkunci|sandi)\s*bios\b",
        r"\bcomputrace\b",
        r"\bmdm\b",
        r"\blupa\s*password\s*bios\b",
        r"\bicloud\s*lock\b"
    ]

    @classmethod
    def evaluate_listing(
        cls,
        price: Optional[float],
        title: str,
        description: str = "",
        expected_msrp: Optional[float] = None
    ) -> Tuple[bool, str, str]:
        """
        Mengevaluasi apakah listing valid, penipuan DP, spek disamarkan, atau locked device.
        Returns: (is_scam_or_dp: bool, category: str, reason: str)
        """
        if price is None or price <= 0:
            return True, "INVALID_PRICE", "Harga kosong atau 0"

        text_corpus = f"{title} {description}".lower()

        # 1. Cek Unit Terkunci Firmware / BIOS / MDM
        for pat in cls.LOCKED_PATTERNS:
            if re.search(pat, text_corpus):
                return True, "LOCKED_OR_BYPASS", f"Unit mengalami lock BIOS / Computrace / MDM: '{pat}'"

        # 2. Cek Spek Palsu atau Sangat Usang yang Disamarkan sebagai Gaming Modern
        for pat in cls.FAKE_SPEC_PATTERNS:
            if re.search(pat, text_corpus) and any(kw in text_corpus for kw in ["gaming", "gahar", "libas game", "rtx"]):
                return True, "MISLEADING_SPECS", f"Indikasi spesifikasi purba/disamarkan sebagai gaming: '{pat}'"

        # 3. Cek Kata Kunci DP di Judul dengan Harga Tidak Wajar
        for pat in DP_SCAM_PATTERNS:
            if re.search(pat, title.lower()):
                if price < 7_000_000:
                    return True, "DP_CLICKBAIT", f"Mengandung kata kunci DP/Kredit di judul: '{pat}'"

        # 4. Anomali Harga Ekstrim Terhadap MSRP Baru
        if expected_msrp and expected_msrp > 0:
            # Jika harga di bawah 15% dari MSRP baru untuk laptop modern (misal Legion 25jt dijual 2jt)
            if price < (expected_msrp * 0.15) and price < 5_000_000:
                for pat in DP_SCAM_PATTERNS:
                    if re.search(pat, text_corpus):
                        return True, "DP_CLICKBAIT", f"Harga anomali ({price:,.0f}) dengan keyword cicilan: '{pat}'"
                return True, "SUSPICIOUS_ANOMALY", f"Harga sangat tidak wajar ({price:,.0f} vs MSRP {expected_msrp:,.0f})"

        # 5. Batas Minimum Absolut
        if price < cls.MIN_PLAUSIBLE_CASH_PRICE:
            return True, "UNREALISTIC_LOW", f"Harga di bawah batas minimum Rp {cls.MIN_PLAUSIBLE_CASH_PRICE:,.0f}"

        return False, "VALID_CASH", "Listing Tunai Valid"
