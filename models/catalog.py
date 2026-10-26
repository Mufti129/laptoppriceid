from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Float, DateTime, Date, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from models.database import Base

class MasterBrand(Base):
    """
    Entitas Produsen / Brand Laptop Resmi di Indonesia.
    """
    __tablename__ = "master_brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # Apple, Lenovo, ASUS, Acer, HP, Dell, MSI, Axioo, Huawei, Microsoft
    country_origin = Column(String(50), nullable=True)                 # United States, Taiwan, China, Indonesia
    tier_category = Column(String(50), default="Mainstream")           # Flagship-Dominant, Business-Enterprise, Gaming-Powerhouse, Value-Local
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    models = relationship("MasterModel", back_populates="brand", cascade="all, delete-orphan")


class MasterModel(Base):
    """
    Entitas Model Laptop beserta Spesifikasi Teknis Hardware Utama.
    """
    __tablename__ = "master_models"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("master_brands.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)              # e.g. ThinkPad X1 Carbon Gen 11, ROG Zephyrus G14, MacBook Pro 14 M3
    series = Column(String(50), nullable=True)                          # ThinkPad, Legion, ROG, TUF, ZenBook, XPS, MacBook Pro, Pongo
    chassis_code = Column(String(50), nullable=True, index=True)        # Kode Sasis / SKU Pabrikan: G614JV, 16IRX8, PHN16-71, A2681, 9320
    release_year = Column(Integer, nullable=False, index=True)          # 2010 - 2026
    
    # 1. Hardware: Processor / CPU
    processor_brand = Column(String(50), nullable=True)                 # Intel, AMD, Apple Silicon
    processor_model = Column(String(100), nullable=True)                # Intel Core Ultra 7 155H, AMD Ryzen 7 7840HS, Apple M3 Pro
    cpu_architecture = Column(String(100), nullable=True)               # 16-Core (6P + 8E + 2LPE), 8-Core Zen 4, 12-Core CPU
    cpu_cores = Column(Integer, nullable=True)                          # 8, 12, 14, 16, 24
    cpu_threads = Column(Integer, nullable=True)                        # 12, 16, 20, 24, 32
    cinebench_score = Column(Integer, nullable=True)                    # Estimasi Cinebench R23 Multi-Core

    # 2. Hardware: GPU & Grafis
    gpu_brand = Column(String(50), nullable=True)                       # NVIDIA, AMD, Intel, Apple
    gpu_model = Column(String(100), nullable=True)                      # GeForce RTX 4060 Laptop, Intel Iris Xe, Apple 18-Core GPU
    vram_gb = Column(Integer, default=0)                                # 4, 6, 8, 12, 16 GB (0 jika terintegrasi/iGPU)
    tgp_watt = Column(Integer, default=0)                               # Total Graphics Power (e.g. 45W, 105W, 140W, 175W)

    # 3. Hardware: Layar & Display Panel
    display_type = Column(String(100), nullable=True)                   # IPS-Level, OLED, Mini-LED Liquid Retina XDR, IPS Anti-Glare
    screen_size_inch = Column(Float, nullable=True)                     # 13.3, 14.0, 15.6, 16.0, 17.3
    refresh_rate_hz = Column(Integer, default=60)                       # 60, 90, 120, 144, 165, 240
    resolution = Column(String(50), nullable=True)                      # FHD (1920x1080), QHD+ (2560x1600), 4K UHD (3840x2160)
    color_gamut = Column(String(50), nullable=True)                     # 100% sRGB, 100% DCI-P3, 45% NTSC

    # 4. Memory & Storage Architecture
    ram_type = Column(String(50), nullable=True)                        # DDR4-3200, DDR5-5600, LPDDR5X-7500, Unified Memory
    is_ram_upgradeable = Column(Boolean, default=True)                  # True jika SODIMM dual-slot, False jika soldered onboard
    storage_interface = Column(String(50), default="NVMe PCIe Gen4")    # NVMe PCIe Gen3, PCIe Gen4, PCIe Gen5, SATA SSD
    storage_slots = Column(Integer, default=1)                          # 1, 2 M.2 slots

    # 5. Daya, Baterai, & Portabilitas
    battery_wh = Column(Integer, nullable=True)                         # 50, 70, 80, 90, 99 Wh
    charger_watt = Column(Integer, default=65)                          # 45W Type-C, 65W, 100W PD, 140W, 230W, 330W
    weight_kg = Column(Float, nullable=True)                            # 1.12, 1.40, 1.95, 2.30, 2.60 kg
    chassis_material = Column(String(100), nullable=True)               # Magnesium-Aluminum, Carbon Fiber, Anodized Aluminum, Polycarbonate

    # 6. Sistem Operasi & Media
    os_at_launch = Column(String(50), nullable=True)                    # Windows 11 Home, macOS Sonoma, Windows 10 Pro
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("MasterBrand", back_populates="models")
    variants = relationship("MasterVariant", back_populates="model", cascade="all, delete-orphan")


class MasterVariant(Base):
    """
    Varian Spesifik Berdasarkan Konfigurasi RAM, SSD Storage, dan Harga Resmi Peluncuran (MSRP OTR).
    """
    __tablename__ = "master_variants"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("master_models.id", ondelete="CASCADE"), nullable=False)
    variant_name = Column(String(150), nullable=False, index=True)      # e.g. ThinkPad X1 Carbon Gen 11 i7/16GB/512GB, ROG Zephyrus G14 RTX 4060 16GB/1TB
    ram_gb = Column(Integer, nullable=False)                            # 8, 16, 24, 32, 64 GB
    storage_gb = Column(Integer, nullable=False)                        # 256, 512, 1024 (1TB), 2048 (2TB)
    color_options = Column(String(200), nullable=True)                  # Eclipse Gray, Moonlight White, Deep Black, Space Gray
    official_msrp_new = Column(Numeric(15, 2), nullable=False)          # Harga Peluncuran Resmi OTR Indonesia (IDR)
    aliases = Column(Text, nullable=True)                               # Keyword pencarian & singkatan pasar (e.g. g14 4060, x1c gen11, mbp14 m3)
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("MasterModel", back_populates="variants")
    scraped_listings = relationship("ScrapedListing", back_populates="matched_variant")


class ScrapedListing(Base):
    """
    Data Listing Laptop Bekas / Sekunder yang diekstraksi dari Marketplace Indonesia.
    """
    __tablename__ = "scraped_listings"

    id = Column(Integer, primary_key=True, index=True)
    source_platform = Column(String(50), nullable=False, index=True)    # 'olx', 'tokopedia', 'facebook', 'shopee'
    external_id = Column(String(100), nullable=False, index=True)       # ID unik listing
    url = Column(Text, nullable=False)
    title = Column(String(300), nullable=False)
    raw_description = Column(Text, nullable=True)

    # Resolusi Varian oleh AI Matcher
    matched_variant_id = Column(Integer, ForeignKey("master_variants.id"), nullable=True, index=True)
    claimed_year = Column(Integer, nullable=True, index=True)

    # Harga & Filter Penipuan (DP Scam Filter)
    price = Column(Numeric(15, 2), nullable=False, index=True)
    is_dp_price = Column(Boolean, default=False, index=True)            # True jika harga hanya DP / Angsuran palsu

    # Atribut Spesifik Pasar Laptop Sekunder (Hasil Ekstraksi NLP)
    # 1. Asal Unit & Garansi
    warranty_type = Column(String(50), default="Resmi Indonesia")       # 'Resmi Indonesia (Asus ID/Lenovo ID/TAM/iBox)', 'Ex-Inter', 'Garansi Distributor'
    warranty_status = Column(String(50), default="Habis (Ex-Resmi)")    # 'Aktif (Masih Garansi Pabrik)', 'Habis (Ex-Resmi)', 'Garansi Toko 1 Bulan'
    
    # 2. Kondisi Baterai & Cycle Count
    battery_condition = Column(String(50), default="Normal Awet")       # 'Normal Awet', 'Normal Standar', 'Baterai Drop (Colok Terus)', 'Baterai Kembung'
    battery_health_pct = Column(Integer, nullable=True)                 # Persentase Battery Health aktual (40% - 100%)
    battery_cycle_count = Column(Integer, nullable=True)                # Jumlah siklus pengisian baterai (e.g. 85, 240, 650)
    
    # 3. Kelengkapan Unit
    completeness = Column(String(50), default="Unit + Charger Original")# 'Fullset Original (Dus+Charger Ori)', 'Unit + Charger Original', 'Charger OEM / Adaptor KW', 'Batangan / Unit Only'
    
    # 4. Kondisi Fisik Bodi & Engsel (Hinge)
    physical_grade = Column(String(50), default="Grade A (Mulus 95%)")   # 'Grade A+ (Like New 99%)', 'Grade A (Mulus 95%)', 'Grade B (Lecet Wajar)', 'Grade C (Dent/Baret)'
    hinge_condition = Column(String(50), default="Normal Kokoh")        # 'Normal Kokoh', 'Engsel Kendor / Patah'
    
    # 5. Kondisi Layar & Display Panel
    screen_condition = Column(String(50), default="Normal Jernih")      # 'Normal Jernih', 'Whitespot Tipis', 'Whitespot Tebal', 'Dead Pixel', 'Layar Bergaris / Flexgate'
    
    # 6. Fitur Hardware & Keamanan
    keyboard_condition = Column(String(50), default="Normal Aktif")     # 'Normal Aktif', 'Backlight Mati', 'Tombol Keyboard Minus/Macet'
    bios_mdm_status = Column(String(50), default="Clean")               # 'Clean (Bebas Password)', 'BIOS Locked / Computrace / MDM'

    # Lokasi & Profil Penjual
    province = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    seller_name = Column(String(150), nullable=True)
    seller_type = Column(String(50), default="Individual")              # 'Individual', 'Store / Toko Komputer'

    # Timestamps & Delta Tracking
    posted_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    price_drop_count = Column(Integer, default=0)
    status = Column(String(20), default="ACTIVE")                       # 'ACTIVE', 'PRICE_DROP', 'DELISTED'
    is_synthetic = Column(Boolean, default=False, nullable=False, index=True) # False = Data Riil Scraping, True = Dummy/Sintetis

    __table_args__ = (
        UniqueConstraint("source_platform", "external_id", name="uq_laptop_source_external_id"),
    )

    matched_variant = relationship("MasterVariant", back_populates="scraped_listings")
    price_history = relationship("ListingPriceHistory", back_populates="listing", cascade="all, delete-orphan")


class ListingPriceHistory(Base):
    """
    Riwayat Perubahan Harga Listing Laptop (Delta Tracking & Price Drop Signals).
    Mencatat pergerakan harga individual untuk mendeteksi unit diskon dan laju depresiasi.
    """
    __tablename__ = "listing_price_history"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("scraped_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    old_price = Column(Numeric(15, 2), nullable=False)
    new_price = Column(Numeric(15, 2), nullable=False)
    price_delta = Column(Numeric(15, 2), nullable=False)                # new_price - old_price (negatif = harga turun)
    price_delta_pct = Column(Numeric(6, 2), nullable=False)            # ((new_price - old_price) / old_price) * 100
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)

    listing = relationship("ScrapedListing", back_populates="price_history")


class MarketPriceStats(Base):
    """
    Agregasi Statistik Harga Pasar Laptop Harian (Tukey IQR, FMV, Kuartil P25/P75).
    """
    __tablename__ = "market_price_stats"

    id = Column(Integer, primary_key=True, index=True)
    stat_date = Column(Date, nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("master_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    city = Column(String(100), nullable=True, index=True)
    sample_count = Column(Integer, nullable=False, default=0)
    
    price_min = Column(Numeric(15, 2), nullable=False)
    price_p25 = Column(Numeric(15, 2), nullable=False)                  # Target Beli Murah (Bargain Hunter Target)
    price_median = Column(Numeric(15, 2), nullable=False)               # Fair Market Value (FMV Ekuilibrium)
    price_p75 = Column(Numeric(15, 2), nullable=False)                  # Unit Istimewa / Pristine Grade A+
    price_max = Column(Numeric(15, 2), nullable=False)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("stat_date", "variant_id", "city", name="uq_laptop_stat_date_variant_city"),
    )
