# LaptopPrice ID — Laptop Intelligence & Hedonic Valuation Platform

Platform riset ekonometrik, intelligence pasar sekunder, dan kalkulator valuasi harga wajar laptop (*Fair Market Value*) pertama di Indonesia yang mengintegrasikan pemodelan hedonik kualitas, deteksi perangkap DP/kredit semu, dan scanner arbitrase otomatis.

---

## Fitur Utama Sistem

1. **AI & NLP Data Refinement Pipeline:**
   - Normalisasi teks bahasa pasar Indonesia untuk spesifikasi teknis CPU, GPU TGP, RAM SODIMM vs Soldered, SSD NVMe, kondisi baterai (*Cycle Count*, *Battery Health*, Baterai Drop), dan cacat layar (*Whitespot*, *Dead Pixel*, *Flexgate*).
   - Deteksi otomatis iklan pancingan DP/angsuran, spek usang yang disamarkan (*misal Intel Core i7 Gen 1*), dan unit terkunci BIOS/Computrace/MDM.
   - **Deep Generational Entity Matcher (`pipeline/entity_matcher.py`):** Pencocokan varian berbasis token N-Gram dan verifikasi generasi CPU/chipset (misal Apple M1 vs M2/M3, ThinkPad Gen 1 vs Gen 4) untuk mencegah false-positive cross-generation.

2. **Econometric Valuation Engine (Lancaster-Rosen Hedonic Model):**
   - Eliminasi anomali harga menggunakan metode **Tukey Interquartile Range (IQR)**.
   - Penyesuaian nilai wajar berbasis bobot empiris kualitas fisik, engsel, kesehatan baterai, kelengkapan charger adaptor original vs OEM, dan garansi resmi.
   - Model penyusutan nilai multi-tier: *Apple Silicon*, *Business Enterprise*, *Gaming High-End*, dan *Consumer Mainstream*.

3. **Arbitrage & Hot Deals Radar:**
   - Detektor otomatis listing laptop yang dijual di bawah nilai pasar wajar (*undervalued*) dengan kalkulasi potensi margin keuntungan reseller (Tier 1 Super Arbitrage $\ge 22\%$, Tier 2 High $15-21\%$, Tier 3 Moderate $12-14\%$).

4. **Modular Executive Streamlit Web Dashboard (`views/`):**
   - Tampilan responsif dengan tema *Executive Dark Slate* yang nyaman dipandang.
   - **Arsitektur Modular Per Tampilan:** Kode dashboard dipecah secara bersih ke dalam direktori `views/` (`market_overview.py`, `fmv_calculator.py`, `price_corridors.py`, `arbitrage_radar.py`, `spec_matrix.py`, `master_catalog.py`, `data_explorer.py`).
   - **Sinkronisasi URL Query Params (`st.query_params`):** Setiap modul dapat diakses dan dibagikan secara instan melalui link URL langsung (misal `?menu=fmv`, `?menu=catalog`).
   - Visualisasi gambar produk laptop beresolusi tinggi pada seluruh lini brand & model.
   - 7 Modul Analisis Lengkap:
     - *Market Overview & Dashboard* (Statistik pasar makro & showcase featured flagships)
     - *FMV & Hedonic Calculator* (Kalkulator valuasi presisi tinggi + foto produk & spek pabrik)
     - *3-Tier Price Corridors & Quantiles* (P25 bargain, median FMV, dan P75 pristine)
     - *Arbitrage & Hot Deals Radar* (Radar peluang beli murah + kartu deal visual interaktif)
     - *Spec Matrix & Model Comparison* (Komparasi berdampingan head-to-head lengkap dengan foto unit)
     - *Master Catalog Data* (Eksplorasi 1.000 Model Hardware, Galeri Visual Kartu, & Export CSV)
     - *Data Explorer & Scam Filter* (Audit listing pasar & filter perangkap DP)

---

## Panduan Instalasi & Penggunaan

### 1. Prasyarat Sistem
- Python 3.10+ (Direkomendasikan Python 3.13)
- SQLite3

### 2. Instalasi Dependensi
```bash
# Clone atau buka direktori proyek
cd "Scrape Data Laptop"

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependensi pustaka
pip install -r requirements.txt
```

### 3. Inisialisasi Database & Pipeline
```bash
# Menjalankan seeding master katalog, snapshot pasar & validasi pipeline
python3 main.py
```

### 4. Menjalankan Web Dashboard
```bash
streamlit run app.py
```
Aplikasi akan terbuka otomatis di peramban Anda pada alamat `http://localhost:8501`.

---

## Pengujian Sistem (Automated Tests)
Jalankan seluruh test suite untuk memverifikasi keandalan sistem:
```bash
python3 -m unittest discover tests
```

---

## Pengembang
- **Pengembang & Analis Sistem:** Mukhammad Rekza Mufti
- **Lisensi:** MIT License (2026)
