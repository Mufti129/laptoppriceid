# AUDIT SISTEM ENGINE SCRAPING & RISET WEBSITE TERPERCAYA
## LaptopPrice ID — Sistem Monitoring & Intelijen Harga Pasar Laptop Indonesia

**Dokumen Analisis Arsitektur, Kualitas Data, Ketahanan Anti-Bot, dan Rekomendasi Platform Sumber Data**  
*Tanggal: 15 Oktober 2026*  
*Versi: 2.0 (Production Review)*

---

## 1. Ringkasan Eksekutif

Sistem **LaptopPrice ID** saat ini telah berhasil menjalankan pipeline *end-to-end* yang memproses data harga laptop sekunder di Indonesia:
- Telah mengumpulkan dan memverifikasi **4.036 listing riil aktif** dari pasar C2C Indonesia.
- Dilengkapi modul **NLP Normalizer**, **Scam & DP Trap Detector**, serta **Deep Entity Matcher** dengan tingkat pencocokan ke katalog master sebesar 58.5%.
- Menerapkan metodologi ekonometrika **Lancaster Hedonic Quality Valuation** dan **Tukey IQR Outlier Filtering** untuk menghitung estimasi Nilai Pasar Wajar (*Fair Market Value* / FMV).

Namun demikian, audit menyeluruh terhadap sistem **Engine Scraping** mengidentifikasi beberapa titik rentan kritis (*critical vulnerabilities*) yang harus dimitigasi agar sistem beroperasi dengan ketahanan kelas *enterprise* (*production-grade resilience*). Dokumen ini menyajikan hasil audit teknis, evaluasi komparatif situs sumber data terpercaya di Indonesia dan global, serta cetak biru arsitektur mesin scraping generasi baru.

---

## 2. Audit Menyeluruh Engine Scraping Saat Ini

### A. Arsitektur Komponen Saat Ini

Sistem harvesting data saat ini terpusat pada 3 berkas utama:
1. `scrapers/real_marketplace_scraper.py`: Mesin pengambil data web Carousell Indonesia berbasis HTTP/1.1 synchronous (`requests.Session` + `BeautifulSoup4`).
2. `scrapers/populate_real_data.py`: Orkes pemrosesan pipeline data mentah menuju pembersihan (purging), normalisasi, filtering penipuan, entity matching, dan batch insert ke SQLite.
3. `pipeline/`: Modul normalisasi spesifikasi hardware, kamus slang bahasa jual beli Indonesia (`slang_dictionary.py`), dan pemfilter anomali.

```
[ Carousell ID Web ] 
        │ (HTTP/1.1 Synchronous via requests)
        ▼
[ real_marketplace_scraper.py ] ──► [ real_listings_cache.json ]
        │
        ▼
[ populate_real_data.py ]
        │
        ├──► [ LaptopListingNormalizer ] (Ekstraksi RAM, SSD, Kondisi)
        ├──► [ LaptopScamDetector ] (Filter DP / Cicilan / Anomali)
        ├──► [ LaptopEntityMatcher ] (Pencocokan ke 1.000 Varian Master)
        │
        ▼
[ laptop_bekas.db (SQLite) ] ──► [ LaptopPricingEngine ] (Tukey IQR + FMV)
```

---

### B. Analisis Keunggulan (Strengths)

1. **Akurasi Tinggi Pemrosesan Bahasa Alami Penjual Indonesia:**
   - Modul `LaptopListingNormalizer` didukung kamus slang komprehensif (`slang_dictionary.py`).
   - Mampu mengekstrak atribut penting laptop: status baterai (Cycle Count, Battery Health %), kondisi engsel (*hinge*), cacat layar (*whitespot*, garis, *flexgate*), kelengkapan (*fullset* vs batangan vs *charger* OEM), serta keamanan BIOS/MDM/Computrace dari teks informal penjual.
2. **Efektivitas Filter Anti-Scam & DP Trap:**
   - Berhasil mendeteksi dan mengisolasi 413 listing (10.2%) yang merupakan iklan jebakan DP/angsuran (*"Promo DP 500rb"*) atau unit rusak total, sehingga statistik FMV tidak terdistorsi ke bawah.
3. **Penyimpanan Batch Berkecepatan Tinggi:**
   - Menggunakan SQLAlchemy `bulk_save_objects` dengan throughput ~1.900 baris/detik ke SQLite tanpa *memory leak*.
4. **Isolasi Brand & Disambiguasi Seri Ketat:**
   - NLP Matcher menerapkan *Brand Isolation Guard* (judul Lenovo tidak akan pernah tertukar dengan ASUS/Acer) dan *Series Disambiguation* (membedakan ThinkPad, Legion, LOQ, dan IdeaPad).

---

### C. Kelemahan Kritis & Celah Sistem (Vulnerabilities & Bottlenecks)

Berdasarkan investigasi teknis dan pengujian langsung di jaringan, ditemukan 6 kelemahan mendasar:

| No | Komponen Rentan | Gejala / Dampak | Tingkat Risiko |
| :---: | :--- | :--- | :---: |
| **1** | **Ketergantungan Sumber Tunggal (*Single Point of Failure*)** | 100% data live bersumber murni dari **Carousell ID**. Jika Carousell memperbarui struktur DOM atau mengaktifkan Cloudflare Turnstile, seluruh aliran data terhenti. | 🔴 **CRITICAL** |
| **2** | **Kerapuhan Selektor DOM (*Brittle CSS Selectors*)** | Pengecekan harga dan judul bergantung pada class inline seperti `p[style*="--max-line:2"]` atau `div[class*="ebp"] p`. Perubahan kecil pada build frontend Carousell akan membuat parsing gagal menghasilkan 0 data. | 🔴 **HIGH** |
| **3** | **Ketiadaan TLS Fingerprint Spoofing (JA3/JA4)** | Library `requests` menggunakan signature TLS OpenSSL standar. Akses ke platform lain (Tokopedia, Shopee, Bukalapak, OLX, Enterkomputer) langsung ditolak dengan `HTTP 403 Forbidden`, `ERR_HTTP2_PROTOCOL_ERROR`, atau timeout karena deteksi bot Akamai/Cloudflare. | 🔴 **HIGH** |
| **4** | **Arsitektur Sekuensial / Monolitik (Blocking)** | Pengecekan 161 keyword berjalan satu per satu secara sinkronus dengan `time.sleep(0.4)`. Waktu eksekusi memakan 2-3 menit. Tidak ada worker asynchronous (`aiohttp`/`asyncio`) dengan rate-limiter adaptif. | 🟡 **MEDIUM** |
| **5** | **Ketiadaan Pelacakan Delta & Siklus Hidup (*Delta Tracking*)** | Sistem belum mencatat riwayat penurunan harga (*price drop history*) untuk listing yang sama, dan belum dapat mendeteksi kapan suatu listing terjual (*sold out*) atau ditarik oleh penjual (*delisted*). | 🟡 **MEDIUM** |
| **6** | **Belum Terintegrasi Job Scheduler Otomatis** | Penarikan data masih memerlukan eksekusi skrip manual melalui terminal. Belum ada worker background daemon (Cron) yang menjalankan sinkronisasi berkala (misal tiap 6 jam) dengan *circuit breaker* dan telemetri kegagalan. | 🟡 **MEDIUM** |

---

## 3. Riset Website & Sumber Data Terpercaya untuk Monitoring Laptop

Untuk membangun ekosistem data yang tahan banting, sistem monitoring harga laptop memerlukan kombinasi **4 lapisan sumber data (*Multi-Tier Data Sourcing*)**:

```
┌────────────────────────────────────────────────────────────────────────┐
│  Tier 1: C2C Peer-to-Peer Marketplaces (Harga Nego Penjual Personal)  │
│  • Carousell ID (Primer) | • Facebook Marketplace (Pelengkap)          │
├────────────────────────────────────────────────────────────────────────┤
│  Tier 2: B2C & Merchant Refurbished (Toko Fisik & Garansi Resmi)       │
│  • Tokopedia Verified Merchants | • Shopee Refurbished Ex-Corporate    │
├────────────────────────────────────────────────────────────────────────┤
│  Tier 3: Aggregators & Retail Ground Truth (MSRP & Tren Mall Offline) │
│  • Enterkomputer (Mangga Dua) | • Pricebook ID                         │
├────────────────────────────────────────────────────────────────────────┤
│  Tier 4: Global Transaction Benchmarks (Ground Truth Transaksi)        │
│  • eBay Completed/Sold API | • Notebookcheck Technical Specs Master    │
└────────────────────────────────────────────────────────────────────────┘
```

---

### A. Matriks Komparasi 8 Platform Sumber Data

| Platform | Kategori | Kelebihan Utama | Hambatan Teknis | Tingkat Aksesibilitas | Rekomendasi Peran |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Carousell ID** (`id.carousell.com`) | C2C Personal | • Listing murni dari perorangan<br>• Foto fisik asli kamera penjual<br>• Label kondisi (*Like new, used*)<br>• Data SSR HTML lengkap | • Sebagian penjual menulis harga singkat (Rp 7.50 = 7.5jt)<br>• Format judul bebas | ⭐⭐⭐⭐⭐<br>*(Sangat Mudah)* | **Sumber Primer Harian Listing C2C** |
| **Tokopedia** (`tokopedia.com`) | B2C & Verified Merchants | • Sentra toko fisik (Harco Mangga Dua, ITC Kuningan, BEC)<br>• Garansi toko terverifikasi (1 bln)<br>• Reputasi toko & rating transparan | • Proteksi Cloudflare Shield & ByteDance Slardar WAF<br>• Initial SSR tidak merender produk<br>• Memerlukan GraphQL internal / stealth client | ⭐⭐⭐<br>*(Menengah - Butuh Bridge)* | **Jangkar Harga Toko Spesialis Second** |
| **Shopee ID** (`shopee.co.id`) | B2C & Refurbished | • Volume laptop bisnis ex-kantor terbesar (ThinkPad T/X, Dell Latitude, HP EliteBook)<br>• Rentang harga 2-6 jutaan sangat padat | • Proteksi Akamai Bot Manager (Error 403 / `error: 90309999`)<br>• Puzzle Slider Captcha dinamis<br>• Varian multi-SKU dalam 1 postingan | ⭐⭐<br>*(Sulit - Butuh Token Solver)* | **Monitoring Segmen Laptop Bisnis Murah** |
| **Enterkomputer** (`enterkomputer.com`) | Retail Master (Mangga Dua) | • Pricelist resmi distributor Indonesia (Synnex, Astrindo, Datascrip)<br>• Spesifikasi presisi & varian part number resmi | • Dilindungi Cloudflare Challenge (HTTP 403 pada raw request) | ⭐⭐⭐<br>*(Menengah - Butuh Cloudflare solver)* | **Ground Truth MSRP Baru untuk Depreciation Engine** |
| **Pricebook** (`pricebook.co.id`) | Offline Mall Aggregator | • Agregasi harga dari toko-toko mall komputer offline di Indonesia<br>• Menampilkan riwayat harga pasar | • Kurang banyak listing C2C personal; lebih fokus katalog baru | ⭐⭐⭐⭐<br>*(Mudah)* | **Validasi Rentang Harga Pasar Wajar** |
| **OLX Indonesia** (`olx.co.id`) | Classifieds P2P | • Platform pionir barang bekas Indonesia<br>• Banyak pedagang lokal kota-kota daerah | • Proteksi blocking agresif (Read Timeout pada connection pool)<br>• Sering memblokir IP data center | ⭐⭐<br>*(Sulit)* | **Sumber Tambahan Kota Tier 2/3** |
| **Facebook Marketplace** | Local P2P | • Volume transaksi terbesar di tingkat lokal (COD)<br>• Harga sangat murah dari *first-party owners* | • *Walled garden* (Wajib login session)<br>• Proteksi anti-crawler AI Meta tingkat tinggi | ⭐<br>*(Sangat Sulit)* | **Data Eksploratif via Session Browser Khusus** |
| **eBay Global (Sold Listings)** | Global Transaction Ground Truth | • Menyediakan data **harga saat barang laku (*Sold Items*)**, bukan sekadar harga tawar iklan<br>• Tersedia **Official REST API (Browse API)** | • Kurs mata uang (USD) harus dikonversi ke IDR<br>• Pola pasar luar negeri sedikit berbeda pada pajak | ⭐⭐⭐⭐⭐<br>*(Sangat Mudah via API Resmi)* | **Benchmark Depresiasi Global (Apple & ThinkPad)** |

---

## 4. Evaluasi Teknis: Mengapa Marketplace Besar Mengunci Datanya?

Berdasarkan pengujian teknis yang telah kita lakukan di environment:
1. **Shopee Indonesia:**
   - Menguji HTTP GET langsung ke endpoint `/api/v4/search/search_items` menghasilkan respons:
     ```json
     {"action_type": 2, "error": 90309999, "error_msg": "bot challenge required"}
     ```
   - Penyebab: Shopee menggunakan sensor **Akamai Edge Worker** yang memvalidasi header terenkripsi `af-ac-enc-dat` dan fingerprint browser Canvas/WebGL.
2. **Tokopedia:**
   - Menguji Playwright headless menghasilkan:
     ```text
     playwright._impl._errors.Error: Page.goto: net::ERR_HTTP2_PROTOCOL_ERROR at https://www.tokopedia.com/...
     ```
   - Penyebab: Server edge Tokopedia memutuskan koneksi HTTP/2 jika *TLS ClientHello handshake* tidak cocok dengan profil peramban manusia asli (deteksi JA3/JA4 fingerprint).
3. **Enterkomputer & OLX:**
   - Menggunakan `requests` menghasilkan respons `403 Just a moment...` (Cloudflare Bot Management).

---

## 5. Cetak Biru Arsitektur Engine Scraping Generasi Baru (Next-Gen Engine)

Untuk mengubah engine scraping saat ini menjadi mesin intelijen harga yang tangguh, berikut adalah rekomendasi arsitektur modular yang dirancang khusus:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      SCRAPING ORCHESTRATOR & CRON                      │
│                (Terjadwal Tiap 6 Jam / On-Demand API)                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌───────────────────────┐                         ┌──────────────────────┐
│   ADAPTER CAROUSELL   │                         │   ADAPTER TOKOPEDIA  │
│ (Direct SSR + Retry)  │                         │ (GraphQL / Stealth)  │
└──────────┬────────────┘                         └──────────┬───────────┘
           │                                                 │
           └────────────────────────┬────────────────────────┘
                                    │ Raw JSON Listings
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       DATA ENRICHMENT PIPELINE                         │
│  1. Normalizer NLP (RAM, SSD, Processor, GPU, Batterai, Grade Fisik)   │
│  2. Scam & DP Detector (Filter Cicilan & Iklan Rusak)                  │
│  3. Deep Entity Matcher (Pencocokan ke 1.000 Varian Master)            │
│  4. Delta Tracker (Deteksi Perubahan Harga & Status Delisted)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Clean Structured Data
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     DATABASE LAPTOPPRICE ID (SQLITE)                   │
│  • master_catalogs  • scraped_listings  • listing_price_history        │
│  • market_price_stats (Kalkulasi Otomatis Tukey IQR & Lancaster FMV)   │
└────────────────────────────────────────────────────────────────────────┘
```

### A. Fitur Inti yang Perlu Diimplementasikan

#### 1. Adapter Pattern (Modularitas per Marketplace)
Setiap marketplace memiliki file adapter tersendiri yang mewarisi class `BaseScraperAdapter`:
- `CarousellAdapter`: Mengambil data C2C tanpa headless browser (kecepatan tinggi, hemat memori).
- `TokopediaAdapter`: Memanggil query GraphQL terverifikasi menggunakan token browser session atau Playwright stealth.
- `PricebookAdapter`: Menarik baseline harga mall offline.

#### 2. Advanced HTTP Engine (`curl_cffi` / TLS Impersonation)
Menggantikan `requests` standar dengan engine yang mampu meniru TLS Handshake peramban Chrome asli (*JA3/JA4 TLS Fingerprint Spoofing*). Pendekatan ini memungkinkan sistem menembus proteksi Cloudflare dan Akamai tanpa perlu menyewa proxy mahal.

#### 3. Delta Scraping & Price History Tracking
Menambahkan tabel baru `listing_price_history`:
```sql
CREATE TABLE listing_price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id INTEGER REFERENCES scraped_listings(id),
    old_price NUMERIC(14, 2),
    new_price NUMERIC(14, 2),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
- Manfaat: Ketika penjual menurunkan harga dari Rp 8.500.000 menjadi Rp 7.900.000, sistem menandainya sebagai sinyal *“Harga Turun / Hot Deal”*.
- Jika listing hilang dari hasil pencarian selama 7 hari berturut-turut, sistem menandainya sebagai *“Terjual / Delisted”*.

#### 4. Asynchronous Concurrency dengan Adaptive Token Bucket
Mengubah loop sekuensial menjadi asinkron (`asyncio` + `aiohttp` / worker pool) dengan pembatasan delay acak 0.3 - 0.7 detik. Ini memangkas waktu harvesting 161 keyword dari 3 menit menjadi **kurang dari 30 detik**.

#### 5. Background Scheduler & Health Observability
Menyediakan modul CLI daemon atau cron job internal:
```bash
python scrapers/daemon.py --interval 6h --sources carousell,tokopedia
```
Dilengkapi logging terstruktur dan telemetri kegagalan (jika suatu marketplace mengubah struktur HTML, scraper langsung mencatat error ke log tanpa menghentikan modul lainnya).

---

## 6. Rencana Aksi Bertahap (Action Plan)

| Tahap | Tindakan Teknis | Estimasi Waktu | Output Nyata |
| :--- | :--- | :---: | :--- |
| **Tahap 1**<br>*(Immediate)* | • Refactor `real_marketplace_scraper.py` dengan fallback selector DOM yang lebih tahan banting (*multi-selector fallback*).<br>• Menambahkan fitur pelacakan riwayat harga (*Price Drop Alert*). | 1 Hari | Scraper Carousell anti-pecah dan fitur deteksi penurunan harga aktif. |
| **Tahap 2**<br>*(Short-Term)* | • Implementasi Tokopedia GraphQL Scraper Adapter dengan session token injection.<br>• Integrasi database multi-platform (Carousell + Tokopedia). | 2-3 Hari | Dataset diperkaya dengan ribuan unit dari toko komputer fisik terpercaya (Mangga Dua/BEC). |
| **Tahap 3**<br>*(Medium-Term)* | • Integrasi background cron daemon untuk sinkronisasi otomatis tiap 6 jam.<br>• Dashboard metrik performa scraper pada antarmuka admin Streamlit. | 1-2 Hari | Sistem berjalan 100% mandiri (*autonomous data pipeline*) tanpa intervensi manual. |

---

*Laporan ini disusun sebagai panduan teknis implementasi pengembangan sistem intelijen pasar LaptopPrice ID.*
