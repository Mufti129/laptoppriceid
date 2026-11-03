# analytics/buyback_engine.py
from typing import List, Dict, Any, Optional

DEFECT_CATALOG = {
    # 1. Display / Layar
    "lcd_broken": {
        "label": "Layar Pecah / Retak",
        "category": "Layar",
        "icon": "ti-device-desktop-off",
        "cost_standard": 750000,
        "cost_gaming": 1200000,
        "cost_apple": 2200000,
        "description": "Panel retak atau pecah fisik, membutuhkan penggantian modul LCD lengkap."
    },
    "lcd_lines": {
        "label": "Layar Bergaris / Flicker",
        "category": "Layar",
        "icon": "ti-line",
        "cost_standard": 650000,
        "cost_gaming": 1000000,
        "cost_apple": 1800000,
        "description": "Muncul garis vertikal/horizontal atau layar berkedip."
    },
    "white_spot": {
        "label": "White Spot / Dead Pixel",
        "category": "Layar",
        "icon": "ti-sun",
        "cost_standard": 250000,
        "cost_gaming": 350000,
        "cost_apple": 500000,
        "description": "Bercak putih terang atau titik piksel mati pada panel."
    },

    # 2. Baterai & Daya
    "battery_drop": {
        "label": "Baterai Drop / Bocor (<30 mnt)",
        "category": "Baterai",
        "icon": "ti-battery-off",
        "cost_standard": 450000,
        "cost_gaming": 650000,
        "cost_apple": 850000,
        "description": "Kapasitas aus parah, hanya bertahan di bawah 30 menit atau harus selalu colok adaptor."
    },
    "battery_swollen": {
        "label": "Baterai Kembung",
        "category": "Baterai",
        "icon": "ti-alert-circle",
        "cost_standard": 550000,
        "cost_gaming": 750000,
        "cost_apple": 950000,
        "description": "Baterai menggembung dan menekan touchpad/casing (resiko keamanan)."
    },

    # 3. Bodi & Struktur Fisik
    "hinge_broken": {
        "label": "Engsel Patah / Kendor Parah",
        "category": "Bodi",
        "icon": "ti-tools",
        "cost_standard": 450000,
        "cost_gaming": 550000,
        "cost_apple": 800000,
        "description": "Dudukan engsel pecah, kaku, atau patah dari rangka sasis."
    },
    "casing_dent": {
        "label": "Casing Penyok / Retak (Dent)",
        "category": "Bodi",
        "icon": "ti-box",
        "cost_standard": 400000,
        "cost_gaming": 500000,
        "cost_apple": 750000,
        "description": "Penyok dalam pada sudut casing, retak rangka, atau patah plastik pelindung."
    },
    "casing_scratch": {
        "label": "Lecet / Baret Kasar Pemakaian",
        "category": "Bodi",
        "icon": "ti-brush",
        "cost_standard": 200000,
        "cost_gaming": 300000,
        "cost_apple": 400000,
        "description": "Goresan mencolok pada cover atas atau palmrest."
    },

    # 4. Input & Fungsional
    "keyboard_faulty": {
        "label": "Keyboard Eror / Tombol Mati",
        "category": "Input",
        "icon": "ti-keyboard",
        "cost_standard": 300000,
        "cost_gaming": 450000,
        "cost_apple": 750000,
        "description": "Satu atau beberapa tombol tidak merespons atau mencet sendiri."
    },
    "touchpad_broken": {
        "label": "Touchpad Mati / Klik Rusak",
        "category": "Input",
        "icon": "ti-mouse",
        "cost_standard": 350000,
        "cost_gaming": 450000,
        "cost_apple": 650000,
        "description": "Kursor tidak bergerak, gesture macet, atau tombol klik fisik tidak berfungsi."
    },
    "speaker_distorted": {
        "label": "Speaker Sember / Mati Sebelah",
        "category": "Multimedia",
        "icon": "ti-volume-3",
        "cost_standard": 300000,
        "cost_gaming": 400000,
        "cost_apple": 550000,
        "description": "Suara pecah berisik saat volume tinggi atau salah satu kanal mati."
    },
    "webcam_broken": {
        "label": "Kamera / Mikrofon Rusak",
        "category": "Multimedia",
        "icon": "ti-camera-off",
        "cost_standard": 250000,
        "cost_gaming": 350000,
        "cost_apple": 500000,
        "description": "Kamera tidak terdeteksi sistem atau mikrofon internal mati."
    },
    "port_broken": {
        "label": "Port USB / Type-C Rusak",
        "category": "Konektivitas",
        "icon": "ti-usb",
        "cost_standard": 250000,
        "cost_gaming": 350000,
        "cost_apple": 450000,
        "description": "Salah satu port konektor longgar, patah pin, atau tidak membaca perangkat."
    },

    # 5. Aksesoris & Penyimpanan
    "charger_missing": {
        "label": "Tidak Ada Charger (Batangan)",
        "category": "Aksesoris",
        "icon": "ti-plug-off",
        "cost_standard": 250000,
        "cost_gaming": 450000,
        "cost_apple": 550000,
        "description": "Penjualan unit tanpa adaptor pengisi daya bawaan."
    },
    "charger_kw": {
        "label": "Charger KW / Bukan Original",
        "category": "Aksesoris",
        "icon": "ti-plug",
        "cost_standard": 150000,
        "cost_gaming": 250000,
        "cost_apple": 350000,
        "description": "Adaptor pengganti non-resmi yang memiliki resiko voltase tidak stabil."
    },
    "storage_hdd": {
        "label": "Masih Pakai Harddisk (Non-SSD)",
        "category": "Performa",
        "icon": "ti-database",
        "cost_standard": 300000,
        "cost_gaming": 350000,
        "cost_apple": 0,
        "description": "Sistem operasi masih di drive piringan magnetik (wajib migrasi SSD oleh toko)."
    }
}


class BuybackPricingEngine:
    MINIMUM_BUYBACK_FLOOR = 150000  # Nilai transaksi minimum komersial toko (IDR)
    SALVAGE_RATE = 0.125            # 12.5% dari FMV normal untuk kondisi Mati Total

    @classmethod
    def get_defect_deduction(cls, defect_key: str, brand_name: str = "", is_gaming: bool = False) -> int:
        defect = DEFECT_CATALOG.get(defect_key)
        if not defect:
            return 0

        b_upper = (brand_name or "").upper()
        if "APPLE" in b_upper:
            return defect["cost_apple"]
        elif is_gaming:
            return defect["cost_gaming"]
        else:
            return defect["cost_standard"]

    @classmethod
    def calculate_buyback_offer(
        cls,
        base_fmv: float,
        condition_state: str = "NORMAL",
        selected_defects: Optional[List[str]] = None,
        completeness: str = "Unit + Charger Original",
        warranty_status: str = "Tidak Ada Garansi",
        brand_name: str = "",
        is_gaming: bool = False,
        release_year: int = 2022,
        physical_grade: str = "Grade B",
        battery_condition: str = "Normal",
        screen_condition: str = "Normal",
        keyboard_condition: str = "Normal",
        bios_security: str = "Bebas",
        ram_gb: Optional[int] = None,
        storage_gb: Optional[int] = None,
        storage_type: str = "SSD",
        base_ram_gb: int = 8,
        base_storage_gb: int = 512,
        **kwargs
    ) -> Dict[str, Any]:
        selected_defects = list(selected_defects or [])
        b_upper = (brand_name or "").upper()
        is_apple = "APPLE" in b_upper

        if is_apple:
            margin_rate = 0.22
        elif is_gaming:
            margin_rate = 0.28
        else:
            margin_rate = 0.25

        # Incorporate component grade inputs into defect list if not already present
        if "Grade C" in physical_grade and "casing_dent" not in selected_defects:
            selected_defects.append("casing_dent")
        elif "Grade D" in physical_grade:
            if "casing_dent" not in selected_defects:
                selected_defects.append("casing_dent")
            if "hinge_broken" not in selected_defects:
                selected_defects.append("hinge_broken")

        if any(w in battery_condition for w in ["Drop", "<30", "<45"]) and "battery_drop" not in selected_defects:
            selected_defects.append("battery_drop")
        elif "Kembung" in battery_condition and "battery_swollen" not in selected_defects:
            selected_defects.append("battery_swollen")

        if "White Spot" in screen_condition and "white_spot" not in selected_defects:
            selected_defects.append("white_spot")
        elif any(w in screen_condition for w in ["Garis", "Flicker"]) and "lcd_lines" not in selected_defects:
            selected_defects.append("lcd_lines")
        elif any(w in screen_condition for w in ["Pecah", "Retak", "Blank", "Tompel"]) and "lcd_broken" not in selected_defects:
            selected_defects.append("lcd_broken")

        if "Tombol" in keyboard_condition and "keyboard_faulty" not in selected_defects:
            selected_defects.append("keyboard_faulty")
        elif "Touchpad" in keyboard_condition and "touchpad_broken" not in selected_defects:
            selected_defects.append("touchpad_broken")
        elif "Keduanya" in keyboard_condition:
            if "keyboard_faulty" not in selected_defects:
                selected_defects.append("keyboard_faulty")
            if "touchpad_broken" not in selected_defects:
                selected_defects.append("touchpad_broken")

        if "HDD" in storage_type and "storage_hdd" not in selected_defects:
            selected_defects.append("storage_hdd")

        # Hardware spec adjustments (RAM / Storage capacity adjustments vs baseline)
        hw_adj = 0
        if ram_gb is not None:
            if ram_gb > base_ram_gb:
                hw_adj += min(1200000, ((ram_gb - base_ram_gb) // 8) * (300000 if is_gaming else 200000))
            elif ram_gb < base_ram_gb:
                hw_adj -= min(400000, ((base_ram_gb - ram_gb) // 4) * 150000)

        if storage_gb is not None:
            if storage_gb > base_storage_gb:
                hw_adj += min(1500000, ((storage_gb - base_storage_gb) // 512) * 350000)
            elif storage_gb < base_storage_gb:
                hw_adj -= min(400000, ((base_storage_gb - storage_gb) // 256) * 150000)

        adjusted_base_fmv = max(cls.MINIMUM_BUYBACK_FLOOR * 2, base_fmv + hw_adj)

        if condition_state.upper() == "MATI_TOTAL":
            salvage_raw = adjusted_base_fmv * cls.SALVAGE_RATE
            range_step = 500000 if is_gaming or is_apple else 250000
            cash_offer_low = max(cls.MINIMUM_BUYBACK_FLOOR, round(salvage_raw / 50000) * 50000)
            cash_offer_high = cash_offer_low + range_step
            trade_in_val = round((cash_offer_low * 1.10) / 50000) * 50000

            is_eligible = cash_offer_low >= cls.MINIMUM_BUYBACK_FLOOR

            return {
                "condition_state": "MATI_TOTAL",
                "base_fmv": round(adjusted_base_fmv),
                "is_eligible": is_eligible,
                "ineligibility_reason": None if is_eligible else "Laptop mati total dengan nilai sisa komponen di bawah ambang batas komersial.",
                "retail_c2c_price": round(salvage_raw * 1.3),
                "cash_offer_low": cash_offer_low,
                "cash_offer_high": cash_offer_high,
                "cash_offer_mid": (cash_offer_low + cash_offer_high) // 2,
                "trade_in_credit": trade_in_val,
                "total_deductions": 0,
                "deductions_breakdown": [{"name": "Salvage Value (Komponen Kanibalan Motherboard Mati)", "cost": round(adjusted_base_fmv * (1 - cls.SALVAGE_RATE))}],
                "margin_rate_pct": 0,
                "warranty_bonus": 0,
                "completeness_bonus": 0,
                "hw_spec_adj": hw_adj
            }

        deductions_breakdown = []
        total_defect_cost = 0
        for d_key in selected_defects:
            cost = cls.get_defect_deduction(d_key, brand_name=brand_name, is_gaming=is_gaming)
            item_info = DEFECT_CATALOG.get(d_key, {})
            label = item_info.get("label", d_key)
            deductions_breakdown.append({"key": d_key, "name": label, "cost": cost, "category": item_info.get("category", "Umum")})
            total_defect_cost += cost

        if "Terkunci" in bios_security:
            bios_cost = 400000 if not is_apple else 800000
            deductions_breakdown.append({"key": "bios_locked", "name": "Penalti Kunci BIOS / MDM (Biaya Unlock Servis)", "cost": bios_cost, "category": "Keamanan"})
            total_defect_cost += bios_cost

        warranty_bonus = 0
        if "Garansi Resmi > 6 Bulan" in warranty_status:
            warranty_bonus = round(adjusted_base_fmv * 0.05)
        elif "Garansi Resmi < 6 Bulan" in warranty_status:
            warranty_bonus = round(adjusted_base_fmv * 0.025)

        completeness_adj = 0
        if "Fullset" in completeness:
            completeness_adj = round(adjusted_base_fmv * 0.03)
        elif "Batangan" in completeness:
            if "charger_missing" not in selected_defects and "charger_kw" not in selected_defects:
                charger_cost = cls.get_defect_deduction("charger_missing", brand_name=brand_name, is_gaming=is_gaming)
                deductions_breakdown.append({"key": "charger_missing", "name": "Penalti Unit Batangan (Tanpa Charger)", "cost": charger_cost, "category": "Aksesoris"})
                total_defect_cost += charger_cost

        physical_grade_bonus = round(adjusted_base_fmv * 0.03) if "Grade A" in physical_grade else 0
        battery_bonus = 150000 if "Sangat Sehat" in battery_condition else 0

        total_bonuses = warranty_bonus + completeness_adj + physical_grade_bonus + battery_bonus

        retail_c2c = max(cls.MINIMUM_BUYBACK_FLOOR, adjusted_base_fmv - total_defect_cost + total_bonuses)

        store_margin_amount = adjusted_base_fmv * margin_rate
        net_cash_base = adjusted_base_fmv - store_margin_amount - total_defect_cost + total_bonuses

        is_eligible = net_cash_base >= cls.MINIMUM_BUYBACK_FLOOR

        cash_mid = round(net_cash_base / 50000) * 50000
        cash_low = max(cls.MINIMUM_BUYBACK_FLOOR, cash_mid - (250000 if not is_gaming else 500000))
        cash_high = max(cls.MINIMUM_BUYBACK_FLOOR + 250000, cash_mid + (250000 if not is_gaming else 500000))

        trade_in_val = round((cash_high * 1.08) / 50000) * 50000

        return {
            "condition_state": "NORMAL",
            "base_fmv": round(adjusted_base_fmv),
            "is_eligible": is_eligible,
            "ineligibility_reason": None if is_eligible else "Akumulasi kerusakan melebihi nilai pasar laptop sehingga tidak ekonomis untuk dibeli komersial.",
            "retail_c2c_price": round(retail_c2c),
            "cash_offer_low": cash_low,
            "cash_offer_high": cash_high,
            "cash_offer_mid": cash_mid,
            "trade_in_credit": trade_in_val,
            "total_deductions": total_defect_cost,
            "deductions_breakdown": deductions_breakdown,
            "margin_rate_pct": int(margin_rate * 100),
            "warranty_bonus": warranty_bonus,
            "completeness_bonus": completeness_adj,
            "physical_grade_bonus": physical_grade_bonus,
            "battery_bonus": battery_bonus,
            "hw_spec_adj": hw_adj
        }
