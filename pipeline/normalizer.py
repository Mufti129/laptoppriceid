import re
from typing import Dict, Any, Optional, Tuple
from pipeline.slang_dictionary import (
    WARRANTY_PATTERNS, BATTERY_PATTERNS, COMPLETENESS_PATTERNS,
    PHYSICAL_GRADE_PATTERNS, HINGE_PATTERNS, SCREEN_PATTERNS,
    KEYBOARD_PATTERNS, BIOS_SECURITY_PATTERNS, PRICE_SLANG_PATTERNS
)

class LaptopListingNormalizer:
    """
    NLP & Rule-based Normalizer untuk Ekstraksi Spesifikasi Hardware & Metadata Pasar Laptop Indonesia.
    """

    @staticmethod
    def parse_price(raw_val: Any) -> Optional[float]:
        """Konversi representasi string/angka harga ke float bersih."""
        if raw_val is None:
            return None
        if isinstance(raw_val, (int, float)):
            return float(raw_val)

        text = str(raw_val).strip().lower()
        text = re.sub(r"^(?:rp\.?|idr|harga:?)\s*", "", text)

        for pattern, multiplier in PRICE_SLANG_PATTERNS:
            match = re.search(pattern, text)
            if match:
                num_str = match.group(1).replace(",", ".")
                try:
                    return float(num_str) * multiplier
                except ValueError:
                    pass

        clean_num = re.sub(r"[^\d]", "", text)
        if clean_num:
            try:
                return float(clean_num)
            except ValueError:
                return None
        return None

    @staticmethod
    def extract_ram(text: str) -> Optional[int]:
        """Ekstraksi kapasitas RAM dalam GB."""
        lower = text.lower()
        # Cek format RAM/SSD misal 16/512, 16gb/1tb, 8/256
        ram_ssd_match = re.search(r"\b(\d{1,2})\s*(?:gb)?\s*[/,]\s*(\d{3,4}|1tb|2tb)\b", lower)
        if ram_ssd_match:
            try:
                val = int(ram_ssd_match.group(1))
                if val in [4, 8, 12, 16, 24, 32, 48, 64, 128]:
                    return val
            except ValueError:
                pass

        # Cek keyword 'ram X gb'
        ram_match = re.search(r"\bram\s*(\d{1,2})\s*(?:gb)?\b", lower)
        if ram_match:
            try:
                val = int(ram_match.group(1))
                if val in [4, 8, 16, 24, 32, 64]:
                    return val
            except ValueError:
                pass

        # Cek pola umum: '8gb 256gb' atau '16gb 512gb'
        ram_storage_pair = re.search(r"\b(4|8|12|16|24|32|48|64)\s*gb\s+(?:ssd\s+)?(128|256|512|1024|1tb|2tb)\b", lower)
        if ram_storage_pair:
            try:
                return int(ram_storage_pair.group(1))
            except ValueError:
                pass

        # Cek isolated RAM size (4, 8, 12, 16, 24, 32, 48, 64) jika diikuti angka storage yang lebih besar
        all_gb = re.findall(r"\b(\d{1,4})\s*gb\b", lower)
        if all_gb:
            int_vals = [int(x) for x in all_gb if x.isdigit()]
            rams = [x for x in int_vals if x in [4, 8, 12, 16, 24, 32, 48, 64]]
            if rams:
                return rams[0]

        return None

    @staticmethod
    def extract_storage(text: str) -> Optional[int]:
        """Ekstraksi kapasitas SSD / Storage dalam GB."""
        lower = text.lower()
        if "2tb" in lower or "2 tb" in lower or "2048gb" in lower:
            return 2048
        if "1tb" in lower or "1 tb" in lower or "1024gb" in lower:
            return 1024

        # Cek format RAM/SSD misal 16/512
        ram_ssd_match = re.search(r"\b\d{1,2}\s*(?:gb)?\s*[/,]\s*(\d{3,4})\s*(?:gb)?\b", lower)
        if ram_ssd_match:
            try:
                val = int(ram_ssd_match.group(1))
                if val in [128, 256, 512, 1024, 2048]:
                    return val
            except ValueError:
                pass

        # Cek pola storage umum
        match = re.search(r"\b(2048|1024|512|256|128)\s*(?:gb)?\s*(?:ssd|nvme|m\.2|storage)?\b", lower)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

        return None

    @staticmethod
    def extract_warranty(text: str) -> Tuple[str, str]:
        """
        Ekstraksi asal garansi dan status garansi pabrik.
        Returns: (warranty_type, warranty_status)
        """
        lower = text.lower()
        w_type = "Resmi Indonesia"
        w_status = "Habis (Ex-Resmi)"

        if any(re.search(pat, lower) for pat in WARRANTY_PATTERNS["resmi_indonesia"]):
            w_type = "Resmi Indonesia"
        elif any(re.search(pat, lower) for pat in WARRANTY_PATTERNS["ex_inter"]):
            w_type = "Ex-Inter"
        elif any(re.search(pat, lower) for pat in WARRANTY_PATTERNS["distributor"]):
            w_type = "Garansi Distributor"

        if re.search(r"\b(?:garansi\s*aktif|garansi\s*panjang|on\s*warranty|applecare\+|garansi\s*resmi\s*(?:sd|sampai|\d{4}))\b", lower):
            w_status = "Aktif (Masih Garansi Pabrik)"
        elif re.search(r"\b(?:garansi\s*toko|garansi\s*personal|garansi\s*1\s*bulan|garansi\s*1\s*minggu)\b", lower):
            w_status = "Garansi Toko 1 Bulan"

        return w_type, w_status

    @staticmethod
    def extract_battery_condition(text: str) -> Tuple[str, Optional[int], Optional[int]]:
        """
        Ekstraksi kondisi baterai, cycle count, dan battery health percentage.
        Returns: (battery_condition, battery_health_pct, cycle_count)
        """
        lower = text.lower()
        condition = "Normal Awet"
        cc = None
        bh = None

        # Cycle Count
        for pat in BATTERY_PATTERNS["cycle_count"]:
            m = re.search(pat, lower)
            if m:
                try:
                    val = int(m.group(1))
                    if 0 <= val <= 2500:
                        cc = val
                        break
                except ValueError:
                    pass

        # Health %
        for pat in BATTERY_PATTERNS["health_pct"]:
            m = re.search(pat, lower)
            if m:
                try:
                    val = int(m.group(1))
                    if 30 <= val <= 100:
                        bh = val
                        break
                except ValueError:
                    pass

        # Status baterai
        if any(re.search(pat, lower) for pat in BATTERY_PATTERNS["swollen"]):
            condition = "Baterai Kembung"
        elif any(re.search(pat, lower) for pat in BATTERY_PATTERNS["drop_or_plugged"]):
            condition = "Baterai Drop (Colok Terus)"
        elif bh is not None:
            if bh >= 85:
                condition = "Normal Awet"
            elif bh >= 70:
                condition = "Normal Standar"
            else:
                condition = "Baterai Drop (Colok Terus)"
        elif cc is not None:
            if cc < 300:
                condition = "Normal Awet"
            elif cc < 600:
                condition = "Normal Standar"
            else:
                condition = "Baterai Drop (Colok Terus)"

        return condition, bh, cc

    @staticmethod
    def extract_completeness(text: str) -> str:
        """Ekstraksi kelengkapan unit jual."""
        lower = text.lower()
        if any(re.search(pat, lower) for pat in COMPLETENESS_PATTERNS["batangan"]):
            return "Batangan / Unit Only"
        if any(re.search(pat, lower) for pat in COMPLETENESS_PATTERNS["charger_oem"]):
            return "Charger OEM / Adaptor KW"
        if any(re.search(pat, lower) for pat in COMPLETENESS_PATTERNS["fullset_original"]):
            return "Fullset Original (Dus+Charger Ori)"
        if any(re.search(pat, lower) for pat in COMPLETENESS_PATTERNS["unit_and_charger_original"]):
            return "Unit + Charger Original"
        return "Unit + Charger Original"

    @staticmethod
    def extract_physical_grade(text: str) -> str:
        """Ekstraksi kondisi fisik casing & bodi laptop."""
        lower = text.lower()
        if any(re.search(pat, lower) for pat in PHYSICAL_GRADE_PATTERNS["grade_c"]):
            return "Grade C (Dent/Baret)"
        if any(re.search(pat, lower) for pat in PHYSICAL_GRADE_PATTERNS["grade_b"]):
            return "Grade B (Lecet Wajar)"
        if any(re.search(pat, lower) for pat in PHYSICAL_GRADE_PATTERNS["grade_a_plus"]):
            return "Grade A+ (Like New 99%)"
        if any(re.search(pat, lower) for pat in PHYSICAL_GRADE_PATTERNS["grade_a"]):
            return "Grade A (Mulus 95%)"
        return "Grade A (Mulus 95%)"

    @staticmethod
    def extract_hinge_condition(text: str) -> str:
        """Ekstraksi kondisi fisik engsel (hinge) laptop."""
        lower = text.lower()
        if any(re.search(pat, lower) for pat in HINGE_PATTERNS["broken"]):
            return "Engsel Kendor / Patah"
        return "Normal Kokoh"

    @staticmethod
    def extract_screen_condition(text: str) -> str:
        """Ekstraksi kondisi panel layar & display."""
        lower = text.lower()
        if any(re.search(pat, lower) for pat in SCREEN_PATTERNS["lines_or_flexgate"]):
            return "Layar Bergaris / Flexgate"
        if any(re.search(pat, lower) for pat in SCREEN_PATTERNS["whitespot_tebal"]):
            return "Whitespot Tebal"
        if any(re.search(pat, lower) for pat in SCREEN_PATTERNS["whitespot_tipis"]):
            return "Whitespot Tipis"
        if any(re.search(pat, lower) for pat in SCREEN_PATTERNS["dead_pixel"]):
            return "Dead Pixel"
        return "Normal Jernih"

    @staticmethod
    def extract_keyboard_and_security(text: str) -> Tuple[str, str]:
        """Ekstraksi kondisi keyboard dan keamanan BIOS / MDM."""
        lower = text.lower()
        kb = "Normal Aktif"
        if any(re.search(pat, lower) for pat in KEYBOARD_PATTERNS["broken"]):
            if "backlight" in lower:
                kb = "Backlight Mati"
            else:
                kb = "Tombol Keyboard Minus/Macet"

        sec = "Clean"
        if any(re.search(pat, lower) for pat in BIOS_SECURITY_PATTERNS["locked"]):
            sec = "BIOS Locked / Computrace / MDM"

        return kb, sec

    @classmethod
    def normalize_listing(cls, raw_listing: Dict[str, Any]) -> Dict[str, Any]:
        """Menjalankan pipeline normalisasi menyeluruh untuk 1 raw listing Laptop."""
        title = raw_listing.get("title", "")
        desc = raw_listing.get("description", "")
        combined = f"{title} {desc}"

        clean_price = cls.parse_price(raw_listing.get("price"))
        ram = raw_listing.get("ram_gb") or cls.extract_ram(combined)
        storage = raw_listing.get("storage_gb") or cls.extract_storage(combined)
        w_type, w_status = cls.extract_warranty(combined)
        bat_cond, bh, cc = cls.extract_battery_condition(combined)
        if raw_listing.get("battery_health"):
            bh = raw_listing.get("battery_health")
        if raw_listing.get("cycle_count"):
            cc = raw_listing.get("cycle_count")

        comp = cls.extract_completeness(combined)
        grade = cls.extract_physical_grade(combined)
        hinge = cls.extract_hinge_condition(combined)
        screen = cls.extract_screen_condition(combined)
        kb, sec = cls.extract_keyboard_and_security(combined)

        return {
            "source_platform": raw_listing.get("source_platform", "olx"),
            "external_id": str(raw_listing.get("external_id", "")),
            "url": raw_listing.get("url", ""),
            "title": title.strip(),
            "raw_description": desc.strip(),
            "price": clean_price,
            "claimed_year": raw_listing.get("year"),
            "ram_gb": ram,
            "storage_gb": storage,
            "warranty_type": w_type,
            "warranty_status": w_status,
            "battery_condition": bat_cond,
            "battery_health_pct": bh,
            "battery_cycle_count": cc,
            "completeness": comp,
            "physical_grade": grade,
            "hinge_condition": hinge,
            "screen_condition": screen,
            "keyboard_condition": kb,
            "bios_mdm_status": sec,
            "province": raw_listing.get("province", "DKI Jakarta"),
            "city": raw_listing.get("city", "Jakarta Selatan"),
            "seller_name": raw_listing.get("seller_name", "Individual Seller"),
            "seller_type": raw_listing.get("seller_type", "Individual")
        }
