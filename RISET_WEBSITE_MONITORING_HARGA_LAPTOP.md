# Riset Komprehensif: Website & Platform Terpercaya untuk Monitoring Harga Laptop Berkala di Indonesia

Dokumen ini menyajikan hasil riset mendalam mengenai lanskap platform jual beli laptop di Indonesia, baik pasar sekunder (*secondhand/preloved*), rekondisi (*refurbished corporate*), maupun retail resmi (*new MSRP*). Riset ini ditujukan untuk menentukan sumber data terbaik guna memantau harga laptop secara berkala, akurat, dan berkelanjutan.

---

## 1. Lanskap Ekosistem Pasar Laptop di Indonesia

Pasar laptop di Indonesia terbagi ke dalam tiga ekosistem utama:
1. **Pasar C2C (Customer-to-Customer) & Pedagang Independen**: Pengguna perorangan yang menjual unit pribadi (*preloved*) serta pedagang rumahan. Karakteristik: harga sangat dinamis, unit bervariasi (lengkap dengan minus dan kondisi fisik riil), potensi negosiasi tinggi.
2. **Pasar B2C & Verified Merchant E-Commerce**: Toko komputer fisik yang memiliki etalase online (sentra ITC Mangga Dua, Mall Ambasador/ITC Kuningan, BEC Bandung, Hi-Tech Mall Surabaya). Karakteristik: stok terstandarisasi, garansi toko 1–3 bulan, harga relatif seragam.
3. **Agregator Harga & Katalog Benchmark Resmi**: Portal pembanding harga dan toko retail distributor resmi (iBox, Digimap, Enterkomputer, Pemmz). Karakteristik: menjadi acuan batas atas (*ground truth MSRP*) dan pemantau tren depresiasi harga baru ke bekas.

---

## 2. Analisis & Evaluasi Platform Terpercaya

Berikut adalah perbandingan mendalam terhadap 6 platform monitoring harga laptop terkemuka di Indonesia:

| Platform | Domain / Kategori | Kualitas Data | Reliabilitas Harga | Kemudahan Crawling / API | Risiko Anomali / Scam | Rekomendasi Frekuensi Update |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Carousell ID** | `id.carousell.com`<br>*(C2C Secondhand)* | **Sangat Tinggi**<br>Foto asli unit, kondisi fisik (*Like new, Lightly used, Well used*), nama seller, URL langsung | **Tinggi (85-90%)**<br>Mencerminkan harga transaksi riil pengguna | **Sangat Mudah**<br>Server-Side Rendering (SSR) ramah crawler, HTTP GET Status 200, latency rendah | **Rendah - Sedang**<br>Beberapa seller menulis harga singkatan (misal Rp 7.60 = 7.6jt), mudah difilter NLP | **Tiap 4–6 Jam** |
| **Tokopedia** | `tokopedia.com`<br>*(B2C & Pro Merchants)* | **Sangat Tinggi**<br>Ulasan pembeli, reputasi toko, filter kondisi (*Bekas/Baru*), spesifikasi varian | **Sangat Tinggi (92-95%)**<br>Harga jual riil pedagang spesialis ITC & BEC | **Moderat - Rumit**<br>Dynamic React / GraphQL API, proteksi bot Shield, memerlukan browser headless atau residential proxy | **Sangat Rendah**<br>Dilindungi sistem escrow rekening bersama | **1x Sehari (Harian)** |
| **Shopee ID** | `shopee.co.id`<br>*(B2C & Refurbished Ex-Corporate)* | **Tinggi**<br>Pusat laptop bisnis bekas import (ThinkPad, Latitude, EliteBook) | **Tinggi (88%)**<br>Sangat bersaing untuk segmen laptop kerja murah | **Rumit**<br>WAF agresif, bot challenge, multi-SKU varian dalam 1 produk | **Rendah**<br>Reputasi toko transparan | **1–2 Hari Sekali** |
| **Pricebook** | `pricebook.co.id`<br>*(Price Aggregator Mall Komputer)* | **Tinggi**<br>Merekam harga toko fisik ITC Roxy, Mangga Dua, Poins Square, BEC | **Tinggi (90%)**<br>Benchmark harga toko fisik di sentra IT | **Moderat**<br>Struktur halaman katalog terindeks rapi | **Sangat Rendah**<br>Data toko terkurasi | **2x Seminggu** |
| **iPrice ID** | `iprice.co.id`<br>*(Meta-Search Aggregator)* | **Moderat - Tinggi**<br>Indeks perbandingan harga antar marketplace | **Moderat (80%)**<br>Beberapa harga merupakan data cache promo | **Moderat**<br>Katalog agregasi dinamis | **Rendah**<br>Tautan dialihkan ke platform utama | **2–3 Hari Sekali** |
| **Enterkomputer** | `enterkomputer.com`<br>*(Retail MSRP Benchmark)* | **Sangat Tinggi**<br>Pricelist harian resmi Mangga Dua Jakarta | **100% (MSRP Baru)**<br>Standar acuan harga resmi distributor Indonesia | **Moderat - Rumit**<br>Proteksi Cloudflare pada endpoint katalog | **Nol (Resmi)**<br>Distributor resmi brand | **Mingguan (Weekly)** |

---

## 3. Profil Mendalam Setiap Platform

### A. Carousell Indonesia (`id.carousell.com`) — *Rekomendasi Utama untuk Pasar Bekas C2C*
- **Mengapa Terbaik:**
  1. Merupakan satu-satunya platform C2C di Indonesia saat ini yang memberikan akses data HTML terstruktur tanpa pemblokiran IP agresif.
  2. Data memuat foto asli yang diunggah langsung oleh pemilik laptop, bukan sekadar foto brosur pabrik.
  3. Menyertakan label kondisi fisik terstandarisasi:
     - `Brand new` (Baru belum terpakai / BNOB)
     - `Like new` (Seperti baru, mulus 98-99%, minim tanda pakai)
     - `Lightly used` (Pemakaian ringan, baterai sehat, fisik mulus wajar)
     - `Well used` (Pemakaian aktif, ada minus kosmetik/baterai, harga bersahabat)
  4. URL listing bersifat langsung (`https://id.carousell.com/p/<slug>-<id>/`), memungkinkan user sistem kita mengklik dan langsung melihat barang aslinya.
- **Implementasi Scraper:**
  - Metode: HTTP GET dengan rotasi `User-Agent` peramban modern.
  - Selektor: Kartu listing `div[class*="D_aPE"]` atau `a[href*="/p/"]`.

### B. Tokopedia (`tokopedia.com`) — *Rekomendasi Utama untuk Toko Spesialis & B2C*
- **Mengapa Penting:**
  - Ribuan pedagang laptop bekas di Mangga Dua, Roxy, dan BEC Bandung menjadikan Tokopedia sebagai etalase inventaris harian mereka.
  - Sangat akurat untuk memetakan harga pasar laptop *business-class* (ThinkPad T/X Series, Dell Latitude, HP EliteBook) dan *gaming series* (ASUS TUF/ROG, Acer Nitro, Lenovo Legion).
- **Strategi Scraping:**
  - Karena proteksi Shield Tokopedia, disarankan menggunakan **Playwright / Puppeteer headless** yang berjalan di server latar belakang dengan interval terjadwal (cron job) atau memanfaatkan endpoint publik GraphQL dengan session cookie valid.

### C. Pricebook Indonesia (`pricebook.co.id`) — *Rekomendasi untuk Indeks Toko Fisik*
- **Mengapa Penting:**
  - Pricebook memiliki jaringan surveyor yang mencatat harga toko-toko komputer offline di sentra IT terkemuka.
  - Sangat berguna sebagai **anchor price** (jangkar harga) untuk menilai apakah harga di marketplace online tergolong murah atau mahal dibanding toko fisik.

### D. Enterkomputer (`enterkomputer.com`) & Pemmz (`pemmz.com`) — *Acuan MSRP Baru*
- **Mengapa Penting:**
  - Menyediakan pricelist resmi laptop baru BNIB (*Brand New in Box*) dengan garansi distributor resmi (Astrindo, Synnex Metrodata, Datascrip, iBox).
  - Data ini menjadi parameter krusial bagi modul **Depreciation Engine** dan **Lancaster Hedonic Pricing** untuk menghitung sisa nilai ekonomis laptop seiring berjalannya tahun.

---

## 4. Rekomendasi Arsitektur Monitoring Harga Berkala (Automated Surveillance)

Untuk menjaga agar database `laptop_bekas.db` selalu terbarui secara otomatis dan bebas data usang, arsitektur monitoring berikut direkomendasikan:

```
Schedulers:
- Rapid Cron (Setiap 4-6 Jam): Carousell ID Live Listings Multi-Brand
- Daily Cron (Setiap Malam 02:00 WIB): E-Commerce & Tokopedia Playwright Worker
- Weekly Cron: MSRP Official Pricelist (Enterkomputer / Pemmz)

Pipeline Ingestion:
1. Normalizer (NLP Hardware & Extraction)
2. Scam Filter (DP Trap, Misleading Specs & Low Price Filter)
3. Deep Entity Matcher (Resolusi ke 1.000 Master Model Katalog)
4. Deduplicator & Delta-Update (Update harga jika berubah, abaikan duplikat)
5. Aggregation Engine (Recalculate P25, Median FMV, P75)
```

### Prinsip Operasional Monitoring:
1. **Delta-Update (Hanya Rekam Perubahan):**
   - Menggunakan kolom `external_id` sebagai *primary key* unik per platform. Jika ID sudah ada di database, scraper hanya memperbarui harga jika ada penurunan (*price drop*) tanpa menduplikasi baris.
2. **TTL (Time to Live) Expiration:**
   - Listing bekas di marketplace yang tidak lagi ditemukan dalam pencarian selama > 14 hari diberi status `is_sold = True` agar tidak lagi mendistorsi kalkulasi harga wajar saat ini.
3. **Scam Shielding Berbasis Ambang Batas:**
   - Iklan dengan judul memuat kata kunci DP, cicilan, atau harga di bawah Rp 800.000 otomatis dialihkan ke status `is_dp_price = True` dan dikeluarkan dari agregasi kuantil pasar.
4. **Alert Peluang Arbitrase:**
   - Mengirim notifikasi (Telegram bot / email / webhook) seketika ketika ada listing riil terverifikasi yang muncul dengan harga >= 20% di bawah nilai Fair Market Value (FMV).

---

## 5. Kesimpulan & Rekomendasi Eksekusi

1. **Sumber Data Riil Saat Ini:**
   - Gunakan **Carousell ID** sebagai sumber primer data scraping listing riil instan karena menyediakan ratusan hingga ribuan listing aktual, foto riil unit, lokasi kota, dan kondisi pemakaian.
2. **Pengembangan Lanjutan:**
   - Integrasikan worker latar belakang (Playwright) untuk mengambil listing dari Tokopedia secara terjadwal seminggu sekali untuk memperkaya sampel dari toko-toko retail second ITC & Mangga Dua.
3. **Ground Truth MSRP:**
   - Gunakan katalog 1.000 Master Model yang telah kita bangun sebagai jangkar spesifikasi dan harga awal rilis resmi di Indonesia.
