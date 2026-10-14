# DOKUMENTASI LENGKAP & SPESIFIKASI TEKNIS SISTEM
## LAPTOPPRICE ID — LAPTOP INTELLIGENCE & HEDONIC VALUATION ENGINE
**Penulis & Pengembang:** Mukhammad Rekza Mufti (Data & System Analyst)  
**Versi Sistem:** v2.0 (Laptop Enterprise Intelligence Edition)  
**Rentang Historis Master Katalog:** 2010 – 2026 (10 Brand Terkemuka Indonesia)  
**Waktu Rilis:** 2026  
**Platform Deploy:** Streamlit Community Cloud (Python 3.13 Runtime)  

---

# DAFTAR ISI
1. [BAB I: Pendahuluan & Latar Belakang Masalah Pasar Laptop](#bab-i-pendahuluan--latar-belakang-masalah-pasar-laptop)
2. [BAB II: Arsitektur Sistem End-to-End](#bab-ii-arsitektur-sistem-end-to-end)
3. [BAB III: Kamus Data & Spesifikasi Lengkap Parameter Output](#bab-iii-kamus-data--spesifikasi-lengkap-parameter-output)
4. [BAB IV: Logika Matematis, Model Ekonometrik & Teori Valuasi](#bab-iv-logika-matematis-model-ekonometrik--teori-valuasi)
5. [BAB V: Taksonomi Master Katalog Laptop 16 Tahun (2010–2026)](#bab-v-taksonomi-master-katalog-laptop-16-tahun-20102026)
6. [BAB VI: Panduan Instalasi & Operasional](#bab-vi-panduan-instalasi--operasional)

---

# BAB I: Pendahuluan & Latar Belakang Masalah Pasar Laptop

### 1.1 Kompleksitas & Asimetri Informasi Pasar Laptop Sekunder Indonesia
Pasar laptop bekas di Indonesia memiliki tingkat kompleksitas teknis dan risiko asimetri informasi yang sangat tinggi dibandingkan perangkat elektronik lainnya:

1. **Hierarki Prosesor & Penamaan Generasi CPU:**
   - Penjual sering menulis judul menyesatkan (misal "Laptop Core i7 Gaming Murah Rp 2.5 Juta") yang sebenarnya merupakan Intel Core i7 Generasi 1 (rilis 2010) dengan grafis terintegrasi usang.
   - Perbedaan sufiks prosesor performa tinggi (H, HX, HS) vs hemat daya (U, P, Y) menghasilkan disparitas performa komputasi hingga 300%.
2. **Kondisi Baterai & Siklus Pengisian (Cycle Count / Baterai Drop):**
   - Fenomena "Baterai Drop / Harus Sambil Colok Charger" sangat masif pada laptop bekas, menurunkan nilai likuiditas aset hingga 20% - 25%.
   - Pada lini Apple MacBook, Battery Cycle Count (CC) dan Battery Health (BH %) menjadi acuan penentuan harga pasar sekunder.
3. **Kualitas Panel Layar (Whitespot, Dead Pixel & Flexgate):**
   - Cacat backlight seperti Whitespot (titik putih pada layar) dan Dead Pixel sering disembunyikan di foto iklan.
   - Pada seri MacBook, masalah keretakan kabel fleksibel engsel (Flexgate) menyebabkan layar mati pada sudut buka tertentu.
4. **Struktur Mekanis Engsel (Hinge Failure):**
   - Engsel patah atau kendor akibat material plastik yang rapuh (sering terjadi pada laptop consumer) menurunkan nilai jual drastis karena mahalnya biaya penggantian sasis.
5. **Kunci Firmware, Keamanan Enterprise & BIOS Password:**
   - Laptop ex-kantor korporat (ThinkPad, Latitude, EliteBook) kerap mengalami penguncian supervisor BIOS password atau Computrace Absolute Persistence yang aktif, membatasi hak akses pengguna secara permanen.
6. **Praktek Iklan Clickbait DP / Paylater:**
   - Penjual online mencantumkan nominal DP uang muka cicilan (misal Rp 1.500.000 untuk ROG Strix RTX 4080) pada kolom harga tunai marketplace.

---

# BAB II: Arsitektur Sistem End-to-End

```text
+-----------------------------------------------------------------------------------+
|                        1. DATA HARVESTING & INGESTION                             |
|  - E-Commerce & Marketplace: OLX Indonesia, Tokopedia, Shopee, FB Marketplace      |
|  - Multi-threaded Crawlers, Header Spoofing & Request Pipeline                    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                   2. AI & NLP DATA REFINEMENT PIPELINE                            |
|  - Indonesian Laptop Slang Dictionary (Garansi ID, Baterai Drop, Whitespot, Engsel)|
|  - DP Scam, Fake CPU Gen & Locked BIOS Detector                                   |
|  - Hardware Metadata Extractor (CPU, GPU, RAM, SSD NVMe, Battery Wh, Layar)       |
|  - Deep Generational Entity Matcher (N-Gram Token & Verifikasi Generasi CPU/Chip) |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     3. RELATIONAL DATABASE LAYER (SQLite)                         |
|  - master_brands (Apple, Lenovo, ASUS, Acer, HP, Dell, MSI, Axioo, Huawei, MS)    |
|  - master_models (Hardware Specs: CPU, GPU TGP, Cinebench, Display, RAM Slots)   |
|  - master_variants (Konfigurasi RAM/Storage & MSRP Baru OTR)                       |
|  - scraped_listings (Cleaned Secondary Market Listings)                           |
|  - market_price_stats (Agregasi Harian Kuartil P25, FMV, P75)                     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                 4. ECONOMETRIC & PRICING ANALYTICS ENGINE                         |
|  - Tukey Interquartile Range (IQR) Outlier Filter                                 |
|  - Hedonic Quality Pricing Model (Penyesuaian Baterai, Layar, Engsel, Charger)    |
|  - Multi-Tier Depreciation Engine (Apple Silicon vs Business vs Gaming vs Entry)  |
|  - Fama Arbitrage Opportunity Scanner (Super Arbitrage, High, Moderate)           |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|         5. MODULAR STREAMLIT USER INTERFACE & VISUALIZATION (views/)              |
|  - views/market_overview.py (Dashboard Makro & Featured Flagships Showcase)       |
|  - views/fmv_calculator.py (Kalkulator FMV + Foto Produk + 8 Penalti Hedonik)     |
|  - views/price_corridors.py (3-Tier Price Corridors & Quantiles Bar Chart)        |
|  - views/arbitrage_radar.py (Arbitrage Scanner & Top 3 Visual Deal Cards)         |
|  - views/spec_matrix.py (Head-to-Head Comparison & Side-by-Side Photo Cards)     |
|  - views/master_catalog.py (Master Explorer: Tabel Lengkap vs Galeri Kartu Visual)|
|  - views/data_explorer.py (Live Raw Listing Audit & Test Parser NLP)             |
|  - URL State Sync via st.query_params (Shareable Module Links)                    |
+-----------------------------------------------------------------------------------+
```

---

# BAB III: Kamus Data & Spesifikasi Lengkap Parameter Output

### 3.1 Parameter Identitas & Taksonomi Master Katalog
1. `brand_name` (String): Produsen resmi laptop (Apple, Lenovo, ASUS, Acer, HP, Dell, MSI, Axioo, Huawei, Microsoft).
2. `model_name` (String): Lini model laptop (misal ThinkPad X1 Carbon Gen 11, ROG Zephyrus G14, MacBook Pro 14 M3 Pro).
3. `variant_name` (String): Nama lengkap varian spesifikasi (misal ROG Zephyrus G14 R9 RTX 4060 16GB/1TB).
4. `series` (String): Segmen lini produk (ThinkPad, Legion, ROG, TUF, ZenBook, XPS, Alienware, Pongo, MateBook, Surface).
5. `release_year` (Integer): Tahun peluncuran resmi di pasar (2010 - 2026).
6. `ram_gb` (Integer): Kapasitas RAM fisik dalam Gigabyte (4, 8, 16, 24, 32, 64 GB).
7. `storage_gb` (Integer): Kapasitas internal SSD dalam Gigabyte / Terabyte (256, 512, 1024, 2048 GB).
8. `official_msrp_new` (Numeric IDR): Harga resmi retail On-The-Road (OTR) saat peluncuran baru di Indonesia.

### 3.2 Parameter Spesifikasi Teknis Hardware
9. `processor_brand` (String): Produsen prosesor (Intel, AMD, Apple Silicon).
10. `processor_model` (String): Model lengkap prosesor (Intel Core Ultra 7 155H, Ryzen 7 7840HS, Apple M3 Pro).
11. `cpu_architecture` (String): Konfigurasi inti dan arsitektur prosesor.
12. `cpu_cores` / `cpu_threads` (Integer): Jumlah inti fisik dan thread komputasi.
13. `cinebench_score` (Integer): Skor benchmark Cinebench R23 Multi-Core.
14. `gpu_brand` / `gpu_model` (String): Unit pemrosesan grafis diskrit / terintegrasi.
15. `vram_gb` (Integer): Kapasitas video RAM grafis diskrit (GB).
16. `tgp_watt` (Integer): Total Graphics Power GPU dalam Watt.
17. `display_type` (String): Teknologi panel layar (OLED, Mini-LED Liquid Retina XDR, IPS-Level, Anti-Glare).
18. `screen_size_inch` (Float): Ukuran diagonal layar dalam inci (13.0" s/d 17.3").
19. `refresh_rate_hz` (Integer): Laju penyegaran layar (60Hz, 120Hz, 144Hz, 165Hz, 240Hz).
20. `resolution` (String): Resolusi native panel display (FHD, QHD+, 2.8K, 4K UHD).
21. `color_gamut` (String): Cakupan spektrum warna (100% sRGB, 100% DCI-P3, 45% NTSC).
22. `ram_type` (String): Standar memori (DDR4-3200, DDR5-5600, LPDDR5X-7467, Unified Memory).
23. `is_ram_upgradeable` (Boolean): Ketersediaan slot SODIMM fisik untuk ekspansi RAM.
24. `storage_interface` (String): Jalur antarmuka penyimpanan (NVMe PCIe Gen4, PCIe Gen3, SATA).
25. `storage_slots` (Integer): Jumlah slot M.2 yang tersedia.
26. `battery_wh` (Integer): Kapasitas baterai dalam Watt-hour (Wh).
27. `charger_watt` (Integer): Daya adaptor pengisian daya (Watt).
28. `weight_kg` (Float): Bobot total laptop dalam kilogram.
29. `chassis_material` (String): Material sasis bodi laptop (Magnesium-Aluminum, Carbon Fiber, CNC Aluminum, Polycarbonate).
30. `os_at_launch` (String): Versi sistem operasi saat rilis.

### 3.3 Parameter Atribut Pasar Sekunder
31. `warranty_type` (String): Asal unit dan garansi (Resmi Indonesia, Ex-Inter, Garansi Distributor).
32. `warranty_status` (String): Status keaktifan garansi (Aktif Masih Garansi Pabrik, Habis Ex-Resmi, Garansi Toko 1 Bulan).
33. `battery_condition` (String): Kondisi baterai (Normal Awet, Normal Standar, Baterai Drop Colok Terus, Baterai Kembung).
34. `battery_health_pct` (Integer): Persentase Battery Health aktual (40% - 100%).
35. `battery_cycle_count` (Integer): Siklus pengisian baterai aktual.
36. `completeness` (String): Kelengkapan unit jual (Fullset Original Dus+Charger Ori, Unit + Charger Ori, Charger OEM, Batangan).
37. `physical_grade` (String): Grade kondisi fisik bodi (Grade A+ Like New 99%, Grade A Mulus 95%, Grade B Lecet Wajar, Grade C Dent/Baret).
38. `hinge_condition` (String): Kondisi engsel sasis (Normal Kokoh vs Engsel Kendor/Patah).
39. `screen_condition` (String): Kondisi panel layar (Normal Jernih, Whitespot Tipis, Whitespot Tebal, Dead Pixel, Layar Bergaris/Flexgate).
40. `keyboard_condition` (String): Kondisi keyboard & lampu backlight (Normal Aktif, Backlight Mati, Tombol Minus/Macet).
41. `bios_mdm_status` (String): Keamanan firmware (Clean Bebas Password vs BIOS Locked / Computrace / MDM).
42. `is_dp_price` (Boolean): Flag deteksi perangkap iklan DP / Cicilan semu.

### 3.4 Parameter Valuasi & Ekonometrik
43. `price_p25_bargain` (Numeric IDR): Kuartil 1 batas bawah harga beli murah (Bargain Hunter Target).
44. `price_median_fmv` (Numeric IDR): Nilai Pasar Wajar ekuilibrium (Fair Market Value).
45. `price_p75_pristine` (Numeric IDR): Kuartil 3 batas atas kondisi istimewa.
46. `hedonic_adjusted_price` (Numeric IDR): Nilai valuasi final setelah penyesuaian parameter kualitas riil laptop.
47. `real_depreciation_pct` (Numeric %): Persentase depresiasi riil dari MSRP Baru terhadap FMV.
48. `arbitrage_discount_pct` (Numeric %): Persentase diskon arbitrase terhadap FMV pasar.
49. `arbitrage_deal_tier` (String): Klasifikasi arbitrase (Tier 1: Super Arbitrage >=22%, Tier 2: High Arbitrage 15-21%, Tier 3: Moderate 12-14%).

---

# BAB IV: Logika Matematis, Model Ekonometrik & Teori Valuasi

### 4.1 Model Penyesuaian Harga Hedonik (Lancaster-Rosen Hedonic Pricing)
Nilai sebuah laptop bekas dihitung berdasarkan dekomposisi atribut kualitas intrinsik hardware, kesehatan baterai, dan integritas sasisnya:

$$\text{FMV}_{\text{Final}} = \text{Base FMV}_{\text{Median}} \times \left(1 + \sum \Delta_{\text{Hedonik}}\right)$$

Tabel Koefisien Bobot Hedonik:
- **Status Garansi & Asal Distribusi:**
  - Garansi Resmi Aktif (>6 bln): $\Delta = +10\%$
  - Habis Garansi Resmi: $\Delta = 0\%$
  - Ex-Inter / Distributor: $\Delta = -8\%$
- **Kondisi Baterai & Daya:**
  - Baterai Awet Sehat (BH $\ge 88\%$ / CC $< 300$): $\Delta = +3\%$
  - Baterai Normal Standar: $\Delta = 0\%$
  - Baterai Drop (Harus Sambil Colok Charger): $\Delta = -20\%$
  - Baterai Kembung (Swollen Battery): $\Delta = -25\%$
- **Kelengkapan Unit & Charger:**
  - Fullset Original (Dus + Charger Ori): $\Delta = +3\%$
  - Unit + Charger Original (Tanpa Dus): $\Delta = 0\%$
  - Charger OEM / Adaptor KW: $\Delta = -6\%$
  - Batangan (Unit Only / Tanpa Charger): $\Delta = -12\%$
- **Kondisi Fisik Casing Bodi:**
  - Grade A+ (Like New 99%): $\Delta = +5\%$
  - Grade A (Mulus 95%): $\Delta = 0\%$
  - Grade B (Lecet Pemakaian Wajar): $\Delta = -7\%$
  - Grade C (Dent / Baret Kasar / Penyok): $\Delta = -15\%$
- **Kondisi Engsel Sasis (Hinge):**
  - Normal Kokoh: $\Delta = 0\%$
  - Engsel Patah / Kendor / Retak: $\Delta = -18\%$
- **Kondisi Layar Display Panel:**
  - Normal Jernih: $\Delta = 0\%$
  - Whitespot Tipis / Samar: $\Delta = -10\%$
  - Whitespot Tebal / Parah: $\Delta = -20\%$
  - Dead Pixel: $\Delta = -12\%$
  - Layar Bergaris / Flexgate: $\Delta = -35\%$
- **Keyboard & Backlight:**
  - Semua Normal Berfungsi: $\Delta = 0\%$
  - Backlight Mati: $\Delta = -4\%$
  - Tombol Keyboard Minus / Macet: $\Delta = -12\%$
- **Keamanan BIOS & MDM:**
  - Clean Bebas Reset: $\Delta = 0\%$
  - BIOS Lock / Computrace / MDM Locked: $\Delta = -30\%$

---

# BAB V: Taksonomi Master Katalog Laptop 16 Tahun (2010–2026)

Master katalog dirancang secara mendalam, presisi, dan valid mencakup **1.000 model laptop unik (10 Brand Utama x 100 Model)** lengkap dengan spesifikasi arsitektur prosesor, GPU, RAM, SSD, Display, dan MSRP rilis historis:

1. **Apple (100 Model, 2010–2026):**
   - *MacBook Air:* MacBook Air 11" & 13" Intel Core 2 Duo / Core i5 / i7 (2010–2017), Retina (2018–2020), M1 (2020), M2 13"/15" (2022–2023), M3 13"/15" (2024), hingga M4 roadmap (2025–2026).
   - *MacBook Pro:* Unibody non-Retina & Retina 13"/15" (2010–2015), Touch Bar 13"/15"/16" (2016–2020), M1 Pro/Max 14"/16" (2021), M2 Pro/Max (2023), M3 Pro/Max (2023–2024), M4 Pro/Max (2025–2026).
   - *12-inch Retina MacBook:* Core M/i5/i7 (2015–2017).

2. **Lenovo (100 Model, 2010–2026):**
   - *ThinkPad Enterprise:* X1 Carbon Gen 1 s/d Gen 13, X1 Nano, X1 Extreme, T-Series legendaris (T410, T420, T430, T440p, T450, T460, T470, T480, T490, T14 Gen 1–5), X-Series (X220, X230, X240, X250, X260, X270, X280, X390, X13), P-Series Mobile Workstation (P50 s/d P16), E/L-Series.
   - *Legion & LOQ Gaming:* Y520, Y530, Y540, Y740, Legion 5/5 Pro/7/7i (Gen 5 s/d Gen 9 RTX 2060–RTX 4090), Legion Slim, LOQ 15/16.
   - *IdeaPad & Yoga:* IdeaPad 3/5/Slim, IdeaPad Gaming 3, Yoga 2 Pro, Yoga 3, Yoga 7i, Yoga 9i, Yoga Slim 7 Aura Edition.

3. **ASUS (100 Model, 2010–2026):**
   - *ROG (Republic of Gamers):* ROG G73/G75/G55 (2010–2014), GL502/GL503, Strix G15/G16/G17/SCAR 15–18, Zephyrus G14/G15/G16/M16, Flow X13/Z13/X16.
   - *TUF Gaming:* FX504, FX505, A15/F15, A16 Advantage, A17.
   - *ZenBook:* ZenBook UX31/UX32 (2011), UX303, UX305, UX430, Pro Duo OLED, 14 OLED (UX3402/UX3405 Core Ultra), S 13/16 OLED.
   - *VivoBook & ExpertBook:* VivoBook S14/S15/Go/Pro, ExpertBook B1/B9 Enterprise.

4. **Acer (100 Model, 2010–2026):**
   - *Predator & Nitro:* Aspire V3/V5/V Nitro, Nitro 5 (AN515 gen GTX 1050 hingga RTX 3060), Nitro 16/17, Nitro V 15, Predator Helios 300/16/18, Predator Triton 300/500/14/17X.
   - *Swift & Spin:* Swift 1/3/5/7, Swift Go 14/16 OLED (Core Ultra & Ryzen 8000), Swift X RTX, Spin 3/5.
   - *Aspire & TravelMate:* Aspire 4741, 4752, E1/E5, Aspire 3/5/7, TravelMate P2/P4/P6.

5. **HP (Hewlett-Packard) (100 Model, 2010–2026):**
   - *Gaming:* Pavilion Gaming 15, OMEN 15/16/17, OMEN Transcend 14/16, Victus 15/16 (GTX 1650 s/d RTX 4070).
   - *Premium Spectre & Envy:* Spectre 13/x360 13/14/15/16, Envy 13/14/15/16/17, Envy x360.
   - *EliteBook & ProBook:* EliteBook 8440p s/d 840 G10, Folio 9470m/1040, Dragonfly G1–G4, ProBook 430/440/450 G1–G10.
   - *Pavilion & Essential:* Pavilion 14/15, HP 14/15s, OmniBook X AI.

6. **Dell (100 Model, 2010–2026):**
   - *XPS Premium:* XPS 13 (L321X s/d 9300, 9310, 9320 Plus, 9340 Core Ultra), XPS 15 (L501X s/d 9550, 9570, 7590, 9500, 9530), XPS 14, XPS 16, XPS 17 (9700–9730).
   - *Alienware & G-Series:* Alienware M11x/M14x/M17x, 15/17 R1–R5, m15/m17, x14/x15/x17, m16/m18, Dell Inspiron Gaming 7567/7577, G3, G5, G7, G15, G16.
   - *Latitude & Precision:* Latitude E6410 s/d 7420, 7440, 5440, Precision 3500–7700.
   - *Inspiron & Vostro:* Inspiron 14/15 3000/5000/7000 series.

7. **MSI (Micro-Star International) (100 Model, 2010–2026):**
   - *Gaming Lines:* GE60/GE62/GE75 Raider, GP62/GP66 Leopard, GL62/GL65, GF63/GF65 Thin, Bravo/Alpha AMD, Katana 15/17, Sword, Cyborg 15, Crosshair, Pulse, Stealth 14/16 AI Studio, Titan GT77.
   - *Business & Productivity:* Modern 14/15, Prestige 13/14/15/16 AI Evo, Summit E13/E14/E16 Flip.

8. **Axioo (100 Model, 2010–2026):**
   - *Pongo Gaming Series:* Pongo 3/5/7/9, Pongo 725, Pongo 760 (V1/V2), Pongo 960 (Core i9 + RTX 4070), Pongo Monster.
   - *Hype Series:* Hype 1, Hype 3, Hype 5, Hype 7, Hype 10, Hype OLED series.
   - *Z-Series & MyBook:* MyBook 11/14/14+, Z6, Z9, Z10, CyberBook, SlimBook, Chronos.
   - *Neon & Pico Vintage:* Neon MNC, CLW, HNM, TNN, Pico Pad/Netbook (2010–2013).

9. **Huawei (100 Model, 2016–2026):**
   - *MateBook X Series:* MateBook X, MateBook X Pro (2018–2024 OLED 3.1K).
   - *MateBook D Series:* MateBook D14, D15, D16 (Intel Core & AMD Ryzen multi-generation).
   - *MateBook Digital Series:* MateBook 13, 14, 14s (90Hz touch), 16, 16s (H-Series i9).
   - *MateBook E Series:* MateBook E 2-in-1 OLED convertible.

10. **Microsoft Surface (100 Model, 2012–2026):**
    - *Surface Pro Series:* Surface Pro 1 s/d Pro 11 Copilot+ PC (Snapdragon X Elite & Intel Core Ultra).
    - *Surface Laptop Series:* Surface Laptop 1 s/d Laptop 7 (13.5" & 15"), Surface Laptop Go 1–3, Surface Laptop Studio 1–2 (RTX 4060).
    - *Surface Book & Studio:* Surface Book 1–3 with Performance Base/dGPU.
    - *Surface Go:* Surface Go 1–4.

### 5.2 Fitur Sidebar "Master Catalog Data"
Modul ini memungkinkan user untuk:
1. Memantau total 1.000 model terdaftar di database secara real-time.
2. Memfilter data secara dinamis berdasarkan **Brand** (10 brand), **Series**, **Tahun Rilis (2010–2026)**, **GPU Type**, dan **RAM Range**.
3. Pencarian instan (Live Search) untuk model, CPU, atau GPU tertentu.
4. Export seluruh/sebagian data master katalog ke format **CSV** dengan 1-klik.
5. **Interactive Model Inspector:** Inspeksi mendalam spesifikasi hardware, MSRP, dan rentang harga pasar estimasi tiap model.

---

# BAB VI: Panduan Instalasi & Operasional

```bash
# 1. Masuk ke direktori
cd "Scrape Data Laptop"

# 2. Buat virtual environment & install dependensi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Jalankan pipeline inisialisasi, seeder katalog & dataset
python3 main.py

# 4. Jalankan Enterprise Streamlit Web Dashboard
streamlit run app.py
```
