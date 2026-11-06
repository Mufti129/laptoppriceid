#!/usr/bin/env python3
"""
Pipeline Pembaruan Berkas Excel:
1. Membaca listing harga riil laptop dari:
   - Tokopedia Seller Terpercaya (Official Store & Power Merchant)
   - Integrasi Marketplace FB & OLX
   - Database laptop_bekas.db
2. Memetakan listing ke 'Model Terkait' pada katalog LaptopMedia.
3. Menambahkan tab/sheet 'list harga tarikan' ke pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx.
4. Menambahkan formula FMV multi-sampel dinamis pada sheet 'Katalog Seri LaptopMedia':
   - Jumlah Sampel Iklan (COUNTIF)
   - Harga Pasar Terendah / Min (MINIFS)
   - Harga Pasar Tertinggi / Max (MAXIFS)
   - Harga Rata-Rata / Mean (AVERAGEIFS)
   - Harga FMV (MEDIAN(IF(...))) multi-sampel riil pasar dengan fallback ekonometrik
   - Metode Kalkulasi FMV
5. Menyinkronkan file ke seluruh direktori terkait dan exports/.
"""

import os
import re
import sys
import sqlite3
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


def load_laptopmedia_models(wb: openpyxl.Workbook) -> tuple[set[str], dict[str, int]]:
    """Membaca daftar Model Terkait dan fallback FMV dari Katalog Seri LaptopMedia dan SQLite DB."""
    ws = wb["Katalog Seri LaptopMedia"]
    lm_models = set()
    for row in range(2, ws.max_row + 1):
        val = ws.cell(row, 3).value
        if val:
            lm_models.add(str(val).strip())

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, fair_market_value, release_year FROM master_models WHERE fair_market_value IS NOT NULL")
    fmv_lookup = {}
    for name, fmv, year in cur.fetchall():
        if name and fmv:
            fmv_lookup[name] = int(fmv)
            clean_name = re.sub(r"\s*\((?:19\d\d|20\d\d)\)$", "", name).strip()
            if clean_name not in fmv_lookup:
                fmv_lookup[clean_name] = int(fmv)
    conn.close()

    return lm_models, fmv_lookup


def normalize_model_for_lm(raw_model: str, brand: str, title: str, lm_models: set[str]) -> str:
    """Normalisasi nama model agar presisi mencocokkan 'Model Terkait' LaptopMedia."""
    m = str(raw_model or "").strip()
    b = str(brand or "").strip()
    t = str(title or "").lower()

    if m in lm_models:
        return m

    # Cek kombinasi Brand + Model
    bm = f"{b} {m}".strip()
    if bm in lm_models:
        return bm

    # Pemetaan Apple MacBook
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

    # Pemetaan Lenovo ThinkPad & IdeaPad
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

    # Pemetaan ASUS
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

    # Pemetaan Acer
    if "nitro 5" in m.lower() or "nitro 5" in t or "an515" in t:
        return "Acer Nitro 5 (52, 51, 41, 31)"
    if "aspire 3" in m.lower() or "aspire 3" in t:
        return "Acer Aspire 3"
    if "aspire 5" in m.lower() or "aspire 5" in t:
        return "Acer Aspire 5"
    if "swift 3" in m.lower() or "swift 3" in t:
        return "Acer Swift 3"

    # Pemetaan HP
    if "victus 15" in m.lower() or "victus" in t:
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

    # Pemetaan Dell
    if "latitude 7490" in m.lower() or "7490" in t:
        return "Dell Latitude 7490"
    if "latitude 7400" in m.lower() or "7400" in t:
        return "Dell Latitude 7400"
    if "xps 13" in m.lower() or "xps 13" in t:
        return "Dell XPS 13 9370"

    # Pencarian parsial dalam merek yang sama
    for x in lm_models:
        if x.lower().startswith(b.lower()) and m.lower() in x.lower() and len(m) >= 4:
            return x

    return m


def collect_all_market_listings(lm_models: set[str]) -> pd.DataFrame:
    """Mengumpulkan dan memadukan seluruh data listing harga riil dari Tokopedia & marketplace."""
    records = []

    # 1. Tarikan Tokopedia Trusted Sellers Terbaru (Official Store & Power Merchant)
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
            records.append({
                "platform_sumber": "Tokopedia (Trusted Seller)",
                "brand": brand,
                "model_terkait": model_terkait,
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
                records.append({
                    "platform_sumber": str(r.get("sumber_marketplace") or "Marketplace Terverifikasi"),
                    "brand": brand,
                    "model_terkait": model_terkait,
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

    # 3. Database Utama laptop_bekas.db (Scraped listings terverifikasi)
    if DB_PATH.exists():
        print(f"[DATA SOURCE] Membaca scraped listings terverifikasi dari {DB_PATH}...")
        conn_db = sqlite3.connect(DB_PATH)
        query = """
        SELECT 
            'Tokopedia' as platform_sumber,
            b.name as brand,
            m.name as model_raw,
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
            model_terkait = normalize_model_for_lm(raw_m, brand, title, lm_models)
            records.append({
                "platform_sumber": "Tokopedia",
                "brand": brand,
                "model_terkait": model_terkait,
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
    # Filter harga tidak valid
    df = df[(df["harga"] >= 800000) & (df["harga"] <= 150000000)]
    # Deduplikasi berbasis URL produk
    df = df.drop_duplicates(subset=["url_produk"], keep="first")
    df = df.reset_index(drop=True)
    df.insert(0, "no", range(1, len(df) + 1))
    print(f"[DATA READY] Total listing harga riil terverifikasi: {len(df)} unit.")
    return df


def update_workbook():
    print("=" * 80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MEMULAI PEMBARUAN MASTER WORKBOOK EXCEL")
    print("=" * 80)

    if not EXCEL_PRIMARY.exists():
        raise FileNotFoundError(f"File master excel tidak ditemukan di {EXCEL_PRIMARY}")

    print(f"[EXCEL LOAD] Membuka file workbook: {EXCEL_PRIMARY}...")
    wb = openpyxl.load_workbook(EXCEL_PRIMARY)

    lm_models, fmv_lookup = load_laptopmedia_models(wb)
    print(f"[CATALOG] Model Terkait unik di LaptopMedia: {len(lm_models)} tipe.")
    print(f"[LOOKUP] Benchmark FMV Ekonometrik di DB: {len(fmv_lookup)} tipe.")

    # 1. Kumpulkan seluruh data listing tarikan
    df_listings = collect_all_market_listings(lm_models)
    n_listings = len(df_listings)

    # 2. Perbarui atau Tambahkan Sheet 'list harga tarikan'
    sheet_name_tarikan = "list harga tarikan"
    if sheet_name_tarikan in wb.sheetnames:
        print(f"[SHEET] Memperbarui sheet eksisting: '{sheet_name_tarikan}'...")
        ws_tarikan = wb[sheet_name_tarikan]
        # Kosongkan konten lama
        ws_tarikan.delete_rows(1, ws_tarikan.max_row + 1)
    else:
        print(f"[SHEET] Membuat sheet baru: '{sheet_name_tarikan}'...")
        ws_tarikan = wb.create_sheet(title=sheet_name_tarikan)

    # Header styling
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

    headers_tarikan = [
        "No", "Platform Sumber", "Brand", "Model Terkait (LaptopMedia)",
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
        "no", "platform_sumber", "brand", "model_terkait",
        "nama_seri_target", "judul_iklan", "harga",
        "nama_toko", "lokasi", "status_seller", "url_produk", "waktu_tarikan"
    ]].values.tolist()

    for r_idx, row_val in enumerate(data_rows, start=2):
        ws_tarikan.append(row_val)
        # Format sel
        c_no = ws_tarikan.cell(row=r_idx, column=1)
        c_no.alignment = center_align
        c_no.border = thin_border

        c_price = ws_tarikan.cell(row=r_idx, column=7)
        c_price.number_format = currency_fmt
        c_price.alignment = right_align
        c_price.border = thin_border

        for c_idx in [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]:
            cell = ws_tarikan.cell(row=r_idx, column=c_idx)
            cell.font = Font(name="Calibri", size=9)
            cell.border = thin_border
            if c_idx in [2, 3, 9, 10, 12]:
                cell.alignment = center_align
            else:
                cell.alignment = left_align

    # Auto fit column widths di sheet tarikan
    for col in ws_tarikan.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col[:50])
        ws_tarikan.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    # 3. Modifikasi Sheet 'Katalog Seri LaptopMedia'
    ws_lm = wb["Katalog Seri LaptopMedia"]
    print(f"[KATALOG LM] Memperbarui sheet 'Katalog Seri LaptopMedia' ({ws_lm.max_row} baris)...")

    # Kolom baru yang ditambahkan:
    # Col H (8): Jumlah Sampel Iklan
    # Col I (9): Harga Pasar Terendah (Min)
    # Col J (10): Harga Pasar Tertinggi (Max)
    # Col K (11): Harga Rata-Rata (Mean Rp)
    # Col L (12): Harga (FMV Rp)
    # Col M (13): Metode Kalkulasi FMV
    new_lm_headers = [
        "Jumlah Sampel Iklan",
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

    tarikan_last_row = n_listings + 1
    # Model Terkait di sheet tarikan berada di Kolom D ($D$2:$D$last)
    # Harga di sheet tarikan berada di Kolom G ($G$2:$G$last)
    tarikan_model_range = f"'list harga tarikan'!$D$2:$D${tarikan_last_row}"
    tarikan_price_range = f"'list harga tarikan'!$G$2:$G${tarikan_last_row}"

    print(f"[FORMULA INJECTION] Menginjeksi rumus FMV dinamis multi-sampel ke {ws_lm.max_row - 1} baris model...")

    for r in range(2, ws_lm.max_row + 1):
        model_name = str(ws_lm.cell(row=r, column=3).value or "").strip()
        brand_name = str(ws_lm.cell(row=r, column=1).value or "").strip()
        year_val = ws_lm.cell(row=r, column=6).value
        try:
            year_int = int(year_val)
        except (ValueError, TypeError):
            year_int = 2021

        # Dapatkan benchmark fallback FMV dari DB
        fallback_fmv = fmv_lookup.get(model_name)
        if not fallback_fmv:
            clean_m = re.sub(r"\s*\((?:19\d\d|20\d\d)\)$", "", model_name).strip()
            fallback_fmv = fmv_lookup.get(clean_m)
        if not fallback_fmv:
            # Fallback ekonometrik estimasi berbasis brand & tahun rilis
            age = max(0, 2026 - year_int)
            base_msrp = 22000000 if brand_name in ["Apple", "Alienware", "Razer"] else 13500000
            deprec_factor = (0.82 ** age)
            fallback_fmv = int(round(base_msrp * deprec_factor, -4))

        # Formula Excel:
        # Col H: Jumlah Sampel Iklan
        f_count = f"=COUNTIF({tarikan_model_range}, C{r})"
        # Col I: Harga Pasar Terendah (Min)
        f_min = f'=IF(H{r}>0, MINIFS({tarikan_price_range}, {tarikan_model_range}, C{r}), "-")'
        # Col J: Harga Pasar Tertinggi (Max)
        f_max = f'=IF(H{r}>0, MAXIFS({tarikan_price_range}, {tarikan_model_range}, C{r}), "-")'
        # Col K: Harga Rata-Rata (Mean Rp)
        f_mean = f'=IF(H{r}>0, ROUND(AVERAGEIFS({tarikan_price_range}, {tarikan_model_range}, C{r}), -3), "-")'
        # Col L: Harga (FMV Rp) -> MEDIAN(IF(...)) multi-sampel dinamis pasar sekunder
        f_fmv = f'=IF(H{r}>0, ROUND(MEDIAN(IF({tarikan_model_range}=C{r}, {tarikan_price_range})), -3), {fallback_fmv})'
        # Col M: Penjelasan Metode Kalkulasi
        f_method = f'=IF(H{r}>0, "Median Sampel Riil Pasar (\'list harga tarikan\')", "Model Ekonometrik Depresiasi")'

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

    # Set column widths for new columns
    ws_lm.column_dimensions["H"].width = 16
    ws_lm.column_dimensions["I"].width = 20
    ws_lm.column_dimensions["J"].width = 20
    ws_lm.column_dimensions["K"].width = 22
    ws_lm.column_dimensions["L"].width = 20
    ws_lm.column_dimensions["M"].width = 34

    # 4. Simpan ke berkas target
    print(f"[SAVE] Menyimpan ke target utama: {EXCEL_PRIMARY}...")
    wb.save(EXCEL_PRIMARY)

    if EXCEL_SECONDARY.parent.exists():
        print(f"[SAVE] Menyimpan salinan ke: {EXCEL_SECONDARY}...")
        wb.save(EXCEL_SECONDARY)

    EXCEL_EXPORT.parent.mkdir(parents=True, exist_ok=True)
    print(f"[SAVE] Menyimpan salinan ke repositori exports: {EXCEL_EXPORT}...")
    wb.save(EXCEL_EXPORT)

    print("=" * 80)
    print("[SELESAI] Master Workbook Excel berhasil diperbarui dan disinkronkan secara menyeluruh.")
    print("=" * 80)


if __name__ == "__main__":
    update_workbook()
