# LaptopPrice ID — Laptop Intelligence & Hedonic Valuation Platform

Platform riset ekonometrik, intelligence pasar sekunder, dan kalkulator valuasi harga wajar laptop (*Fair Market Value*) pertama di Indonesia yang mengintegrasikan pemodelan hedonik kualitas, deteksi perangkap DP/kredit semu, dan scanner arbitrase otomatis.

---

## Fitur Utama Sistem

1. **AI & NLP Data Refinement Pipeline:**
   - Normalisasi teks bahasa pasar Indonesia untuk spesifikasi teknis CPU, GPU TGP, RAM SODIMM vs Soldered, SSD NVMe, kondisi baterai (*Cycle Count*, *Battery Health*, Baterai Drop), dan cacat layar (*Whitespot*, *Dead Pixel*, *Flexgate*).
   - Deteksi otomatis iklan pancingan DP/angsuran, spek usang yang disamarkan (*misal Intel Core i7 Gen 1*), dan unit terkunci BIOS/Computrace/MDM.
   - RapidFuzz entity matching untuk resolusi judul listing marketplace ke master katalog varian resmi.

2. **Econometric Valuation Engine (Lancaster-Rosen Hedonic Model):**
   - Eliminasi anomali harga menggunakan metode **Tukey Interquartile Range (IQR)**.
   - Penyesuaian nilai wajar berbasis bobot empiris kualitas fisik, engsel, kesehatan baterai, kelengkapan charger adaptor original vs OEM, dan garansi resmi.
   - Model penyusutan nilai multi-tier: *Apple Silicon*, *Business Enterprise*, *Gaming High-End*, dan *Consumer Mainstream*.

3. **Arbitrage & Hot Deals Radar:**
   - Detektor otomatis listing laptop yang dijual di bawah nilai pasar wajar (*undervalued*) dengan kalkulasi potensi margin keuntungan reseller (Tier 1 Super Arbitrage $\ge 22\%$, Tier 2 High $15-21\%$, Tier 3 Moderate $12-14\%$).

4. **Executive Streamlit Web Dashboard:**
   - Tampilan responsif dengan tema *Executive Dark Slate* yang nyaman dipandang.
   - 7 Modul Analisis Lengkap:
     - *Market Overview & Dashboard*
     - *FMV & Hedonic Calculator*
     - *3-Tier Price Corridors & Quantiles*
     - *Arbitrage & Hot Deals Radar*
     - *Spec Matrix & Model Comparison*
     - *Master Catalog Data* (Eksplorasi 1.000 Model Hardware & Export CSV)
     - *Data Explorer & Scam Filter*

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
