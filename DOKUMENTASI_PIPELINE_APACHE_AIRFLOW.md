# DOKUMENTASI ARSITEKTUR & IMPLEMENTASI PIPELINE APACHE AIRFLOW
## Sistem Sinkronisasi Master Katalog Laptop, Scraping Pasar Sekunder & Fair Market Value (FMV)

---

### 1. Ringkasan Eksekutif

Dokumen ini menyajikan panduan arsitektur, spesifikasi teknis, dan implementasi operasional untuk menjalankan pipeline orkestrasi data berbasis **Apache Airflow** pada repositori `laptoppriceid`.

Pipeline ini bertanggung jawab secara otomatis untuk:
1. Memverifikasi integritas database master katalog (`laptop_bekas.db`).
2. Menarik data listing harga aktual dari pasar sekunder (OLX Indonesia) serta fallback marketplace secara berkala.
3. Melakukan normalisasi entitas (*entity matching*) antara listing pasar liar dengan master varian dan nomor sasis (*chassis SKU*).
4. Menghitung nilai wajar pasar (*Fair Market Value* / FMV) menggunakan metode statistik **Tukey Interquartile Range (IQR)** serta kalibrasi ekonometrik kurva depresiasi multi-kategori.
5. Memperbarui kolom `fair_market_value` pada master katalog (`master_models` & `master_variants`) dan memperluas basis data katalog teknis (LaptopMedia).
6. Menjalankan audit kualitas data (*data quality gate*) otomatis sebelum data disajikan ke dashboard analitik dan kalkulator trade-in Streamlit.

---

### 2. Arsitektur Data Pipeline End-to-End

```mermaid
flowchart TD
    subgraph SOU ["1. Sumber Data Eksternal"]
        LM["LaptopMedia Specs DB<br/>(14.033 Models, 20.331 Chassis)"]
        OLX["OLX Indonesia API / Scraper<br/>(Listing Pasar Sekunder)"]
        TKP["Marketplace Fallback Scraper<br/>(Carousell / Tokopedia)"]
    end

    subgraph DAG ["2. Apache Airflow DAG: dag_laptop_market_sync"]
        T1["Task 1: Environment & DB Health Check<br/>(t1_check_database_environment)"]
        T2["Task 2: Marketplace Scraping Ingestion<br/>(t2_scrape_marketplace_listings)"]
        T3["Task 3: Entity Matching & SKU Lookup<br/>(t3_match_listings_to_master_variants)"]
        T4["Task 4: Compute Fair Market Value<br/>(t4_compute_fair_market_values)"]
        T5["Task 5: Master Catalog Sync & Update FMV<br/>(t5_sync_laptopmedia_catalog_and_olx_fmv)"]
        T6["Task 6: Data Quality & Sanity Audit<br/>(t6_data_quality_audit)"]

        T1 --> T2 --> T3 --> T4 --> T5 --> T6
    end

    subgraph STO ["3. Lapisan Penyimpanan Data (Storage Layer)"]
        DB[("Database SQLite / PostgreSQL<br/>laptop_bekas.db")]
        T_BRAND["master_brands"]
        T_MODEL["master_models (fair_market_value)"]
        T_VAR["master_variants (fair_market_value)"]
        T_LOOKUP["kode_model_lookup (20.331 chassis)"]
        T_SCRAPE["scraped_listings"]
        T_STATS["market_price_stats"]

        DB --- T_BRAND
        DB --- T_MODEL
        DB --- T_VAR
        DB --- T_LOOKUP
        DB --- T_SCRAPE
        DB --- T_STATS
    end

    subgraph APP ["4. Lapisan Konsumsi Pengguna (Application Layer)"]
        APP_EXP["Master Catalog Explorer<br/>(views/master_catalog.py)"]
        APP_CALC["Trade-In Matrix Calculator<br/>(views/tradein_calculator.py)"]
        APP_ANL["Market Analytics Dashboard<br/>(views/market_analytics.py)"]
    end

    SOU --> DAG
    DAG --> STO
    STO --> APP
```

---

### 3. Rincian Alur Kerja Setiap Task Airflow

#### Task 1: Environment & Database Health Check (`t1_check_database_environment`)
- **Tujuan**: Memastikan konektivitas database, integritas file database `laptop_bekas.db`, ketersediaan tabel utama (`master_models`, `master_variants`, `master_brands`), dan validasi path eksekusi.
- **Kriteria Keberhasilan**: Query `SELECT COUNT(*) FROM master_models` mengembalikan jumlah $\ge 1.000$ baris tanpa kegagalan I/O.
- **Failover**: Jika database terkorupsi atau path tidak valid, task gagal seketika (*fail-fast*) dan memicu notifikasi peringatan.

#### Task 2: Marketplace Scraping Ingestion (`t2_scrape_marketplace_listings`)
- **Tujuan**: Mengambil data iklan laptop bekas aktif dari marketplace (OLX Indonesia) dengan keyword dinamis berdasarkan brand utama (Lenovo, Apple, ASUS, Acer, HP, Dell, MSI, Axioo, Huawei, Microsoft).
- **Mekanisme**:
  - Request headers acak dan delay adaptor (0,5–1,5 detik) untuk menghindari pemblokiran IP / rate limiting.
  - Ekstraksi atribut listing: judul, harga mentah, lokasi penjual, URL listing, dan deskripsi produk.
  - Deteksi dan eliminasi otomatis listing penipuan (scam DP, harga fiktif di bawah ambang batas minimal Rp 500.000).
- **Penyimpanan**: Listing disimpan ke dalam tabel `scraped_listings` dengan status `matched_variant_id = NULL`.

#### Task 3: Entity Matching & SKU Lookup (`t3_match_listings_to_master_variants`)
- **Tujuan**: Menghubungkan judul iklan pasar liar ke entitas canonical di tabel `master_variants` dan `master_models`.
- **Algoritma**:
  1. **Direct SKU / Chassis Lookup**: Memindai kata kunci terhadap tabel `kode_model_lookup` (20.331 kode sasis seperti `20L7`, `A2337`, `FA506`, `G3-3590`).
  2. **Tokenized Matching & Levenshtein Distance**: Pencocokan token brand, seri, prosesor (misal: Core i5-8250U, Ryzen 7 5800H, Apple M1), dan kapasitas memori/penyimpanan.
  3. **Penyimpanan Status**: Jika confidence score $\ge 0.75$, `matched_variant_id` diperbarui di tabel `scraped_listings`.

#### Task 4: Compute Fair Market Value (`t4_compute_fair_market_values`)
- **Tujuan**: Menghitung estimasi harga pasar wajar dari kumpulan listing yang telah terverifikasi.
- **Metode Statistik**:
  - **Filter Outlier Tukey IQR**: Menghilangkan harga listing di luar batas $[Q_1 - 1.5 \times \text{IQR}, Q_3 + 1.5 \times \text{IQR}]$ untuk membuang harga rusak atau anomali aksesoris.
  - **Metrik Utama**: Mengkalkulasi nilai Median Pasar, Min, Max, Standar Deviasi, dan Volume Listing ke tabel `market_price_stats`.

#### Task 5: Master Catalog Sync & Update FMV (`t5_sync_laptopmedia_catalog_and_olx_fmv`)
- **Tujuan**: Melakukan sinkronisasi master katalog dengan data teknis LaptopMedia dan mengisi kolom `fair_market_value` secara menyeluruh pada `master_models` dan `master_variants`.
- **Logika Penentuan Nilai FMV (Dual Approach)**:
  1. **Sampel Listing Riil Tersedia**: Mengambil nilai median aktual dari OLX yang telah difilter Tukey IQR.
  2. **Model Tanpa Sampel Langsung**: Menggunakan kurva depresiasi ekonometrik berdasarkan segmen perangkat:
     $$\text{FMV} = \text{MSRP} \times (1 - \text{DeprRate})^{\Delta \text{Tahun}}$$
     - *Apple MacBook*: Laju depresiasi ~12% per tahun.
     - *Gaming Laptop*: Laju depresiasi ~17% per tahun.
     - *Business Laptop*: Laju depresiasi ~15% per tahun.
     - *Budget / Consumer*: Laju depresiasi ~19% per tahun.
     - *Guardrails*: Nilai FMV dibatasi dengan ambang bawah minimum Rp 1.500.000 dan ambang atas 90% dari MSRP asli.
- **Pembersihan Redundansi**: Menjamin nama model bersih dari akhiran tahun berulang (misal: `Dell G15 (5515)` dinormalisasi menjadi `Dell G15 5515`).

#### Task 6: Data Quality & Sanity Audit (`t6_data_quality_audit`)
- **Tujuan**: Menjamin integritas skema dan akurasi data sebelum dirilis ke lingkungan produksi.
- **Pengujian yang Dilakukan**:
  - Memastikan seluruh model memiliki kolom `fair_market_value > 0`.
  - Memastikan 100% dari 20.331 kode sasis di `kode_model_lookup` terhubung secara valid (*foreign key integrity*).
  - Memastikan tidak ada nama model yang memiliki akhiran redundan `(YYYY)`.
  - Memverifikasi 10 brand utama Indonesia masing-masing memiliki $\ge 100$ model.

---

### 4. Implementasi Kode DAG Airflow

File DAG tersimpan pada `dags/dag_laptop_market_sync.py`:

```python
# -*- coding: utf-8 -*-
"""
DAG Apache Airflow: Otomasi Scraping Pasar Laptop, Ingesti Spesifikasi LaptopMedia,
dan Kalkulasi Fair Market Value (FMV) OLX.
"""

import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

ROOT_DIR = os.getenv("LAPTOPPRICEID_HOME", "/opt/airflow/dags/laptoppriceid")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

default_args = {
    "owner": "laptoppriceid",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=60),
}

# (Definisi Callable Task functions terlampir di file dags/dag_laptop_market_sync.py)

with DAG(
    dag_id="dag_laptop_market_sync",
    default_args=default_args,
    description="Pipeline ETL Master Katalog Laptop, Scraping Pasar & Fair Market Value OLX",
    schedule_interval="0 2 * * *",  # Jam 02:00 UTC (09:00 WIB)
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["laptop", "scraping", "olx", "fmv", "laptopmedia", "production"],
) as dag:

    t1_check_env = PythonOperator(
        task_id="t1_check_database_environment",
        python_callable=task_check_db_connectivity,
    )

    t2_scrape_marketplace = PythonOperator(
        task_id="t2_scrape_marketplace_listings",
        python_callable=task_run_olx_laptop_scraping,
    )

    t3_entity_matching = PythonOperator(
        task_id="t3_match_listings_to_master_variants",
        python_callable=task_run_entity_matching,
    )

    t4_calculate_fmv = PythonOperator(
        task_id="t4_compute_fair_market_values",
        python_callable=task_calculate_fair_market_value,
    )

    t5_sync_master_catalog = PythonOperator(
        task_id="t5_sync_laptopmedia_catalog_and_olx_fmv",
        python_callable=task_sync_laptopmedia_and_fmv_columns,
    )

    t6_data_quality_audit = BashOperator(
        task_id="t6_data_quality_audit",
        bash_command=f"python3 {os.path.join(ROOT_DIR, 'tests', 'test_chassis_taxonomy.py')}",
    )

    t1_check_env >> t2_scrape_marketplace >> t3_entity_matching >> t4_calculate_fmv >> t5_sync_master_catalog >> t6_data_quality_audit
```

---

### 5. Panduan Instalasi & Deployment Apache Airflow

#### Opsi A: Deployment Mandiri di Lingkungan Lokal / VM (Virtualenv)

1. **Persiapan Virtual Environment**:
   ```bash
   python3 -m venv airflow_env
   source airflow_env/bin/activate
   pip install --upgrade pip
   ```

2. **Instalasi Apache Airflow dan Dependensi Proyek**:
   ```bash
   AIRFLOW_VERSION=2.9.2
   PYTHON_VERSION="$(python --version | cut -d ' ' -f 2 | cut -d '.' -f 1-2)"
   CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
   pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
   pip install sqlalchemy pandas numpy requests beautifulsoup4 rapidfuzz
   ```

3. **Inisialisasi Database Airflow & Konfigurasi**:
   ```bash
   export AIRFLOW_HOME=~/airflow
   export LAPTOPPRICEID_HOME="/Users/macbookair/Documents/Scrape Data Laptop"
   airflow db migrate
   ```

4. **Registrasi DAG**:
   Buat symbolic link atau salin file DAG ke folder dags Airflow:
   ```bash
   mkdir -p ~/airflow/dags
   ln -s "${LAPTOPPRICEID_HOME}/dags/dag_laptop_market_sync.py" ~/airflow/dags/
   ```

5. **Menjalankan Scheduler dan Webserver**:
   ```bash
   # Terminal 1: Webserver UI
   airflow webserver --port 8080

   # Terminal 2: Scheduler
   airflow scheduler
   ```
   Buka UI Airflow pada browser: `http://localhost:8080`.

---

#### Opsi B: Deployment Produksi Menggunakan Docker Compose

Berikut adalah konfigurasi `docker-compose.yaml` yang siap diintegrasikan:

```yaml
version: '3.8'
x-airflow-common:
  &airflow-common
  image: apache/airflow:2.9.2-python3.11
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    LAPTOPPRICEID_HOME: /opt/airflow/dags/laptoppriceid
    PYTHONPATH: /opt/airflow/dags/laptoppriceid
  volumes:
    - ./dags:/opt/airflow/dags/laptoppriceid/dags
    - ./:/opt/airflow/dags/laptoppriceid
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
  depends_on:
    - postgres

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5

  airflow-init:
    <<: *airflow-common
    command: version
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_MIGRATE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: admin
      _AIRFLOW_WWW_USER_PASSWORD: admin_password

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: always

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
      interval: 30s
      timeout: 10s
      retries: 5
    restart: always

volumes:
  postgres-db-volume:
```

Langkah peluncuran:
```bash
docker compose up airflow-init
docker compose up -d
```

---

### 6. Jadwal Eksekusi, SLA, dan Notifikasi

- **Cron Schedule**: `0 2 * * *` (Pukul 02:00 UTC / 09:00 WIB setiap hari kerja dan akhir pekan).
- **Service Level Agreement (SLA)**: 45 Menit untuk keseluruhan pipeline run.
- **Maksimal Durasi Eksekusi (`execution_timeout`)**: 60 Menit.
- **Retry Policy**: 2 kali percobaan ulang dengan jeda 5 menit (`retry_delay = timedelta(minutes=5)`).
- **Alerting**: Mengaktifkan `email_on_failure = True` atau callback webhook ke Telegram/Slack jika salah satu task mengalami status `FAILED`.

---

### 7. Pengujian dan Verifikasi Pipeline

Untuk memverifikasi task secara individual tanpa menunggu trigger scheduler Airflow, gunakan CLI testing:

```bash
# Uji coba Task 1 (Database Check)
airflow tasks test dag_laptop_market_sync t1_check_database_environment 2026-11-05

# Uji coba Task 4 (Kalkulasi FMV)
airflow tasks test dag_laptop_market_sync t4_compute_fair_market_values 2026-11-05

# Uji coba Task 5 (Sinkronisasi Katalog & Kolom FMV)
airflow tasks test dag_laptop_market_sync t5_sync_laptopmedia_catalog_and_olx_fmv 2026-11-05

# Uji coba Task 6 (Audit Kualitas Data)
airflow tasks test dag_laptop_market_sync t6_data_quality_audit 2026-11-05
```

---

### 8. Ringkasan Status Database Terkini

| Parameter Metrik | Hasil Verifikasi Terkini |
| :--- | :--- |
| **Total Brand Terdaftar** | 27 Brand |
| **Total Model di Master Catalog** | 8.444 Model |
| **Total Varian Spesifikasi** | 8.444 Varian |
| **Total Indeks Nomor Sasis / SKU (`kode_model_lookup`)** | 20.331 Chassis Records |
| **Cakupan Nilai Fair Market Value (`fair_market_value`)** | 100,0% (8.444 / 8.444) |
| **Rata-Rata Fair Market Value (Bekas Pasar OLX)** | Rp 12.410.616 |
| **Ukuran File Database (`laptop_bekas.db`)** | 14 MB (Aman untuk GitHub) |
| **Status Unit Tests (`python -m unittest`)** | 35 Lulus, 0 Gagal (100% OK) |
