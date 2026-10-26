"""
Kamus & Taksonomi Generasi Model / Seri Laptop (2010 - 2026).
Mencakup 10 Brand: Apple, Lenovo, ASUS, Acer, HP, Dell, MSI, Axioo, Huawei, Microsoft.
Fungsi:
1. Menentukan label generasi manufaktur (Gen 1 s/d Gen 12, Apple Silicon M1-M4, G1-G11, R1-R7, v1-v2).
2. Membersihkan nama model kanonikal dari redundansi imbuhan tahun (YYYY).
"""

import re

def resolve_generation_and_canonical_name(brand_name: str, series_name: str, current_name: str, release_year: int = 2023, processor_model: str = "", gpu_model: str = "", chassis_code: str = "") -> tuple[str, str]:
    b = (brand_name or "").strip().upper()
    s = (series_name or "").strip()
    m = (current_name or "").strip()
    cpu = (processor_model or "").strip().upper()
    gpu = (gpu_model or "").strip().upper()
    chassis = (chassis_code or "").strip()
    yr = int(release_year) if release_year else 2023

    # Bersihkan nama dasar dari suffix tahun seperti (2010) atau 2010
    base_name = re.sub(r"\s*\(\d{4}\)$", "", m).strip()
    base_name = re.sub(r"\s+\d{4}$", "", base_name).strip()

    # 1. APPLE MACBOOK
    if b == "APPLE" or "MACBOOK" in m.upper():
        if "M4" in m.upper() or "M4" in cpu:
            gen = "Apple Silicon M4"
            clean_name = m.replace(f" ({yr})", "").strip()
            return clean_name, gen
        if "M3" in m.upper() or "M3" in cpu:
            gen = "Apple Silicon M3"
            clean_name = m.replace(f" ({yr})", "").strip()
            return clean_name, gen
        if "M2" in m.upper() or "M2" in cpu:
            gen = "Apple Silicon M2"
            clean_name = m.replace(f" ({yr})", "").strip()
            return clean_name, gen
        if "M1" in m.upper() or "M1" in cpu:
            gen = "Apple Silicon M1"
            clean_name = m.replace(f" ({yr})", "").strip()
            return clean_name, gen
        
        # Era Intel MacBook (2010 - 2020)
        clean_name = base_name
        if "Air 13" in m:
            if yr >= 2018:
                return "MacBook Air 13 Retina", "Retina Intel"
            elif yr >= 2012:
                return "MacBook Air 13 (A1466)", "Unibody Thin"
            else:
                return "MacBook Air 13 Unibody", "Unibody Intel"
        if "Air 11" in m:
            return "MacBook Air 11 (A1465)", "Unibody Thin"
        if "12 Retina" in m:
            return "MacBook 12 Retina", "Retina Ultra-Thin"
        if "Pro 16" in m:
            return "MacBook Pro 16 Intel (A2141)", "Touch Bar Intel"
        if "Pro 15" in m:
            if yr >= 2016:
                return "MacBook Pro 15 Touch Bar", "Touch Bar Intel"
            elif yr >= 2012:
                return "MacBook Pro 15 Retina", "Retina Intel"
            else:
                return "MacBook Pro 15 Unibody", "Unibody Intel"
        if "Pro 13" in m:
            if yr >= 2016:
                return "MacBook Pro 13 Touch Bar", "Touch Bar Intel"
            elif yr >= 2012:
                return "MacBook Pro 13 Retina", "Retina Intel"
            else:
                return "MacBook Pro 13 Unibody", "Unibody Intel"
        if "Pro 17" in m:
            return "MacBook Pro 17 Unibody", "Unibody Intel"

        return clean_name, "Intel Core Legacy"

    # 2. LENOVO
    if b == "LENOVO":
        # ThinkPad T-Series
        if "T-SERIES" in base_name.upper() or "T14" in base_name.upper() or "T480" in base_name.upper():
            if yr >= 2024: return "ThinkPad T14 Gen 5", "Gen 5"
            if yr == 2023: return "ThinkPad T14 Gen 4", "Gen 4"
            if yr == 2022: return "ThinkPad T14 Gen 3", "Gen 3"
            if yr == 2021: return "ThinkPad T14 Gen 2", "Gen 2"
            if yr == 2020: return "ThinkPad T14 Gen 1", "Gen 1"
            if yr == 2019: return "ThinkPad T490", "Classic Gen 9"
            if yr == 2018: return "ThinkPad T480", "Classic Gen 8"
            if yr == 2017: return "ThinkPad T470", "Classic Gen 7"
            if yr == 2016: return "ThinkPad T460", "Classic Gen 6"
            if yr == 2015: return "ThinkPad T450", "Classic Gen 5"
            if yr in [2013, 2014]: return "ThinkPad T440", "Classic Gen 4"
            if yr == 2012: return "ThinkPad T430", "Classic Gen 3"
            if yr == 2011: return "ThinkPad T420", "Classic Gen 2"
            return "ThinkPad T410", "Classic Gen 1"

        # ThinkPad X1 Carbon
        if "X1 CARBON" in base_name.upper():
            if yr >= 2024: return "ThinkPad X1 Carbon Gen 12", "Gen 12"
            if yr == 2023: return "ThinkPad X1 Carbon Gen 11", "Gen 11"
            if yr == 2022: return "ThinkPad X1 Carbon Gen 10", "Gen 10"
            if yr == 2021: return "ThinkPad X1 Carbon Gen 9", "Gen 9"
            if yr == 2020: return "ThinkPad X1 Carbon Gen 8", "Gen 8"
            if yr == 2019: return "ThinkPad X1 Carbon Gen 7", "Gen 7"
            if yr == 2018: return "ThinkPad X1 Carbon Gen 6", "Gen 6"
            if yr == 2017: return "ThinkPad X1 Carbon Gen 5", "Gen 5"
            if yr == 2016: return "ThinkPad X1 Carbon Gen 4", "Gen 4"
            if yr == 2015: return "ThinkPad X1 Carbon Gen 3", "Gen 3"
            if yr in [2013, 2014]: return "ThinkPad X1 Carbon Gen 2", "Gen 2"
            return "ThinkPad X1 Carbon Gen 1", "Gen 1"

        # ThinkPad X-Series (X2xx / X13)
        if "X-SERIES" in base_name.upper() or "X13" in base_name.upper() or "X280" in base_name.upper():
            if yr >= 2023: return "ThinkPad X13 Gen 4", "Gen 4"
            if yr == 2022: return "ThinkPad X13 Gen 3", "Gen 3"
            if yr == 2021: return "ThinkPad X13 Gen 2", "Gen 2"
            if yr == 2020: return "ThinkPad X13 Gen 1", "Gen 1"
            if yr == 2019: return "ThinkPad X390", "Classic Gen 9"
            if yr == 2018: return "ThinkPad X280", "Classic Gen 8"
            if yr == 2017: return "ThinkPad X270", "Classic Gen 7"
            if yr == 2016: return "ThinkPad X260", "Classic Gen 6"
            if yr == 2015: return "ThinkPad X250", "Classic Gen 5"
            if yr in [2013, 2014]: return "ThinkPad X240", "Classic Gen 4"
            if yr == 2012: return "ThinkPad X230", "Classic Gen 3"
            if yr == 2011: return "ThinkPad X220", "Classic Gen 2"
            return "ThinkPad X201", "Classic Gen 1"

        # ThinkPad E-Series (E14 / E4xx)
        if "E-SERIES" in base_name.upper() or "E14" in base_name.upper():
            if yr >= 2024: return "ThinkPad E14 Gen 6", "Gen 6"
            if yr == 2023: return "ThinkPad E14 Gen 5", "Gen 5"
            if yr == 2022: return "ThinkPad E14 Gen 4", "Gen 4"
            if yr == 2021: return "ThinkPad E14 Gen 3", "Gen 3"
            if yr == 2020: return "ThinkPad E14 Gen 2", "Gen 2"
            if yr == 2019: return "ThinkPad E490", "Gen E490"
            if yr == 2018: return "ThinkPad E480", "Gen E480"
            return f"ThinkPad E4{yr-2010+10}", f"Gen E4xx"

        # ThinkPad P-Series Workstation
        if "P-SERIES" in base_name.upper() or "WORKSTATION" in base_name.upper():
            if yr >= 2023: return "ThinkPad P16 Gen 2", "Gen 2"
            if yr == 2022: return "ThinkPad P16 Gen 1", "Gen 1"
            if yr >= 2020: return f"ThinkPad P15 Gen {yr-2019}", f"Gen {yr-2019}"
            if yr >= 2016: return f"ThinkPad P5{yr-2016}", f"Gen P5{yr-2016}"
            return "ThinkPad W530 Workstation", "Classic W-Series"

        # Legion Gaming
        if "LEGION 5" in base_name.upper():
            if yr >= 2024: return "Legion Pro 5 16IRX9", "Gen 9"
            if yr == 2023: return "Legion Pro 5 16IRX8", "Gen 8"
            if yr == 2022: return "Legion 5 Pro 16IAH7", "Gen 7"
            if yr == 2021: return "Legion 5 15ACH6", "Gen 6"
            if yr == 2020: return "Legion 5 15IMH05", "Gen 5"
            if yr == 2019: return "Legion Y540", "Gen Y540"
            if yr == 2018: return "Legion Y530", "Gen Y530"
            if yr == 2017: return "Legion Y520", "Gen Y520"
            return "Lenovo Y50-70 Gaming", "Gen Y-Series"

        if "LEGION 7" in base_name.upper():
            if yr >= 2024: return "Legion Pro 7i 16IRX9", "Gen 9"
            if yr == 2023: return "Legion Pro 7i 16IRX8", "Gen 8"
            if yr == 2022: return "Legion 7 16IAH7", "Gen 7"
            if yr == 2021: return "Legion 7 16ACHg6", "Gen 6"
            if yr == 2020: return "Legion 7 15IMH05", "Gen 5"
            return "Legion Y740 Gaming", "Gen Y740"

        # LOQ Series
        if "LOQ" in base_name.upper():
            if yr >= 2024: return "Lenovo LOQ 15IRX9", "Gen 9"
            return "Lenovo LOQ 15IRH8", "Gen 8"

        # IdeaPad & Yoga
        if "SLIM 3" in base_name.upper():
            gen_num = max(1, yr - 2016)
            return "IdeaPad Slim 3", f"Gen {gen_num}"
        if "SLIM 5" in base_name.upper():
            gen_num = max(1, yr - 2016)
            return "IdeaPad Slim 5", f"Gen {gen_num}"
        if "IDEAPAD GAMING" in base_name.upper():
            return "IdeaPad Gaming 3", f"Gen {max(1, yr - 2019)}"
        if "YOGA" in base_name.upper():
            gen_num = max(1, yr - 2015)
            clean = "Yoga Slim 7" if "SLIM" in base_name.upper() else "Yoga 9i"
            return clean, f"Gen {gen_num}"

    # 3. ASUS
    if b == "ASUS":
        if "STRIX" in base_name.upper():
            if yr >= 2024: return f"ROG Strix G16 {chassis or G614JVR}", "Gen 2024 Refresh"
            if yr == 2023: return f"ROG Strix G16 {chassis or G614JV}", "Gen 2023 (16\")"
            if yr >= 2021: return "ROG Strix G15 G513", "Gen 2021 (RTX 30)"
            if yr >= 2019: return "ROG Strix G531", "Gen Strix III"
            return "ROG Strix GL503", "Gen GL-Series"
        if "TUF" in base_name.upper():
            if "A15" in base_name.upper() or "FA50" in chassis.upper():
                if yr >= 2022: return "TUF Gaming A15 FA507", "Gen 4 (FA507)"
                if yr >= 2020: return "TUF Gaming A15 FA506", "Gen 3 (FA506)"
                return "TUF Gaming FX505DY", "Gen 2 (FX505)"
            else:
                if yr >= 2022: return "TUF Gaming F15 FX507", "Gen 4 (FX507)"
                if yr >= 2020: return "TUF Gaming F15 FX506", "Gen 3 (FX506)"
                if yr == 2019: return "TUF Gaming FX505", "Gen 2 (FX505)"
                return "TUF Gaming FX504", "Gen 1 (FX504)"
        if "ZEPHYRUS G14" in base_name.upper():
            if yr >= 2024: return "ROG Zephyrus G14 GA403", "Gen 2024 OLED"
            if yr == 2023: return "ROG Zephyrus G14 GA402X", "Gen 2023 (RTX 40)"
            if yr == 2022: return "ROG Zephyrus G14 GA402R", "Gen 2022 (Radeon)"
            return "ROG Zephyrus G14 GA401", "Gen 1 (GA401)"
        if "ZEPHYRUS G16" in base_name.upper() or "M16" in base_name.upper():
            if yr >= 2024: return "ROG Zephyrus G16 GU605", "Gen 2024 OLED"
            if yr == 2023: return "ROG Zephyrus G16 GU604", "Gen 2023 (16\")"
            return "ROG Zephyrus M16 GU603", "Gen 2021-2022"
        if "FLOW" in base_name.upper():
            return "ROG Flow X13 / Z13", f"Gen {yr-2020}" if yr >= 2021 else "Gen 1"
        if "ZENBOOK 14" in base_name.upper():
            if yr >= 2024: return "ZenBook 14 OLED UX3405", "Core Ultra Gen 1"
            if yr == 2023: return "ZenBook 14 OLED UX3404", "Gen 13 (UX3404)"
            if yr == 2022: return "ZenBook 14 OLED UX3402", "Gen 12 (UX3402)"
            if yr >= 2020: return "ZenBook 14 UX425", "Gen 11 (UX425)"
            return "ZenBook 14 UX430", "Classic UX"
        if "ZENBOOK DUO" in base_name.upper():
            if yr >= 2024: return "ZenBook Duo OLED UX8406", "Gen 2024 Dual OLED"
            return "ZenBook Duo UX482", "Gen 2 (UX482)"

    # 4. HP (HEWLETT-PACKARD)
    if b == "HP":
        if "ELITEBOOK 840" in base_name.upper():
            if yr >= 2024: return "EliteBook 840 G11", "G11"
            g_num = max(1, yr - 2013 + 1)
            if yr == 2013: g_num = 1
            elif yr in [2014, 2015]: g_num = 2
            elif yr == 2016: g_num = 3
            elif yr == 2017: g_num = 4
            elif yr == 2018: g_num = 5
            elif yr == 2019: g_num = 6
            elif yr == 2020: g_num = 7
            elif yr == 2021: g_num = 8
            elif yr == 2022: g_num = 9
            elif yr == 2023: g_num = 10
            return f"EliteBook 840 G{g_num}", f"G{g_num}"
        if "OMEN" in base_name.upper():
            if yr >= 2023: return "OMEN 16 (16-wf0000)", "Gen 3 (16\")"
            if yr >= 2021: return "OMEN 16 (16-b0000)", "Gen 1-2 (16\")"
            return "OMEN 15 Gaming", f"Gen 15 (201{yr-2010})"
        if "VICTUS" in base_name.upper():
            clean = "Victus 16" if "16" in base_name else "Victus 15"
            return clean, "Gen 2" if yr >= 2023 else "Gen 1"
        if "PAVILION" in base_name.upper():
            clean = re.sub(r"\s*\(\d{4}\)$", "", base_name).strip()
            return clean, f"Gen {max(1, yr - 2016)}"
        if "ENVY" in base_name.upper():
            return "HP Envy 16" if "16" in base_name else "HP Envy 14", f"Gen {max(1, yr - 2018)}"

    # 5. DELL
    if b == "DELL":
        if "XPS 13" in base_name.upper():
            if yr >= 2024: return "XPS 13 9340", "Gen 9340 (Core Ultra)"
            if yr in [2022, 2023]: return "XPS 13 Plus 9320", "Gen 9320 Plus"
            if yr == 2021: return "XPS 13 9310", "Gen 9310"
            if yr == 2020: return "XPS 13 9300", "Gen 9300 (16:10)"
            if yr == 2019: return "XPS 13 9380", "Gen 9380"
            if yr == 2018: return "XPS 13 9370", "Gen 9370"
            if yr == 2017: return "XPS 13 9360", "Gen 9360"
            if yr == 2016: return "XPS 13 9350", "Gen 9350"
            if yr == 2015: return "XPS 13 9343", "Gen 9343"
            return "XPS 13 9333", "Gen 9333"
        if "XPS 15" in base_name.upper():
            if yr >= 2023: return "XPS 15 9530", "Gen 9530"
            if yr == 2022: return "XPS 15 9520", "Gen 9520"
            if yr in [2020, 2021]: return "XPS 15 9500", "Gen 9500"
            return f"XPS 15 95{min(7, yr-2010)}0", "Gen 95xx"
        if "ALIENWARE" in base_name.upper():
            if yr >= 2023: return "Alienware m16 R1", "Revision 1 (16\")"
            if yr in [2021, 2022]: return "Alienware m15 R5/R6", "Revision 5-6"
            if yr in [2019, 2020]: return "Alienware m15 R2/R3", "Revision 2-3"
            if yr == 2018: return "Alienware m15 R1", "Revision 1"
            return "Alienware 15 R3", "Alienware 15 Classic"
        if "DELL G" in base_name.upper():
            clean = "Dell G16" if "G16" in base_name.upper() else "Dell G15"
            return clean, f"Gen {max(1, yr - 2017)}"
        if "INSPIRON" in base_name.upper():
            clean = "Inspiron 15" if "15" in base_name else "Inspiron 14"
            return clean, f"Gen {max(1, yr - 2017)}"

    # 6. ACER
    if b == "ACER":
        if "NITRO 5" in base_name.upper():
            if yr in [2022, 2023]: return "Nitro 5 AN515-58", "Gen AN515-58"
            if yr == 2021: return "Nitro 5 AN515-57", "Gen AN515-57"
            if yr == 2020: return "Nitro 5 AN515-55", "Gen AN515-55"
            if yr == 2019: return "Nitro 5 AN515-54", "Gen AN515-54"
            if yr == 2018: return "Nitro 5 AN515-52", "Gen AN515-52"
            return "Nitro 5 AN515-51", "Gen AN515-51"
        if "NITRO 16" in base_name.upper():
            return "Nitro 16 AN16-51", "Gen AN16-51"
        if "NITRO V" in base_name.upper():
            return "Nitro V 15 ANV15-51", "Gen ANV15-51"
        if "PREDATOR HELIOS" in base_name.upper():
            if yr >= 2024: return "Predator Helios 16 PH16-72", "Gen 2024 (Neo/Helios)"
            if yr == 2023: return "Predator Helios Neo 16 PHN16-71", "Gen 2023 (Neo)"
            return "Predator Helios 300 PH315", f"Helios 300 Gen {max(1, yr-2017)}"
        if "SWIFT GO" in base_name.upper():
            if yr >= 2024: return "Swift Go 14 SFG14-72", "Gen 2024 (Core Ultra)"
            return "Swift Go 14 SFG14-71", "Gen 2023 (13th Gen)"
        if "SWIFT 3" in base_name.upper() or "SWIFT" in base_name.upper():
            clean = re.sub(r"\s*\(\d{4}\)$", "", base_name).strip()
            return clean, f"Gen {max(1, yr - 2016)}"

    # 7. MSI
    if b == "MSI":
        clean = re.sub(r"\s*\(\d{4}\)$", "", base_name).strip()
        if "14V" in chassis.upper() or "B14V" in chassis.upper():
            return clean, "Intel 14th Gen"
        if "13V" in chassis.upper() or "B13V" in chassis.upper():
            return clean, "Intel 13th Gen"
        if "12V" in chassis.upper() or "A12V" in chassis.upper():
            return clean, "Intel 12th Gen"
        if "11U" in chassis.upper() or "11V" in chassis.upper():
            return clean, "Intel 11th Gen"
        if yr >= 2024: return clean, "Intel 14th Gen"
        if yr == 2023: return clean, "Intel 13th Gen"
        if yr == 2022: return clean, "Intel 12th Gen"
        if yr == 2021: return clean, "Intel 11th Gen"
        return clean, f"Intel Gen {max(1, yr - 2009)}"

    # 8. AXIOO
    if b == "AXIOO":
        clean = re.sub(r"\s*\(\d{4}\)$", "", base_name).strip()
        if "PONGO 760" in clean.upper():
            if yr >= 2024 or "V2" in chassis.upper(): return "Axioo Pongo 760 v2", "Gen 3 (v2)"
            return "Axioo Pongo 760 v1", "Gen 2 (v1)"
        if "PONGO 960" in clean.upper():
            return "Axioo Pongo 960 v1", "Gen 2 (v1)"
        if "PONGO 725" in clean.upper():
            return "Axioo Pongo 725 v1", "Gen 2 (v1)"
        if "HYPE" in clean.upper():
            return clean, "Hype Series Gen 1"
        return clean, f"Axioo Gen {max(1, yr - 2018)}"

    # 9. HUAWEI
    if b == "HUAWEI":
        clean = re.sub(r"\s*\(\d{4}\)$", "", base_name).strip()
        return clean, f"Gen {yr}"

    # 10. MICROSOFT SURFACE
    if b == "MICROSOFT" or "SURFACE" in base_name.upper():
        clean = re.sub(r"\s*\(\d{4}\)$", "", base_name).strip()
        match_num = re.search(r"(Laptop\s*\d|Pro\s*\d+|Go\s*\d+|Studio\s*\d*)", clean, re.IGNORECASE)
        if match_num:
            return clean, f"Surface {match_num.group(1).title()}"
        return clean, f"Surface Gen {yr}"

    # FALLBACK
    clean = re.sub(r"\s*\(\d{4}\)$", "", base_name).strip()
    return clean, f"Gen {yr}"
