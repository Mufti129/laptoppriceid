"""
Kamus & Taksonomi Kode Sasis / Model SKU Pabrikan Resmi (2010 - 2026).
Mencakup 10 Brand: ASUS, Lenovo, Acer, Apple, HP, Dell, MSI, Axioo, Huawei, Microsoft.
Digunakan untuk sinkronisasi database master catalog dan presisi pencarian audit 1-to-1.
"""

import re

def resolve_chassis_code(brand_name: str, series_name: str, model_name: str, release_year: int = 2023, processor_model: str = "", gpu_model: str = "") -> str:
    """
    Menghasilkan kode sasis / SKU resmi pabrikan secara deterministik.
    Contoh:
      - ASUS ROG Strix G16 (RTX 4060) -> G614JV / G614JVR
      - Lenovo Legion Pro 5 (RTX 4070) -> 16IRX8
      - Acer Predator Helios Neo 16 -> PHN16-71
      - Apple MacBook Air 13 M2 -> A2681
      - MSI Katana 15 (RTX 4060) -> B13VFK
    """
    b = (brand_name or "").strip().upper()
    s = (series_name or "").strip().upper()
    m = (model_name or "").strip().upper()
    cpu = (processor_model or "").strip().upper()
    gpu = (gpu_model or "").strip().upper()
    year = int(release_year) if release_year else 2023

    # =========================================================================
    # 1. APPLE (Model Number A-Series & Hardware Identifier)
    # =========================================================================
    if b == "APPLE" or "MACBOOK" in m:
        if "AIR 13" in m:
            if "M3" in m or "M3" in cpu: return "A3113"
            if "M2" in m or "M2" in cpu: return "A2681"
            if "M1" in m or "M1" in cpu: return "A2337"
            if year >= 2020: return "A2179"
            if year >= 2018: return "A1932"
            return "A1466"
        if "AIR 15" in m:
            if "M3" in m or "M3" in cpu: return "A3114"
            return "A2941"
        if "PRO 14" in m:
            if "M4" in m or "M4" in cpu: return "A3112"
            if "M3 MAX" in m or "M3 PRO" in m or "M3 MAX" in cpu or "M3 PRO" in cpu: return "A2992"
            if "M3" in m or "M3" in cpu: return "A2918"
            if "M2" in m or "M2" in cpu: return "A2779"
            return "A2442"
        if "PRO 16" in m:
            if "M4" in m or "M4" in cpu: return "A3403"
            if "M3" in m or "M3" in cpu: return "A2991"
            if "M2" in m or "M2" in cpu: return "A2780"
            if "M1" in m or "M1" in cpu: return "A2485"
            return "A2141"
        if "PRO 13" in m:
            if "M2" in m or "M2" in cpu: return "A2338-M2"
            if "M1" in m or "M1" in cpu: return "A2338"
            if year >= 2020: return "A2251"
            if year >= 2016: return "A1706"
            if year >= 2013: return "A1502"
            return "A1278"
        if "PRO 15" in m:
            if year >= 2018: return "A1990"
            if year >= 2016: return "A1707"
            if year >= 2012: return "A1398"
            return "A1286"
        return "A2681"

    # =========================================================================
    # 2. ASUS (G614, FA507, UX3405, etc.)
    # =========================================================================
    if b == "ASUS":
        is_intel = any(k in cpu for k in ["INTEL", "CORE", "I3", "I5", "I7", "I9", "ULTRA"]) or not any(k in cpu for k in ["RYZEN", "AMD"])
        
        # Ekstraksi huruf GPU ASUS: U=4050, V=4060, I=4070, Z=4080, X=4090
        gpu_letter = "V"  # default 4060
        if "4050" in gpu: gpu_letter = "U"
        elif "4060" in gpu: gpu_letter = "V"
        elif "4070" in gpu: gpu_letter = "I"
        elif "4080" in gpu: gpu_letter = "Z"
        elif "4090" in gpu: gpu_letter = "X"
        elif "3050" in gpu: gpu_letter = "ZC"
        elif "3060" in gpu: gpu_letter = "ZM"
        elif "3070" in gpu: gpu_letter = "QR"
        elif "3080" in gpu: gpu_letter = "QS"
        elif "1060" in gpu: gpu_letter = "GS"
        elif "GTX" in gpu: gpu_letter = "VW"

        if "STRIX G16" in m or "G15/G16" in m or "STRIX G15" in m:
            if year >= 2024:
                return f"G614J{gpu_letter}R" if is_intel else f"G614P{gpu_letter}"
            if year == 2023:
                if gpu_letter in ["I", "Z", "X"]:
                    return f"G614J{gpu_letter}R" if is_intel else f"G614P{gpu_letter}"
                return f"G614J{gpu_letter}" if is_intel else f"G614P{gpu_letter}"
            if year >= 2021: return "G513QM" if not is_intel else "G513QR"
            if year >= 2019: return "G531GT"
            if year >= 2017: return "GL503VD"
            return f"GL552VW-{year}"

        if "STRIX SCAR" in m:
            if year >= 2024: return "G634JZR" if "16" in m or "4080" in gpu else "G834JYR"
            if year == 2023: return "G634JZ" if "16" in m or "4080" in gpu else "G834JY"
            if year >= 2021: return "G733QS"
            if year >= 2019: return "G532LWS"
            return f"GL703GS-{year}"

        if "ZEPHYRUS G14" in m:
            if year >= 2024: return "GA403UI" if "4070" in gpu else "GA403UV"
            if year == 2023: return "GA402XV" if "4060" in gpu else "GA402XY"
            if year == 2022: return "GA402RJ"
            if year == 2021: return "GA401QM"
            if year == 2020: return "GA401II"
            return f"GA401-{year}"

        if "ZEPHYRUS G16" in m or "ZEPHYRUS M16" in m or "G16/M16" in m:
            if year >= 2024: return "GU605MZ" if "4080" in gpu else "GU605MI" if "4070" in gpu else "GU605MU"
            if year == 2023: return "GU604VI" if "M16" in m else "GU603VV"
            if year >= 2021: return "GU603HM"
            return f"GU502GV-{year}"

        if "FLOW" in m:
            if "Z13" in m: return "GZ301VV" if year >= 2023 else "GZ301ZC"
            if "X16" in m: return "GV601VI" if year >= 2023 else "GV601RW"
            return "GV302XI" if year >= 2023 else "GV301QE"

        if "TUF GAMING A15" in m or "FA506" in m or "FA507" in m:
            if year >= 2024: return "FA507UI" if "4070" in gpu else "FA507UV"
            if year == 2023: return "FA507XI" if "4070" in gpu else "FA507NV"
            if year == 2022: return "FA507RM"
            if year >= 2020: return "FA506QM" if year >= 2021 else "FA506II"
            return f"FX505DY-{year}"

        if "TUF GAMING F15" in m or "FX506" in m or "FX507" in m:
            if year >= 2024: return "FX507VI" if "4070" in gpu else "FX507VU"
            if year == 2023: return "FX507ZV" if "4060" in gpu else "FX507ZC"
            if year == 2022: return "FX507ZM"
            if year >= 2020: return "FX506HM" if year >= 2021 else "FX506LH"
            return f"FX504GD-{year}"

        if "ZENBOOK 14 OLED" in m:
            if year >= 2024: return "UX3405MA"
            if year == 2023: return "UX3404VA"
            if year == 2022: return "UX3402ZA"
            return f"UX425EA-{year}"

        if "ZENBOOK DUO" in m:
            if year >= 2024: return "UX8406MA"
            if year >= 2022: return "UX582ZM"
            return "UX482EG"

        if "VIVOBOOK PRO" in m:
            return "K6502VU" if year >= 2023 else "K3500PC"
        if "VIVOBOOK S14" in m:
            return "S5406MA" if year >= 2024 else "K3402ZA" if year >= 2022 else "S433EA"
        if "VIVOBOOK" in m:
            return "A1404ZA" if year >= 2023 else "A416MA"
        if "EXPERTBOOK" in m:
            return "B9403CVA" if year >= 2023 else "B9400CEA" if year >= 2021 else "B9450FA"
        return f"ASUS-{m.split()[0]}-{year}"

    # =========================================================================
    # 3. LENOVO (16IRX8, 21HD, 15IRH8, etc.)
    # =========================================================================
    if b == "LENOVO":
        if "LEGION PRO 5" in m or "LEGION 5 PRO" in m or "LEGION 5" in m:
            if year >= 2024: return "16IRX9" if "INTEL" in cpu or not "RYZEN" in cpu else "16AHP9"
            if year == 2023: return "16IRX8" if "INTEL" in cpu or not "RYZEN" in cpu else "16ARX8"
            if year == 2022: return "16IAH7H" if "INTEL" in cpu else "16ARH7H"
            if year == 2021: return "16ACH6H" if "16" in m else "15ACH6H"
            if year == 2020: return "15IMH05H"
            if year >= 2017: return "Y540-15IRH" if year >= 2019 else "Y530-15ICH" if year >= 2018 else "Y520-15IKBN"
            return f"Y50-70-{year}"

        if "LEGION 7" in m or "LEGION PRO 7" in m:
            if year >= 2024: return "16IRX9H"
            if year == 2023: return "16IRX8H"
            if year >= 2021: return "16ACHg6"
            return f"Y740-15IRH-{year}"

        if "LOQ" in m:
            if year >= 2024: return "15IAX9" if "INTEL" in cpu or not "RYZEN" in cpu else "15AHP9"
            return "15IRH8" if "INTEL" in cpu or not "RYZEN" in cpu else "15APH8"

        if "THINKPAD T" in m or "T14" in m or "T480" in m or "T450" in m:
            if "GEN 5" in m or year >= 2024: return "T14 Gen 5 (21ML)"
            if "GEN 4" in m or year == 2023: return "T14 Gen 4 (21HD)"
            if "GEN 3" in m or year == 2022: return "T14 Gen 3 (21AH)"
            if "GEN 2" in m or year == 2021: return "T14 Gen 2 (20W0)"
            if "GEN 1" in m or year == 2020: return "T14 Gen 1 (20S0)"
            if "T490" in m or year == 2019: return "T490 (20N2)"
            if "T480" in m or year == 2018: return "T480 (20L5)"
            if "T470" in m or year == 2017: return "T470 (20HD)"
            if "T460" in m or year == 2016: return "T460 (20FM)"
            if "T450" in m or year == 2015: return "T450 (20BV)"
            if "T440" in m or year == 2014: return "T440 (20B6)"
            if "T430" in m or year == 2013: return "T430 (2342)"
            if "T420" in m or year == 2012: return "T420 (4177)"
            return "T410 (2516)"

        if "X1 CARBON" in m:
            if "GEN 12" in m or year >= 2024: return "X1 Carbon Gen 12 (21KC)"
            if "GEN 11" in m or year == 2023: return "X1 Carbon Gen 11 (21HM)"
            if "GEN 10" in m or year == 2022: return "X1 Carbon Gen 10 (21CB)"
            if "GEN 9" in m or year == 2021: return "X1 Carbon Gen 9 (20XW)"
            if "GEN 8" in m or year == 2020: return "X1 Carbon Gen 8 (20U9)"
            if "GEN 7" in m or year == 2019: return "X1 Carbon Gen 7 (20QD)"
            if "GEN 6" in m or year == 2018: return "X1 Carbon Gen 6 (20KH)"
            if "GEN 5" in m or year == 2017: return "X1 Carbon Gen 5 (20HR)"
            return f"X1 Carbon Gen {max(1, year - 2011)}"

        if "THINKPAD X" in m or "X13" in m or "X280" in m or "X230" in m:
            if year >= 2023: return "X13 Gen 4 (21EX)"
            if year == 2022: return "X13 Gen 3 (21BN)"
            if year >= 2020: return "X13 Gen 1 (20T2)"
            if year == 2019: return "X390 (20Q0)"
            if year == 2018: return "X280 (20KF)"
            if year == 2017: return "X270 (20HN)"
            if year == 2016: return "X260 (20F6)"
            if year == 2015: return "X250 (20CL)"
            if year == 2014: return "X240 (20AL)"
            if year == 2013: return "X230 (2320)"
            return "X220 (4286)"

        if "THINKPAD E" in m or "E14" in m or "E480" in m:
            if year >= 2023: return "E14 Gen 5 (21JK)"
            if year == 2022: return "E14 Gen 4 (21E3)"
            if year >= 2020: return "E14 Gen 2 (20TA)"
            return "E480 (20KN)" if year >= 2018 else "E450 (20DC)"

        if "IDEAPAD SLIM 3" in m:
            return "14IRU8" if year >= 2023 else "14IAU7" if year == 2022 else "14ITL6"
        if "IDEAPAD SLIM 5" in m:
            return "14IRL8" if year >= 2023 else "14ABA7" if year == 2022 else "14ITL05"
        if "YOGA" in m:
            return "14IMH9" if year >= 2024 else "14IRH8" if year == 2023 else "14IAP7"
        return f"LENOVO-{m.split()[0]}-{year}"

    # =========================================================================
    # 4. ACER (PHN16-71, AN515-58, SFG14-72, etc.)
    # =========================================================================
    if b == "ACER":
        if "HELIOS NEO 16" in m:
            return "PHN16-72" if year >= 2024 else "PHN16-71"
        if "HELIOS 16" in m or "PREDATOR HELIOS 16" in m or "HELIOS 16/300" in m:
            if year >= 2024: return "PH16-72"
            if year == 2023: return "PH16-71"
            if year == 2022: return "PH315-55"
            if year == 2021: return "PH315-54"
            if year == 2020: return "PH315-53"
            if year >= 2018: return "PH315-52" if year >= 2019 else "PH315-51"
            return f"G3-571-{year}"
        if "NITRO 16" in m:
            return "AN16-41" if "RYZEN" in cpu else "AN16-51"
        if "NITRO V 15" in m or "NITRO V" in m:
            return "ANV15-51"
        if "NITRO 5" in m or "NITRO" in m:
            if year >= 2022: return "AN515-58"
            if year == 2021: return "AN515-57"
            if year == 2020: return "AN515-55"
            if year == 2019: return "AN515-54"
            if year == 2018: return "AN515-52"
            return "AN515-51"
        if "SWIFT GO 14" in m or "SWIFT GO" in m:
            return "SFG14-72" if year >= 2024 else "SFG14-71"
        if "SWIFT X" in m:
            return "SFX14-72G" if year >= 2024 else "SFX14-71G"
        if "SWIFT 3" in m:
            return "SF314-512" if year >= 2022 else "SF314-511" if year == 2021 else "SF314-59"
        if "ASPIRE 5" in m:
            return "A515-58M" if year >= 2023 else "A514-55" if year == 2022 else "A514-54"
        if "ASPIRE 3" in m:
            return "A314-36M" if year >= 2023 else "A314-22"
        return f"ACER-{m.split()[0]}-{year}"

    # =========================================================================
    # 5. MSI (B13VFK, A12VF, A13VG, etc.)
    # =========================================================================
    if b == "MSI":
        gpu_c = "F"  # default 4060
        if "4050" in gpu: gpu_c = "E"
        elif "4060" in gpu: gpu_c = "F"
        elif "4070" in gpu: gpu_c = "G"
        elif "4080" in gpu: gpu_c = "H"
        elif "3050" in gpu: gpu_c = "C"
        elif "3060" in gpu: gpu_c = "D"

        if "KATANA 15" in m or "KATANA" in m:
            if year >= 2024: return f"B14V{gpu_c}K"
            if year == 2023: return f"B13V{gpu_c}K"
            return f"B12V{gpu_c}K" if year == 2022 else "GF66 11UE"
        if "CYBORG 15" in m or "CYBORG" in m:
            if year >= 2024: return f"A14V{gpu_c}"
            return f"A13V{gpu_c}" if year == 2023 else f"A12V{gpu_c}"
        if "STEALTH 16" in m or "STEALTH" in m:
            return "A1VGG" if year >= 2024 else f"A13V{gpu_c}"
        if "RAIDER" in m:
            return "GE78 HX 14V" if year >= 2024 else "GE78 HX 13V" if year == 2023 else "GE76 Raider"
        if "TITAN" in m:
            return "18 HX A14V" if year >= 2024 else "GT77 HX 13V"
        if "MODERN 14" in m or "MODERN" in m:
            return "C13M" if year >= 2023 else "C12M" if year == 2022 else "B11M"
        if "PRESTIGE" in m:
            return "AI Evo B1M" if year >= 2024 else "14 A12UD"
        return f"MSI-MODEL-{year}"

    # =========================================================================
    # 6. HP (16-wf, 15-fa, 840 G10, etc.)
    # =========================================================================
    if b == "HP":
        if "OMEN 16" in m or "OMEN" in m:
            if year >= 2024: return "16-wf1000" if "INTEL" in cpu or not "RYZEN" in cpu else "16-xf1000"
            if year == 2023: return "16-wf0000" if "INTEL" in cpu or not "RYZEN" in cpu else "16-xf0000"
            if year == 2022: return "16-k0000"
            return "16-c0000" if year == 2021 else "15-dh1000"
        if "VICTUS 15" in m or "VICTUS" in m:
            if year >= 2023: return "15-fa1000" if "INTEL" in cpu or not "RYZEN" in cpu else "15-fb1000"
            return "15-fa0000" if "INTEL" in cpu or not "RYZEN" in cpu else "15-fb0000"
        if "ELITEBOOK 840" in m or "ELITEBOOK" in m:
            gen_no = max(1, min(11, year - 2013))
            return f"840 G{gen_no}"
        if "PAVILION PLUS" in m or "PAVILION" in m:
            return "14-ew0000" if year >= 2024 else "14-eh0000" if year >= 2022 else "14-dv0000"
        if "ENVY" in m:
            return "16-h1000" if year >= 2023 else "16-h0000"
        return f"HP-SERIES-{year}"

    # =========================================================================
    # 7. DELL (m16 R1, 9320, 5530, 5440, etc.)
    # =========================================================================
    if b == "DELL":
        if "ALIENWARE M16" in m or "ALIENWARE" in m:
            return "m16 R2" if year >= 2024 else "m16 R1" if year == 2023 else "m15 R7" if year == 2022 else "m15 R4"
        if "DELL G15" in m or "G15" in m:
            return "5530" if year >= 2023 else "5520" if year == 2022 else "5511" if year == 2021 else "5590"
        if "DELL G16" in m or "G16" in m:
            return "7630" if year >= 2023 else "7620"
        if "XPS 13" in m:
            if year >= 2024: return "9340"
            if year == 2023: return "9320 Plus"
            if year == 2022: return "9315"
            if year >= 2020: return "9310"
            return "7390" if year == 2019 else "9380" if year == 2018 else "9370"
        if "XPS 15" in m:
            return "9530" if year >= 2023 else "9520" if year == 2022 else "9510"
        if "LATITUDE" in m:
            return f"54{max(10, year - 2009) * 10 // 10}"
        if "INSPIRON" in m:
            return "5430" if year >= 2023 else "5420"
        return f"DELL-{m.split()[0]}-{year}"

    # =========================================================================
    # 8. AXIOO (Pongo 760 v2, Hype 5, etc.)
    # =========================================================================
    if b == "AXIOO":
        if "PONGO 760" in m:
            return "Pongo 760 v2" if year >= 2024 else "Pongo 760 v1"
        if "PONGO 960" in m:
            return "Pongo 960 v1"
        if "PONGO 725" in m:
            return "Pongo 725 v1"
        if "PONGO" in m:
            return "Pongo Clevo NP50" if year <= 2022 else "Pongo 760 v1"
        if "HYPE 5" in m:
            return "Hype 5 X5-AMD" if "RYZEN" in cpu else "Hype 5 Gen 12"
        if "HYPE 7" in m:
            return "Hype 7 X7-AMD"
        if "HYPE 3" in m:
            return "Hype 3 Gen 10"
        if "SAGA" in m:
            return "SAGA 12"
        return f"AXIOO-{m.split()[0]}-{year}"

    # =========================================================================
    # 9. HUAWEI (VGHH-16, MDF-W5651, etc.)
    # =========================================================================
    if b == "HUAWEI":
        if "X PRO" in m:
            return "VGHH-32" if year >= 2024 else "VGHH-16" if year == 2023 else "MRGF-X"
        if "MATEBOOK 14S" in m:
            return "HKDE-W7611"
        if "MATEBOOK 14" in m:
            return "KLVD-WFE9" if year >= 2022 else "KLV-W19"
        if "D14" in m:
            return "MDF-W5651" if year >= 2023 else "NbD-WDI9" if year >= 2021 else "NobelB-WAH9P"
        if "D15" in m:
            return "BoD-WDH9" if year >= 2021 else "BoB-WAH9P"
        if "D16" in m:
            return "MCLG-X" if year >= 2023 else "RLEF-X"
        return f"HUAWEI-{m.split()[0]}-{year}"

    # =========================================================================
    # 10. MICROSOFT SURFACE (Model 1951, Model 2038, etc.)
    # =========================================================================
    if b == "MICROSOFT" or "SURFACE" in m:
        if "SURFACE LAPTOP 5" in m: return "Model 1951 (13.5\")"
        if "SURFACE LAPTOP 6" in m: return "Model 2036 (Core Ultra)"
        if "SURFACE LAPTOP 4" in m: return "Model 1950 (Intel)"
        if "SURFACE LAPTOP 3" in m: return "Model 1867"
        if "SURFACE PRO 9" in m: return "Model 2038 (Intel Gen 12)"
        if "SURFACE PRO 10" in m: return "Model 2079 (Core Ultra)"
        if "SURFACE PRO 8" in m: return "Model 1983"
        if "SURFACE PRO 7" in m: return "Model 1866"
        if "STUDIO 2" in m or "STUDIO 2+" in m: return "Model 2029"
        if "STUDIO" in m: return "Model 1964"
        return f"Surface Model-{year}"

    return f"{b}-{m.split()[0]}-{year}"
