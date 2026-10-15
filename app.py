import os
import sys
import streamlit as st
from sqlalchemy.orm import Session

# Setup Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant, ScrapedListing
from data.master_catalog_seed import seed_master_catalog
import json
from scrapers.populate_real_data import ingest_real_listings

# Import Modular Views
from views import (
    render_market_overview,
    render_fmv_calculator,
    render_price_corridors,
    render_arbitrage_radar,
    render_spec_matrix,
    render_master_catalog,
    render_data_explorer,
)

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="LaptopPrice ID | Laptop Market Intelligence & Hedonic Valuation",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# EXECUTIVE DARK SLATE THEME (HIGH CONTRAST & RESPONSIVE PROPORTIONS)
# ==============================================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
    /* Global Typography & Canvas */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }

    /* Executive Hero Header */
    .hero-appbar {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.025em;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        max-width: 900px;
        line-height: 1.5;
    }
    .hero-tags {
        display: flex;
        gap: 8px;
        margin-top: 14px;
        flex-wrap: wrap;
    }
    .hero-tag-pill {
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #60a5fa;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 3px 10px;
        border-radius: 20px;
    }

    /* KPI Metrics Cards Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .pro-metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    }
    .pro-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
    }
    .pro-metric-card.emerald::before {
        background: linear-gradient(90deg, #10b981, #34d399);
    }
    .pro-metric-card.rose::before {
        background: linear-gradient(90deg, #ef4444, #f87171);
    }
    .pro-metric-card.purple::before {
        background: linear-gradient(90deg, #8b5cf6, #c084fc);
    }
    .pro-metric-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .pro-metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
    }
    .pro-metric-sub {
        font-size: 0.76rem;
        color: #60a5fa;
        margin-top: 5px;
        font-weight: 600;
    }
    .pro-metric-sub.emerald {
        color: #34d399;
    }
    .pro-metric-sub.rose {
        color: #f87171;
    }
    .pro-metric-sub.purple {
        color: #c084fc;
    }

    /* Structured Information Callout Boxes */
    .info-box-blue {
        background: rgba(59, 130, 246, 0.10);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-left: 4px solid #3b82f6;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 18px;
        color: #e2e8f0;
    }
    .info-box-green {
        background: rgba(16, 185, 129, 0.10);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-left: 4px solid #10b981;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 18px;
        color: #e2e8f0;
    }
    .info-box-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .info-box-desc {
        font-size: 0.84rem;
        line-height: 1.5;
        color: #cbd5e1;
    }

    /* Specification Card */
    .spec-card-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 22px;
        color: #f8fafc;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
        height: 100%;
        box-sizing: border-box;
    }
    .spec-card-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #60a5fa;
        border-bottom: 1px solid #334155;
        padding-bottom: 10px;
        margin-bottom: 14px;
        letter-spacing: -0.01em;
    }
    .spec-item {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid rgba(51, 65, 85, 0.4);
        font-size: 0.85rem;
    }
    .spec-item-key {
        color: #94a3b8;
    }
    .spec-item-val {
        font-weight: 600;
        color: #f1f5f9;
        text-align: right;
    }

    /* Valuation Hero Output Card */
    .val-hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #38bdf8;
        border-radius: 14px;
        padding: 22px 26px;
        margin-top: 18px;
        margin-bottom: 18px;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.15);
        text-align: center;
    }
    .val-hero-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .val-hero-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.3rem;
        font-weight: 800;
        color: #38bdf8;
        line-height: 1.15;
        margin: 8px 0;
    }
    .val-hero-meta {
        font-size: 0.84rem;
        color: #cbd5e1;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #1e293b;
    }
    .sidebar-brand-box {
        padding: 6px 0 14px 0;
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .sidebar-desc {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 4px;
        line-height: 1.4;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        font-size: 0.70rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 3px 10px;
        border-radius: 20px;
        margin-top: 8px;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        background: #10b981;
        border-radius: 50%;
    }

    /* Product Images & Cards */
    .laptop-img-hero {
        width: 100%;
        height: 190px;
        object-fit: cover;
        border-radius: 10px;
        display: block;
        border: 1px solid #334155;
        background: #0f172a;
    }
    .laptop-card-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .laptop-card-box:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    .laptop-card-img {
        width: 100%;
        height: 140px;
        object-fit: cover;
        display: block;
        border-bottom: 1px solid #334155;
    }
    .laptop-card-content {
        padding: 12px 14px;
    }
    .laptop-card-title {
        font-weight: 700;
        color: #f8fafc;
        font-size: 0.90rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .laptop-card-meta {
        font-size: 0.76rem;
        color: #94a3b8;
        margin-top: 3px;
        margin-bottom: 8px;
    }
    .laptop-card-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        font-weight: 800;
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATABASE LIFECYCLE & CACHING
# ==============================================================================
@st.cache_resource(show_spinner="Inisialisasi Database & Master Katalog Laptop...")
def ensure_database_ready():
    """Memastikan database terinisialisasi dan terisi katalog komprehensif laptop serta data riil."""
    init_db()
    db = SessionLocal()
    try:
        if db.query(MasterVariant).count() == 0:
            seed_master_catalog()

        if db.query(ScrapedListing).count() == 0:
            cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "real_listings_cache.json")
            if os.path.exists(cache_path):
                print(f"[INIT] Memulihkan database dengan 100% data riil dari {cache_path}...")
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                ingest_real_listings(cached_data, purge_old=False)
            else:
                print("[INFO] Database listing kosong. Jalankan scraper live (python scrapers/daemon.py --run-once) untuk mengambil data riil marketplace.")
    except Exception as e:
        print(f"[WARN] Error on DB init: {e}")
    finally:
        db.close()
    return True

# Ensure DB is warmed up
ensure_database_ready()

def get_db():
    return SessionLocal()

# ==============================================================================
# SIDEBAR NAVIGATION & URL QUERY PARAMS SYNCHRONIZATION
# ==============================================================================
st.sidebar.markdown("""
<div class="sidebar-brand-box">
    <div class="sidebar-title">LaptopPrice ID</div>
    <div class="sidebar-desc">Laptop Market Intelligence & Hedonic Valuation Platform</div>
    <div class="status-pill">
        <span class="status-dot"></span>
        Enterprise Active
    </div>
</div>
""", unsafe_allow_html=True)

MENU_SLUG_MAP = {
    "Market Overview & Dashboard": "overview",
    "FMV & Hedonic Calculator": "fmv",
    "3-Tier Price Corridors & Quantiles": "corridors",
    "Arbitrage & Hot Deals Radar": "arbitrage",
    "Spec Matrix & Model Comparison": "compare",
    "Master Catalog Data": "catalog",
    "Data Explorer & Scam Filter": "explorer"
}
SLUG_MENU_MAP = {v: k for k, v in MENU_SLUG_MAP.items()}
menu_options = list(MENU_SLUG_MAP.keys())

# Read URL query params for direct sharing
default_index = 0
current_slug = st.query_params.get("menu")
if current_slug and current_slug in SLUG_MENU_MAP:
    default_index = menu_options.index(SLUG_MENU_MAP[current_slug])

menu = st.sidebar.radio(
    "PILIH MODUL ANALISIS:",
    menu_options,
    index=default_index
)

# Keep URL parameter synchronized
st.query_params["menu"] = MENU_SLUG_MAP[menu]

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size:0.75rem; color:#64748b; line-height:1.6;">
    <b>STATUS SISTEM:</b><br>
    • Database: <span style="color:#34d399;">🟢 Online (SQLite)</span><br>
    • Master Model: <b>1.000 Unit (10 Brand)</b><br>
    • Snapshot Listing: <b>15.000 Terverifikasi</b><br>
    • Cakupan Wilayah: <b>13 Kota Indonesia</b><br>
    • Engine: <b>Lancaster-Rosen Hedonic</b>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# DISPATCH CONTROLLER TO MODULAR VIEWS
# ==============================================================================
with get_db() as db:
    if menu == "Market Overview & Dashboard":
        render_market_overview(db)
    elif menu == "FMV & Hedonic Calculator":
        render_fmv_calculator(db)
    elif menu == "3-Tier Price Corridors & Quantiles":
        render_price_corridors(db)
    elif menu == "Arbitrage & Hot Deals Radar":
        render_arbitrage_radar(db)
    elif menu == "Spec Matrix & Model Comparison":
        render_spec_matrix(db)
    elif menu == "Master Catalog Data":
        render_master_catalog(db)
    elif menu == "Data Explorer & Scam Filter":
        render_data_explorer(db)
