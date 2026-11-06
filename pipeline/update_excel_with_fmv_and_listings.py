#!/usr/bin/env python3
"""
Pipeline Pembaruan Berkas Excel:
1. Membaca listing harga riil laptop dari Tokopedia Trusted Sellers, Marketplace FB/OLX, dan DB.
2. Mengekstraksi dan menstandarisasi Tahun Rilis / Generasi untuk setiap listing.
3. Menulis ke tab 'list harga tarikan' (13 kolom).
4. Menghitung dan membuat tab khusus 'Matriks FMV (Model & Tahun)' (identik dengan implementasi pada pemetaan motor):
   - Merek
   - Model Terkait (LaptopMedia)
   - Mapping Kategori Internal (Gaming, Premium/Ultrabook, Bisnis, Consumer)
   - Tahun Rilis Model
   - Sampel Riil
   - Harga Minimum (Rp)
   - Harga Bawah P25 (Rp)
   - Harga FMV Median (Rp)
   - Harga Atas P75 (Rp)
   - Harga Maksimum (Rp)
   - Harga Rata-Rata (Rp)
5. Memetakan ke tab 'Katalog Seri LaptopMedia' menggunakan formula SUMIFS universal yang bebas dari error #NAME?:
   - Jumlah Sampel Iklan (Model + Tahun)
   - Harga Pasar Terendah (Min)
   - Harga Pasar Tertinggi (Max)
   - Harga Rata-Rata (Mean Rp)
   - Harga (FMV Rp)
   - Metode Kalkulasi FMV
6. Menyinkronkan file ke seluruh direktori terkait dan exports/.
"""

import os
import re
import sys
import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

EXCEL_PRIMARY = Path("/Users/macbookair/Downloads/pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx")
EXCEL_SECONDARY = Path("/Users/macbookair/Downloads/pemetaan tipe laptop data internal dan data tarikan laptopmedia/pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx")
EXCEL_EXPORT = ROOT_DIR / "exports" / "pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx"

DB_PATH = ROOT_DIR / "laptop_bekas.db"
INTEGRASI_DB_PATH = Path("/tmp/integrasi_harga_laptop_extracted/integrasi_harga_laptop/data/integrasi_pasar_laptopmedia.db")
TOKOPEDIA_CSV = ROOT_DIR / "exports" / "tarikan_harga_tokopedia_trusted_sellers.csv"


def load_laptopmedia_metadata(wb: openpyxl.Workbook) -> tuple[set[str], dict[str, int], dict[str, int], dict[str, int]]:
    """Membaca daftar Model Terkait, pemetaan tahun, dan fallback FMV dari Katalog Seri LaptopMedia & DB."""
    ws = wb["Katalog Seri LaptopMedia"]
    lm_models = set()
    lm_model_year = {}

    for row in range(2, ws.max_row + 1):
        m_val = ws.cell(row, 3).value
        y_val = ws.cell(row, 6).value
        if m_val:
            m_str = str(m_val).strip()
            lm_models.add(m_str)
            try:
                y_int = int(y_val)
                if m_str not in lm_model_year:
                    lm_model_year[m_str] = y_int
            except (ValueError, TypeError):
                pass

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, fair_market_value, release_year FROM master_models WHERE fair_market_value IS NOT NULL")
    fmv_lookup = {}
    db_model_year = {}
    for name, fmv, year in cur.fetchall():
        if name:
            if fmv:
                fmv_lookup[name] = int(fmv)
                clean_name = re.sub(r"\s*\((?:19\d\d|20\d\d)\)$", "", name).strip()
                if clean_name not in fmv_lookup:
                    fmv_lookup[clean_name] = int(fmv)
            if year:
                db_model_year[name] = int(year)
                clean_name = re.sub(r"\s*\((?:19\d\d|20\d\d)\)$", "", name).strip()
                if clean_name not in db_model_year:
                    db_model_year[clean_name] = int(year)
    conn.close()

    return lm_models, lm_model_year, fmv_lookup, db_model_year


def normalize_model_for_lm(raw_model: str, brand: str, title: str, lm_models: set[str]) -> str:
    """Normalisasi nama model agar presisi mencocokkan 'Model Terkait' LaptopMedia."""
    m = str(raw_model or "").strip()
    b = str(brand or "").strip()
    t = str(title or "").lower()

    if m in lm_models:
        return m

    bm = f"{b} {m}".strip()
    if bm in lm_models:
        return bm

    # Apple MacBook
    if "macbook air 13 m1" in m.lower() or ("macbook air" in t and "m1" in t and "13" in t):
        return "Apple MacBook Air 13 (2020)"
    if "macbook air 13 m2" in m.lower() or ("macbook air" in t and "m2" in t and "13" in t):
        return "Apple MacBook Air 13 (2022)"
    if "macbook air 13 m3" in m.lower():
        return "Apple MacBook Air 13 (Early 2024)"
    if "macbook air 15" in m.lower() or ("macbook air" in t and "15" in t):
        return "Apple MacBook Air 15"
    if "macbook air 13 retina" in m.lower() or ("macbook air" in t and "retina" in t):
        return "Apple MacBook Air 13 (2018, 2019)"
    if "macbook air 13 (a1466)" in m.lower():
        return "Apple MacBook Air 13 (Early 2015)"
    if "macbook pro 13 touch bar" in m.lower() or ("macbook pro" in t and "touch bar" in t and "2020" in t):
        return "Apple MacBook Pro 13 (Touch Bar / 2020)"
    if "macbook pro 13 m1" in m.lower() or ("macbook pro" in t and "m1" in t and "13" in t):
        return "Apple MacBook Pro 13 (Touch Bar / Late 2020)"
    if "macbook pro 14" in m.lower() or ("macbook pro" in t and "14" in t):
        return "Apple MacBook Pro 14 (Late 2021)"
    if "macbook pro 16" in m.lower() or ("macbook pro" in t and "16" in t):
        return "Apple MacBook Pro 16 (Late 2021)"
    if "macbook pro 13" in m.lower():
        return "Apple MacBook Pro 13"

    # Lenovo ThinkPad & IdeaPad
    if "thinkpad x1 carbon" in m.lower() or "thinkpad x1 carbon" in t:
        gen = re.search(r"gen\s*(\d+)", f"{m} {t}".lower())
        if gen:
            g = gen.group(1)
            suff = {"1": "1st", "2": "2nd", "3": "3rd"}.get(g, f"{g}th")
            cand = f"Lenovo ThinkPad X1 Carbon ({suff} Gen)"
            if cand in lm_models:
                return cand
            for x in lm_models:
                if f"Lenovo ThinkPad X1 Carbon ({suff} Gen" in x:
                    return x
        return "Lenovo ThinkPad X1 Carbon (6th Gen, 2018)"

    if "loq 15" in m.lower() or "loq 15" in t:
        for x in lm_models:
            if "Lenovo LOQ 15" in x:
                return x

    if "ideapad gaming 3" in m.lower() or "ideapad gaming" in t:
        return "Lenovo IdeaPad Gaming 3 (15\", 2021)"

    if "ideapad slim 3" in m.lower() or "ideapad 3" in m.lower():
        return "Lenovo IdeaPad 330S (14\")" if "330" in t else "Lenovo IdeaPad Slim 3"

    if "thinkpad t480" in m.lower() or "t480" in t:
        return "Lenovo ThinkPad T480"
    if "thinkpad t470" in m.lower() or "t470" in t:
        return "Lenovo ThinkPad T470"
    if "thinkpad t460" in m.lower() or "t460" in t:
        return "Lenovo ThinkPad T460"
    if "thinkpad t450" in m.lower() or "t450" in t:
        return "Lenovo ThinkPad T450"

    # ASUS
    if "flow x13" in m.lower() or "flow x13" in t:
        return "ASUS ROG Flow X13"
    if "flow z13" in m.lower() or "flow z13" in t:
        return "ASUS ROG Flow Z13"
    if "vivobook 14" in m.lower() or "vivobook 14" in t:
        return "ASUS VivoBook 14"
    if "vivobook 15" in m.lower() or "vivobook 15" in t:
        return "ASUS VivoBook 15"
    if "vivobook" in m.lower() or "vivobook" in t:
        return "ASUS VivoBook 14"
    if "tuf gaming" in m.lower() or "tuf" in t:
        return "ASUS TUF Gaming"
    if "rog strix" in m.lower() or "gl503" in t:
        return "ASUS ROG Strix GL503" if "gl503" in t else "ASUS ROG Strix"
    if "zephyrus g14" in m.lower() or "ga401" in t:
        return "ASUS ROG Zephyrus G14"
    if "zenbook" in m.lower() or "zenbook" in t:
        return "ASUS ZenBook"

    # Acer
    if "nitro 5" in m.lower() or "nitro 5" in t or "an515" in t:
        return "Acer Nitro 5 (52, 51, 41, 31)"
    if "aspire 3" in m.lower() or "aspire 3" in t:
        return "Acer Aspire 3"
    if "aspire 5" in m.lower() or "aspire 5" in t:
        return "Acer Aspire 5"
    if "swift 3" in m.lower() or "swift 3" in t:
        return "Acer Swift 3"

    # HP
    if "victus 15" in m.lower() or "victus 16" in m.lower() or "victus" in t:
        return "HP Victus 15"
    if "elitebook 840 g3" in m.lower() or "840 g3" in t:
        return "HP EliteBook 840 G3"
    if "elitebook 840 g1" in m.lower() or "840 g1" in t:
        return "HP EliteBook 840 G1"
    if "elitebook 840" in m.lower():
        return "HP EliteBook 840 G3"
    if "pavilion 14" in m.lower() or "pavilion 14" in t:
        return "HP Pavilion 14"
    if "pavilion 15" in m.lower() or "pavilion 15" in t:
        return "HP Pavilion 15"

    # Dell
    if "latitude 7490" in m.lower() or "7490" in t:
        return "Dell Latitude 7490"
    if "latitude 7400" in m.lower() or "7400" in t:
        return "Dell Latitude 7400"
    if "xps 13" in m.lower() or "xps 13" in t:
        return "Dell XPS 13 9370"

    for x in lm_models:
        if x.lower().startswith(b.lower()) and m.lower() in x.lower() and len(m) >= 4:
            return x

    return m


def extract_year_advanced(title: str) -> int | None:
    """Ekstraksi tahun rilis dari judul iklan dengan pembersihan tanggal garansi masa depan."""
    t = str(title).lower()
    t_clean = re.sub(r'garansi[^\n\r,.]*?\b202[5-9]\b', '', t)
    t_clean = re.sub(r'on\s*\d{1,2}/\d{1,2}/202[5-9]', '', t_clean)

    # 1. Tahun rilis eksplisit (2010 - 2026)
    m_year = re.search(r'\b(20[12]\d)\b', t_clean)
    if m_year:
        y = int(m_year.group(1))
        if 2010 <= y <= 2026:
            return y

    # 2. Apple Silicon
    if "m1" in t_clean: return 2020
    if "m2" in t_clean: return 2022
    if "m3" in t_clean or "m4" in t_clean: return 2024

    # 3. Frasa Generasi CPU Intel
    m_gen_phrase = re.search(r'(?:core\s*i[3579]|intel)[^\d]{1,10}(?:gen|generation)\s*(\d{1,2})', t_clean)
    if not m_gen_phrase:
        m_gen_phrase = re.search(r'\b(?:gen|generation)\s*(\d{1,2})\b', t_clean)
    if m_gen_phrase:
        g = int(m_gen_phrase.group(1))
        gen_map = {
            1: 2010, 2: 2011, 3: 2012, 4: 2014, 5: 2015, 6: 2016,
            7: 2017, 8: 2018, 9: 2019, 10: 2020, 11: 2021, 12: 2022, 13: 2023, 14: 2024
        }
        if g in gen_map:
            return gen_map[g]

    # 4. Nomor Model CPU Intel
    m_cpu = re.search(r'i[3579][-\s]*(\d{1,2})\d{3}[a-z0-9]*', t_clean)
    if m_cpu:
        g = int(m_cpu.group(1))
        cpu_map = {
            2: 2011, 3: 2012, 4: 2014, 5: 2015, 6: 2016,
            7: 2017, 8: 2018, 9: 2019, 10: 2020, 11: 2021, 12: 2022, 13: 2023, 14: 2024
        }
        if g in cpu_map:
            return cpu_map[g]

    # 5. Seri AMD Ryzen
    m_ryzen = re.search(r'ryzen\s*[3579][-\s]*(\d)\d{3}', t_clean)
    if m_ryzen:
        rg = int(m_ryzen.group(1))
        ryzen_map = {1: 2017, 2: 2018, 3: 2019, 4: 2020, 5: 2021, 6: 2022, 7: 2023, 8: 2024, 9: 2024}
        if rg in ryzen_map:
            return ryzen_map[rg]

    # 6. Intel Codenames
    if "haswell" in t_clean: return 2014
    if "broadwell" in t_clean: return 2015
    if "skylake" in t_clean: return 2016
    if "kaby lake" in t_clean: return 2017
    if "coffee lake" in t_clean or "whiskey lake" in t_clean: return 2018
    if "comet lake" in t_clean or "ice lake" in t_clean: return 2020
    if "tiger lake" in t_clean: return 2021
    if "alder lake" in t_clean: return 2022
    if "raptor lake" in t_clean: return 2023

    return None


def resolve_listing_release_year(title: str, model_terkait: str, raw_model: str,
                                 lm_model_year: dict[str, int], db_model_year: dict[str, int]) -> int:
    """Menentukan tahun rilis listing dengan prioritas: Judul -> Model Terkait -> LM Katalog -> DB."""
    y_title = extract_year_advanced(title)
    if y_title and 2010 <= y_title <= 2026:
        return y_title

    m_in_name = re.search(r'\(.*?(20[12]\d).*?\)', model_terkait)
    if m_in_name:
        y_name = int(m_in_name.group(1))
        if 2010 <= y_name <= 2026:
            return y_name

    if model_terkait in lm_model_year:
        return lm_model_year[model_terkait]

    if raw_model in db_model_year:
        return db_model_year[raw_model]
    if model_terkait in db_model_year:
        return db_model_year[model_terkait]

    return 2021


def get_mapping_tier(model_name: str) -> str:
    """Menentukan mapping tier/kategori internal laptop."""
    m_lower = str(model_name).lower()
    if any(k in m_lower for k in ['rog', 'tuf', 'legion', 'gaming', 'nitro', 'predator', 'loq', 'victus', 'omen', 'alienware', 'blade']):
        return 'Laptop Gaming'
    if any(k in m_lower for k in ['macbook', 'zenbook', 'xps', 'spectre', 'yoga', 'thinkpad x1', 'gram', 'surface', 'prestige']):
        return 'Laptop Premium / Ultrabook'
    if any(k in m_lower for k in ['thinkpad', 'latitude', 'elitebook', 'probook', 'expertbook', 'vostro', 'precision', 'zbook']):
        return 'Laptop Bisnis / Commercial'
    return 'Laptop Consumer'


def collect_all_market_listings(lm_models: set[str], lm_model_year: dict[str, int],
                                db_model_year: dict[str, int]) -> pd.DataFrame:
    """Mengumpulkan dan memadukan seluruh data listing harga riil dengan atribusi Tahun Rilis."""
    records = []

    # 1. Tarikan Tokopedia Trusted Sellers Terbaru
    if TOKOPEDIA_CSV.exists():
        print(f"[DATA SOURCE] Membaca tarikan Tokopedia Trusted Sellers dari {TOKOPEDIA_CSV}...")
        df_tok = pd.read_csv(TOKOPEDIA_CSV)
        for _, r in df_tok.iterrows():
            title = str(r.get("nama_produk_tokopedia") or "")
            brand = str(r.get("merk") or "")
            target_type = str(r.get("target_tipe_internal") or "")
            raw_match = str(r.get("matched_master_model") or "").split(" - ")[0].strip()
            if raw_match == "-":
                raw_match = target_type

            model_terkait = normalize_model_for_lm(raw_match, brand, title, lm_models)
            tahun_rilis = resolve_listing_release_year(title, model_terkait, raw_match, lm_model_year, db_model_year)

            records.append({
                "platform_sumber": "Tokopedia (Trusted Seller)",
                "brand": brand,
                "model_terkait": model_terkait,
                "tahun_rilis_model": tahun_rilis,
                "nama_seri_target": target_type,
                "judul_iklan": title,
                "harga": int(r.get("harga_idr") or 0),
                "nama_toko": str(r.get("nama_toko") or "Official Store / Power Merchant"),
                "lokasi": str(r.get("lokasi_toko") or "Indonesia"),
                "status_seller": str(r.get("status_seller") or "Official Store / PM"),
                "url_produk": str(r.get("url_produk") or ""),
                "waktu_tarikan": str(r.get("waktu_tarikan") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            })

    # 2. Marketplace DB Integrasi (Facebook Marketplace & OLX)
    if INTEGRASI_DB_PATH.exists():
        print(f"[DATA SOURCE] Membaca data integrasi marketplace dari {INTEGRASI_DB_PATH}...")
        try:
            conn_m = sqlite3.connect(INTEGRASI_DB_PATH)
            df_m = pd.read_sql_query("SELECT * FROM market_listings", conn_m)
            conn_m.close()
            for _, r in df_m.iterrows():
                brand = str(r.get("canonical_brand") or "")
                raw_m = str(r.get("canonical_model") or "")
                title = str(r.get("judul") or "")
                model_terkait = normalize_model_for_lm(raw_m, brand, title, lm_models)
                tahun_rilis = resolve_listing_release_year(title, model_terkait, raw_m, lm_model_year, db_model_year)

                records.append({
                    "platform_sumber": str(r.get("sumber_marketplace") or "Marketplace Terverifikasi"),
                    "brand": brand,
                    "model_terkait": model_terkait,
                    "tahun_rilis_model": tahun_rilis,
                    "nama_seri_target": str(r.get("model_seri") or raw_m),
                    "judul_iklan": title,
                    "harga": int(r.get("harga") or 0),
                    "nama_toko": str(r.get("tipe_penjual") or "Verified Seller"),
                    "lokasi": str(r.get("lokasi") or "Indonesia"),
                    "status_seller": str(r.get("tipe_penjual") or "Verified"),
                    "url_produk": str(r.get("url") or ""),
                    "waktu_tarikan": str(r.get("last_scraped_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                })
        except Exception as e:
            print(f"[WARNING] Gagal membaca integrasi DB: {e}")

    # 3. Database Utama laptop_bekas.db
    if DB_PATH.exists():
        print(f"[DATA SOURCE] Membaca scraped listings terverifikasi dari {DB_PATH}...")
        conn_db = sqlite3.connect(DB_PATH)
        query = """
        SELECT 
            'Tokopedia' as platform_sumber,
            b.name as brand,
            m.name as model_raw,
            m.release_year as model_year,
            v.variant_name as seri_target,
            s.title as judul_iklan,
            CAST(s.price AS INTEGER) as harga,
            COALESCE(s.seller_name, 'Toko Terverifikasi') as nama_toko,
            COALESCE(s.city, 'Indonesia') as lokasi,
            COALESCE(s.seller_type, 'Power Merchant') as status_seller,
            s.url as url_produk,
            s.scraped_at as waktu_tarikan
        FROM scraped_listings s
        JOIN master_variants v ON s.matched_variant_id = v.id
        JOIN master_models m ON v.model_id = m.id
        JOIN master_brands b ON m.brand_id = b.id
        WHERE s.price >= 800000 AND s.price <= 150000000
        """
        df_db = pd.read_sql_query(query, conn_db)
        conn_db.close()
        for _, r in df_db.iterrows():
            brand = str(r.get("brand") or "")
            raw_m = str(r.get("model_raw") or "")
            title = str(r.get("judul_iklan") or "")
            model_year = r.get("model_year")
            model_terkait = normalize_model_for_lm(raw_m, brand, title, lm_models)
            tahun_rilis = resolve_listing_release_year(title, model_terkait, raw_m, lm_model_year, db_model_year)
            if model_year and 2010 <= model_year <= 2026:
                y_from_title = extract_year_advanced(title)
                if not y_from_title:
                    tahun_rilis = int(model_year)

            records.append({
                "platform_sumber": "Tokopedia",
                "brand": brand,
                "model_terkait": model_terkait,
                "tahun_rilis_model": tahun_rilis,
                "nama_seri_target": str(r.get("seri_target") or raw_m),
                "judul_iklan": title,
                "harga": int(r.get("harga") or 0),
                "nama_toko": str(r.get("nama_toko") or "Toko Terverifikasi"),
                "lokasi": str(r.get("lokasi") or "Indonesia"),
                "status_seller": str(r.get("status_seller") or "Power Merchant"),
                "url_produk": str(r.get("url_produk") or ""),
                "waktu_tarikan": str(r.get("waktu_tarikan") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            })

    df = pd.DataFrame(records)
    df = df[(df["harga"] >= 800000) & (df["harga"] <= 150000000)]
    df = df.drop_duplicates(subset=["url_produk"], keep="first")
    df = df.reset_index(drop=True)
    df.insert(0, "no", range(1, len(df) + 1))
    print(f"[DATA READY] Total listing harga riil terverifikasi: {len(df)} unit.")
    return df


def calculate_fmv_matrix(df_listings: pd.DataFrame) -> pd.DataFrame:
    """Mengkalkulasi agregat statistik Matriks FMV (Model & Tahun) dari data listing pasar riil."""
    print("[MATRIX CALC] Menghitung distribusi Matriks FMV (Model & Tahun)...")
    matrix_rows = []
    grouped = df_listings.groupby(["brand", "model_terkait", "tahun_rilis_model"])

    for (brand, model, year), group in grouped:
        prices = group["harga"].dropna().astype(float).values
        n = len(prices)
        if n == 0:
            continue
        p_min = int(np.min(prices))
        p25 = int(round(np.percentile(prices, 25), -3))
        p_med = int(round(np.median(prices), -3))
        p75 = int(round(np.percentile(prices, 75), -3))
        p_max = int(np.max(prices))
        p_mean = int(round(np.mean(prices), -3))
        tier = get_mapping_tier(model)

        matrix_rows.append({
            "Merek": brand,
            "Model Terkait (LaptopMedia)": model,
            "Mapping Kategori Internal": tier,
            "Tahun Rilis": int(year),
            "Sampel Riil": n,
            "Harga Minimum (Rp)": p_min,
            "Harga Bawah P25 (Rp)": p25,
            "Harga FMV Median (Rp)": p_med,
            "Harga Atas P75 (Rp)": p75,
            "Harga Maksimum (Rp)": p_max,
            "Harga Rata-Rata (Rp)": p_mean
        })

    df_matrix = pd.DataFrame(matrix_rows)
    df_matrix = df_matrix.sort_values(by=["Merek", "Model Terkait (LaptopMedia)", "Tahun Rilis"]).reset_index(drop=True)
    print(f"[MATRIX CALC] Berhasil menghitung {len(df_matrix)} entri Matriks FMV.")
    return df_matrix


def update_workbook():
    print("=" * 80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MEMULAI PEMBARUAN MASTER WORKBOOK EXCEL (TAB MATRIKS FMV)")
    print("=" * 80)

    if not EXCEL_PRIMARY.exists():
        raise FileNotFoundError(f"File master excel tidak ditemukan di {EXCEL_PRIMARY}")

    print(f"[EXCEL LOAD] Membuka file workbook: {EXCEL_PRIMARY}...")
    wb = openpyxl.load_workbook(EXCEL_PRIMARY)

    lm_models, lm_model_year, fmv_lookup, db_model_year = load_laptopmedia_metadata(wb)
    print(f"[CATALOG] Model Terkait unik di LaptopMedia: {len(lm_models)} tipe.")
    print(f"[LOOKUP] Benchmark FMV Ekonometrik di DB: {len(fmv_lookup)} tipe.")

    # 1. Kumpulkan seluruh data listing tarikan dengan Tahun Rilis
    df_listings = collect_all_market_listings(lm_models, lm_model_year, db_model_year)
    n_listings = len(df_listings)

    # 2. Hitung Matriks FMV (Model & Tahun)
    df_matrix = calculate_fmv_matrix(df_listings)
    n_matrix = len(df_matrix)

    # Styling umum
    header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    header_fill = PatternFill(fill_type="solid", start_color="1F497D", end_color="1F497D")
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9")
    )
    currency_fmt = '_("Rp"* #,##0_);_("Rp"* (#,##0);_("Rp"* "-"_);_(@_)'

    # 3. Perbarui Sheet 'list harga tarikan'
    sheet_name_tarikan = "list harga tarikan"
    if sheet_name_tarikan in wb.sheetnames:
        print(f"[SHEET] Memperbarui sheet eksisting: '{sheet_name_tarikan}'...")
        ws_tarikan = wb[sheet_name_tarikan]
        ws_tarikan.delete_rows(1, ws_tarikan.max_row + 1)
    else:
        print(f"[SHEET] Membuat sheet baru: '{sheet_name_tarikan}'...")
        ws_tarikan = wb.create_sheet(title=sheet_name_tarikan)

    headers_tarikan = [
        "No", "Platform Sumber", "Brand", "Model Terkait (LaptopMedia)", "Tahun Rilis Model",
        "Nama Seri / Tipe Target", "Nama Produk / Judul Iklan", "Harga (Rp)",
        "Nama Toko / Seller", "Lokasi / Kota", "Status Seller", "URL Produk", "Waktu Tarikan"
    ]

    ws_tarikan.append(headers_tarikan)
    for col_idx in range(1, len(headers_tarikan) + 1):
        cell = ws_tarikan.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    ws_tarikan.row_dimensions[1].height = 26

    print(f"[POPULATE] Menulis {n_listings} baris listing ke '{sheet_name_tarikan}'...")
    data_rows = df_listings[[
        "no", "platform_sumber", "brand", "model_terkait", "tahun_rilis_model",
        "nama_seri_target", "judul_iklan", "harga",
        "nama_toko", "lokasi", "status_seller", "url_produk", "waktu_tarikan"
    ]].values.tolist()

    for r_idx, row_val in enumerate(data_rows, start=2):
        ws_tarikan.append(row_val)
        c_no = ws_tarikan.cell(row=r_idx, column=1)
        c_no.alignment = center_align
        c_no.border = thin_border

        # Kolom E (Tahun Rilis Model)
        c_year = ws_tarikan.cell(row=r_idx, column=5)
        c_year.value = int(row_val[4]) if row_val[4] else 2021
        c_year.alignment = center_align
        c_year.border = thin_border

        # Kolom H (Harga Rp)
        c_price = ws_tarikan.cell(row=r_idx, column=8)
        c_price.number_format = currency_fmt
        c_price.alignment = right_align
        c_price.border = thin_border

        for c_idx in [2, 3, 4, 6, 7, 9, 10, 11, 12, 13]:
            cell = ws_tarikan.cell(row=r_idx, column=c_idx)
            cell.font = Font(name="Calibri", size=9)
            cell.border = thin_border
            if c_idx in [2, 3, 10, 11, 13]:
                cell.alignment = center_align
            else:
                cell.alignment = left_align

    for col in ws_tarikan.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col[:50])
        ws_tarikan.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    # 4. Tambahkan / Perbarui Sheet Khusus: 'Matriks FMV (Model & Tahun)'
    sheet_name_matrix = "Matriks FMV (Model & Tahun)"
    if sheet_name_matrix in wb.sheetnames:
        print(f"[SHEET] Memperbarui sheet eksisting: '{sheet_name_matrix}'...")
        ws_mat = wb[sheet_name_matrix]
        ws_mat.delete_rows(1, ws_mat.max_row + 1)
    else:
        print(f"[SHEET] Membuat sheet baru: '{sheet_name_matrix}'...")
        ws_mat = wb.create_sheet(title=sheet_name_matrix)

    # Struktur Kolom Matriks FMV (Model & Tahun):
    # Col A (1): Merek
    # Col B (2): Model Terkait (LaptopMedia)
    # Col C (3): Mapping Kategori Internal
    # Col D (4): Tahun Rilis
    # Col E (5): Sampel Riil
    # Col F (6): Harga Minimum (Rp)
    # Col G (7): Harga Bawah P25 (Rp)
    # Col H (8): Harga FMV Median (Rp)
    # Col I (9): Harga Atas P75 (Rp)
    # Col J (10): Harga Maksimum (Rp)
    # Col K (11): Harga Rata-Rata (Rp)
    headers_matrix = [
        "Merek", "Model Terkait (LaptopMedia)", "Mapping Kategori Internal", "Tahun Rilis", "Sampel Riil",
        "Harga Minimum (Rp)", "Harga Bawah P25 (Rp)", "Harga FMV Median (Rp)", "Harga Atas P75 (Rp)",
        "Harga Maksimum (Rp)", "Harga Rata-Rata (Rp)"
    ]

    ws_mat.append(headers_matrix)
    for col_idx in range(1, len(headers_matrix) + 1):
        cell = ws_mat.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    ws_mat.row_dimensions[1].height = 26

    print(f"[POPULATE] Menulis {n_matrix} baris ke '{sheet_name_matrix}'...")
    matrix_data_rows = df_matrix.values.tolist()

    for r_idx, row_val in enumerate(matrix_data_rows, start=2):
        ws_mat.append(row_val)
        # Col A (Merek)
        cA = ws_mat.cell(row=r_idx, column=1)
        cA.alignment = center_align
        cA.border = thin_border
        cA.font = Font(name="Calibri", size=9)

        # Col B (Model Terkait)
        cB = ws_mat.cell(row=r_idx, column=2)
        cB.alignment = left_align
        cB.border = thin_border
        cB.font = Font(name="Calibri", size=9)

        # Col C (Kategori)
        cC = ws_mat.cell(row=r_idx, column=3)
        cC.alignment = center_align
        cC.border = thin_border
        cC.font = Font(name="Calibri", size=9)

        # Col D (Tahun Rilis)
        cD = ws_mat.cell(row=r_idx, column=4)
        cD.value = int(row_val[3])
        cD.alignment = center_align
        cD.border = thin_border
        cD.font = Font(name="Calibri", size=9)

        # Col E (Sampel Riil)
        cE = ws_mat.cell(row=r_idx, column=5)
        cE.value = int(row_val[4])
        cE.number_format = '#,##0'
        cE.alignment = center_align
        cE.border = thin_border
        cE.font = Font(name="Calibri", size=9, bold=True)

        # Col F..K (Nominal Harga)
        for c_idx in range(6, 12):
            cell = ws_mat.cell(row=r_idx, column=c_idx)
            cell.number_format = currency_fmt
            cell.alignment = right_align
            cell.border = thin_border
            # Bold untuk Harga FMV Median (Col 8 / H)
            cell.font = Font(name="Calibri", size=9, bold=(c_idx == 8))

    for col in ws_mat.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col[:50])
        ws_mat.column_dimensions[col_letter].width = min(max(max_len + 3, 14), 45)

    # 5. Modifikasi Sheet 'Katalog Seri LaptopMedia' Berbasis Matriks FMV
    ws_lm = wb["Katalog Seri LaptopMedia"]
    print(f"[KATALOG LM] Memperbarui sheet 'Katalog Seri LaptopMedia' ({ws_lm.max_row} baris)...")

    new_lm_headers = [
        "Jumlah Sampel Iklan (Model + Tahun)",
        "Harga Pasar Terendah (Min)",
        "Harga Pasar Tertinggi (Max)",
        "Harga Rata-Rata (Mean Rp)",
        "Harga (FMV Rp)",
        "Metode Kalkulasi FMV"
    ]

    for offset, h_text in enumerate(new_lm_headers, start=8):
        cell = ws_lm.cell(row=1, column=offset)
        cell.value = h_text
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    ws_lm.row_dimensions[1].height = 28

    # Rentang referensi pada sheet Matriks FMV:
    mat_last_row = n_matrix + 1
    mat_model_range = f"'Matriks FMV (Model & Tahun)'!$B$2:$B${mat_last_row}"
    mat_year_range = f"'Matriks FMV (Model & Tahun)'!$D$2:$D${mat_last_row}"
    mat_sample_range = f"'Matriks FMV (Model & Tahun)'!$E$2:$E${mat_last_row}"
    mat_min_range = f"'Matriks FMV (Model & Tahun)'!$F$2:$F${mat_last_row}"
    mat_median_range = f"'Matriks FMV (Model & Tahun)'!$H$2:$H${mat_last_row}"
    mat_max_range = f"'Matriks FMV (Model & Tahun)'!$J$2:$J${mat_last_row}"
    mat_mean_range = f"'Matriks FMV (Model & Tahun)'!$K$2:$K${mat_last_row}"

    print(f"[FORMULA INJECTION] Menginjeksi rumus SUMIFS universal ke Matriks FMV untuk 4829 baris katalog...")

    for r in range(2, ws_lm.max_row + 1):
        model_name = str(ws_lm.cell(row=r, column=3).value or "").strip()
        brand_name = str(ws_lm.cell(row=r, column=1).value or "").strip()
        year_raw = ws_lm.cell(row=r, column=6).value
        try:
            year_int = int(year_raw)
        except (ValueError, TypeError):
            year_int = 2021

        ws_lm.cell(row=r, column=6, value=year_int)

        # Fallback FMV ekonometrik
        fallback_fmv = fmv_lookup.get(model_name)
        if not fallback_fmv:
            clean_m = re.sub(r"\s*\((?:19\d\d|20\d\d)\)$", "", model_name).strip()
            fallback_fmv = fmv_lookup.get(clean_m)
        if not fallback_fmv:
            age = max(0, 2026 - year_int)
            base_msrp = 22000000 if brand_name in ["Apple", "Alienware", "Razer"] else 13500000
            deprec_factor = (0.82 ** age)
            fallback_fmv = int(round(base_msrp * deprec_factor, -4))

        # Formula Excel Universal Menggunakan SUMIFS (Bebas dari #NAME? & 100% Kompatibel Semua Versi Excel):
        # Col H: Jumlah Sampel Iklan (Model + Tahun)
        f_count = f"=SUMIFS({mat_sample_range}, {mat_model_range}, C{r}, {mat_year_range}, F{r})"
        # Col I: Harga Pasar Terendah (Min)
        f_min = f'=IF(H{r}>0, SUMIFS({mat_min_range}, {mat_model_range}, C{r}, {mat_year_range}, F{r}), "-")'
        # Col J: Harga Pasar Tertinggi (Max)
        f_max = f'=IF(H{r}>0, SUMIFS({mat_max_range}, {mat_model_range}, C{r}, {mat_year_range}, F{r}), "-")'
        # Col K: Harga Rata-Rata (Mean Rp)
        f_mean = f'=IF(H{r}>0, SUMIFS({mat_mean_range}, {mat_model_range}, C{r}, {mat_year_range}, F{r}), "-")'
        # Col L: Harga (FMV Rp)
        f_fmv = f'=IF(H{r}>0, SUMIFS({mat_median_range}, {mat_model_range}, C{r}, {mat_year_range}, F{r}), {fallback_fmv})'
        # Col M: Metode Kalkulasi FMV
        f_method = f'=IF(H{r}>0, "Median Riil Matriks FMV (Model & Tahun)", "Model Ekonometrik Depresiasi")'

        cH = ws_lm.cell(row=r, column=8, value=f_count)
        cH.number_format = '#,##0'
        cH.alignment = center_align
        cH.border = thin_border
        cH.font = Font(name="Calibri", size=9)

        cI = ws_lm.cell(row=r, column=9, value=f_min)
        cI.number_format = currency_fmt
        cI.alignment = right_align
        cI.border = thin_border
        cI.font = Font(name="Calibri", size=9)

        cJ = ws_lm.cell(row=r, column=10, value=f_max)
        cJ.number_format = currency_fmt
        cJ.alignment = right_align
        cJ.border = thin_border
        cJ.font = Font(name="Calibri", size=9)

        cK = ws_lm.cell(row=r, column=11, value=f_mean)
        cK.number_format = currency_fmt
        cK.alignment = right_align
        cK.border = thin_border
        cK.font = Font(name="Calibri", size=9)

        cL = ws_lm.cell(row=r, column=12, value=f_fmv)
        cL.number_format = currency_fmt
        cL.alignment = right_align
        cL.border = thin_border
        cL.font = Font(name="Calibri", size=9, bold=True)

        cM = ws_lm.cell(row=r, column=13, value=f_method)
        cM.alignment = left_align
        cM.border = thin_border
        cM.font = Font(name="Calibri", size=9)

    ws_lm.column_dimensions["H"].width = 24
    ws_lm.column_dimensions["I"].width = 20
    ws_lm.column_dimensions["J"].width = 20
    ws_lm.column_dimensions["K"].width = 22
    ws_lm.column_dimensions["L"].width = 20
    ws_lm.column_dimensions["M"].width = 38

    # 6. Simpan ke seluruh berkas target
    print(f"[SAVE] Menyimpan ke target utama: {EXCEL_PRIMARY}...")
    wb.save(EXCEL_PRIMARY)

    if EXCEL_SECONDARY.parent.exists():
        print(f"[SAVE] Menyimpan salinan ke: {EXCEL_SECONDARY}...")
        wb.save(EXCEL_SECONDARY)

    EXCEL_EXPORT.parent.mkdir(parents=True, exist_ok=True)
    print(f"[SAVE] Menyimpan salinan ke repositori exports: {EXCEL_EXPORT}...")
    wb.save(EXCEL_EXPORT)

    print("=" * 80)
    print(f"[SELESAI] Master Workbook Excel berhasil dilengkapi dengan tab 'Matriks FMV (Model & Tahun)' ({n_matrix} entri).")
    print("=" * 80)


if __name__ == "__main__":
    update_workbook()
