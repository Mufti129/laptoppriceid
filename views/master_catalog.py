import re
import urllib.parse
import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from models.catalog import MasterBrand, MasterModel, MasterVariant, ScrapedListing
from data.image_catalog import get_product_image_url

def render_master_catalog(db: Session):
    """Render modul Master Catalog Data (2010 - 2026)."""
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Master Hardware Catalog Explorer (2010 - 2026)</div>
        <div class="hero-subtitle">
            Eksplorasi komprehensif master database spesifikasi teknis hardware laptop: 1.000 model terverifikasi (100 model per brand) mencakup prosesor CPU, grafis GPU, memori RAM, display panel, baterai, dan MSRP peluncuran resmi Indonesia.
        </div>
        <div class="hero-tags">
            <span class="hero-tag-pill">1.000 Model Terdaftar</span>
            <span class="hero-tag-pill">10 Brand Utama</span>
            <span class="hero-tag-pill">2010 - 2026 Archive</span>
            <span class="hero-tag-pill">Filter & Export Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        # 1. Filter Bar
        all_brands = [b.name for b in db.query(MasterBrand).order_by(MasterBrand.name).all()]
        brand_filter_options = ["Semua Brand"] + all_brands

        f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 1, 1.2])
        with f_col1:
            selected_cat_brand = st.selectbox("Filter Brand Laptop:", brand_filter_options, index=0)

        # Query series options based on brand
        series_query = db.query(MasterModel.series).distinct()
        if selected_cat_brand != "Semua Brand":
            brand_id = db.query(MasterBrand.id).filter(MasterBrand.name == selected_cat_brand).scalar()
            if brand_id:
                series_query = series_query.filter(MasterModel.brand_id == brand_id)

        all_series = sorted([s[0] for s in series_query.all() if s[0]])
        series_filter_options = ["Semua Series"] + all_series

        with f_col2:
            selected_cat_series = st.selectbox("Filter Series / Lini:", series_filter_options, index=0)

        with f_col3:
            selected_platform = st.selectbox(
                "Filter Platfrom:",
                ["Semua Platfrom", "Pemmz.com", "Tokopedia", "Carousell ID", "iBox ID"],
                index=0
            )

        with f_col4:
            search_query = st.text_input("Pencarian Model / CPU / GPU:", placeholder="Contoh: RTX 4060, ThinkPad, M3, Core Ultra...")

        f_col5, f_col6, f_col7 = st.columns([1.2, 1, 1])
        with f_col5:
            year_range = st.slider("Rentang Tahun Rilis:", min_value=2010, max_value=2026, value=(2010, 2026))

        with f_col6:
            gpu_filter = st.selectbox("Tipe Grafis (GPU):", ["Semua GPU", "Dedicated GPU (RTX / GTX / Radeon)", "Integrated iGPU (Iris / UHD)"])

        with f_col7:
            ram_filter = st.selectbox("Arsitektur RAM:", ["Semua RAM", "Dual SODIMM (Upgradeable)", "Soldered Onboard"])

        # 2. Build Query & Platform Resolution
        # Mapping sumber platform riil dari live scraping di database
        scraped_platforms = db.query(
            ScrapedListing.matched_variant_id,
            ScrapedListing.source_platform
        ).filter(
            ScrapedListing.matched_variant_id.isnot(None)
        ).distinct().all()

        variant_platforms_map = {}
        for vid, plat in scraped_platforms:
            variant_platforms_map.setdefault(vid, set()).add(plat)

        def get_model_platform(brand_name, series_name, model_name, variant_id):
            active_scraped = variant_platforms_map.get(variant_id, set())
            sources = []

            # 1. Platform hasil live scraping yang aktif di database
            if "carousell" in active_scraped:
                sources.append("Carousell ID")
            if "tokopedia" in active_scraped:
                sources.append("Tokopedia")
            if "pemmz" in active_scraped:
                sources.append("Pemmz.com")

            # 2. Sumber rujukan spesifikasi teknis hardware & baseline MSRP resmi
            s_upper = (series_name or "").upper()
            m_upper = (model_name or "").upper()
            b_upper = (brand_name or "").upper()

            is_gaming = any(k in s_upper or k in m_upper for k in [
                "ROG", "TUF", "LEGION", "LOQ", "PREDATOR", "NITRO", "OMEN", "VICTUS", "ALIENWARE", "GAMING", "PONGO"
            ]) or b_upper == "MSI"
            is_apple = (b_upper == "APPLE" or "MACBOOK" in m_upper)

            if is_gaming:
                base_source = "Pemmz.com"
            elif is_apple:
                base_source = "iBox ID"
            else:
                base_source = "Tokopedia"

            if base_source not in sources:
                sources.append(base_source)

            return " & ".join(sources)

        def generate_audit_search_keyword(brand_name, series_name, model_name, processor_model="", gpu_model="", vram_gb=0.0, ram=None, rom=None, platform="", chassis_code=""):
            """Menghasilkan kata kunci pencarian audit persis untuk dicocokkan 1-to-1 di website sumber."""
            b_name = (brand_name or "").strip()
            m_name = (model_name or "").strip()
            c_code = (chassis_code or "").strip()

            if m_name.lower().startswith(b_name.lower()):
                base_name = m_name
            else:
                base_name = f"{b_name} {m_name}".strip()

            # Ekstraksi GPU singkat
            gpu_clean = ""
            if gpu_model and vram_gb and vram_gb > 0:
                match_rtx = re.search(r'(RTX\s*\d{4}(?:\s*Ti)?|GTX\s*\d{4}(?:\s*Ti)?|Radeon\s*RX\s*\d{4}\w*)', gpu_model, re.IGNORECASE)
                if match_rtx:
                    gpu_clean = match_rtx.group(1).upper()
                else:
                    gpu_clean = gpu_model.replace("Laptop GPU", "").replace("NVIDIA GeForce", "").strip()

            # Ekstraksi CPU tier singkat
            cpu_clean = ""
            if processor_model:
                match_apple = re.search(r'(M[1234](?:\s*(?:Pro|Max|Ultra))?)', processor_model, re.IGNORECASE)
                match_intel = re.search(r'(Core\s*Ultra\s*\d|Core\s*i[3579]|i[3579]-\d{4,5}\w*)', processor_model, re.IGNORECASE)
                match_ryzen = re.search(r'(Ryzen\s*[3579]|Ryzen\s*AI\s*\d)', processor_model, re.IGNORECASE)
                if match_apple:
                    cpu_clean = match_apple.group(1)
                elif match_intel:
                    cpu_clean = match_intel.group(1)
                elif match_ryzen:
                    cpu_clean = match_ryzen.group(1)

            plat_lower = platform.lower()

            # 1. iBox ID / Apple
            if "ibox" in plat_lower or b_name.lower() == "apple":
                parts = [base_name]
                if c_code and c_code.lower() not in base_name.lower():
                    parts.append(c_code)
                if cpu_clean and cpu_clean.lower() not in base_name.lower():
                    parts.append(cpu_clean)
                if ram:
                    parts.append(f"{ram}GB")
                if rom:
                    parts.append(f"{rom}GB")
                return " ".join(parts).strip()

            # 2. Pemmz.com / Gaming
            if "pemmz" in plat_lower or (gpu_clean and any(k in plat_lower for k in ["gaming", "pemmz"])):
                parts = [base_name]
                if c_code and c_code.lower() not in base_name.lower():
                    parts.append(c_code)
                if gpu_clean and gpu_clean.lower() not in base_name.lower():
                    parts.append(gpu_clean)
                elif cpu_clean and cpu_clean.lower() not in base_name.lower():
                    parts.append(cpu_clean)
                return " ".join(parts).strip()

            # 3. Tokopedia / Carousell / Mainstream & Business
            parts = [base_name]
            if c_code and c_code.lower() not in base_name.lower() and not c_code.startswith(f"{b_name}-"):
                parts.append(c_code)
            if cpu_clean and cpu_clean.lower() not in base_name.lower():
                parts.append(cpu_clean)
            elif gpu_clean and gpu_clean.lower() not in base_name.lower():
                parts.append(gpu_clean)
            return " ".join(parts).strip()

        def get_audit_search_url(platform_str, keyword):
            """Menghasilkan tautan URL pencarian audit langsung ke website sumber live."""
            encoded_kw = urllib.parse.quote_plus(keyword)
            plat_lower = platform_str.lower()
            if "pemmz" in plat_lower:
                return f"https://pemmz.com/catalogsearch/result/?q={encoded_kw}"
            elif "ibox" in plat_lower:
                return f"https://ibox.co.id/catalogsearch/result/?q={encoded_kw}"
            elif "carousell" in plat_lower:
                return f"https://id.carousell.com/search/{encoded_kw}"
            else:
                return f"https://www.tokopedia.com/search?st=product&q={encoded_kw}"

        q = db.query(
            MasterModel,
            MasterBrand.name.label("brand_name"),
            MasterVariant.official_msrp_new,
            MasterVariant.ram_gb,
            MasterVariant.storage_gb,
            MasterVariant.id.label("variant_id")
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).outerjoin(
            MasterVariant, MasterVariant.model_id == MasterModel.id
        )

        if selected_cat_brand != "Semua Brand":
            q = q.filter(MasterBrand.name == selected_cat_brand)

        if selected_cat_series != "Semua Series":
            q = q.filter(MasterModel.series == selected_cat_series)

        q = q.filter(MasterModel.release_year.between(year_range[0], year_range[1]))

        if gpu_filter == "Dedicated GPU (RTX / GTX / Radeon)":
            q = q.filter(MasterModel.vram_gb > 0)
        elif gpu_filter == "Integrated iGPU (Iris / UHD)":
            q = q.filter(MasterModel.vram_gb == 0)

        if ram_filter == "Dual SODIMM (Upgradeable)":
            q = q.filter(MasterModel.is_ram_upgradeable == True)
        elif ram_filter == "Soldered Onboard":
            q = q.filter(MasterModel.is_ram_upgradeable == False)

        if search_query:
            term = f"%{search_query.strip().lower()}%"
            q = q.filter(
                MasterModel.name.ilike(term) |
                MasterModel.processor_model.ilike(term) |
                MasterModel.gpu_model.ilike(term) |
                MasterModel.series.ilike(term)
            )

        records = q.order_by(MasterModel.release_year.desc(), MasterBrand.name, MasterModel.name).all()

        # Filter berdasarkan Platfrom jika dipilih
        if selected_platform != "Semua Platfrom":
            records = [
                r for r in records
                if selected_platform.lower() in get_model_platform(r[1], r[0].series, r[0].name, r[5]).lower()
            ]

        # 3. Metrik & KPI
        total_filtered = len(records)
        unique_models = len(set(r[0].id for r in records))
        avg_msrp = np.mean([float(r[2]) for r in records if r[2]]) if records else 0

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="pro-metric-card">
                <div class="pro-metric-label">Model Terfilter</div>
                <div class="pro-metric-val">{unique_models} Model</div>
                <div class="pro-metric-sub">{total_filtered} Varian Terdaftar</div>
            </div>
            <div class="pro-metric-card emerald">
                <div class="pro-metric-label">Rentang Tahun</div>
                <div class="pro-metric-val">{year_range[0]} - {year_range[1]}</div>
                <div class="pro-metric-sub emerald">Historis Terverifikasi</div>
            </div>
            <div class="pro-metric-card purple">
                <div class="pro-metric-label">Rata-Rata MSRP Baru</div>
                <div class="pro-metric-val">Rp {avg_msrp:,.0f}</div>
                <div class="pro-metric-sub purple">Nilai Retail Peluncuran</div>
            </div>
            <div class="pro-metric-card rose">
                <div class="pro-metric-label">Brand & Platfrom</div>
                <div class="pro-metric-val">{selected_cat_brand}</div>
                <div class="pro-metric-sub rose">{selected_platform}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. Format Data Table & Visual Gallery
        if records:
            view_mode = st.radio("Format Tampilan Katalog:", ["Tabel Data Lengkap", "Galeri Kartu Produk Visual"], horizontal=True)

            if view_mode == "Galeri Kartu Produk Visual":
                st.markdown("#### 📸 Galeri Visual Produk Laptop")
                sample_records = records[:24]  # showcase top 24 filtered products
                cols_per_row = 4
                for row_idx in range(0, len(sample_records), cols_per_row):
                    row_items = sample_records[row_idx:row_idx+cols_per_row]
                    cols = st.columns(cols_per_row)
                    for col_idx, item in enumerate(row_items):
                        m, b_name, msrp, ram, rom, vid = item
                        img_url = m.image_url or get_product_image_url(b_name, m.series, m.name)
                        msrp_val = float(msrp) if msrp else 0
                        plat_val = get_model_platform(b_name, m.series, m.name, vid)
                        audit_kw = generate_audit_search_keyword(b_name, m.series, m.name, m.processor_model, m.gpu_model, m.vram_gb, ram, rom, plat_val, m.chassis_code)
                        audit_url = get_audit_search_url(plat_val, audit_kw)
                        with cols[col_idx]:
                            st.markdown(f"""
                            <div class="laptop-card-box">
                                <div style="position:relative;">
                                    <img class="laptop-card-img" src="{img_url}" alt="{m.name}" />
                                    <div style="position:absolute; top:8px; right:8px; background:rgba(15,23,42,0.85); color:#60a5fa; font-size:0.70rem; font-weight:700; padding:2px 7px; border-radius:6px; border:1px solid #334155;">
                                        {m.release_year}
                                    </div>
                                </div>
                                <div class="laptop-card-content">
                                    <div class="laptop-card-title">{b_name} {m.name}</div>
                                    <div class="laptop-card-meta">{m.series or '-'}</div>
                                    <div style="font-size:0.72rem; color:#38bdf8; font-weight:600; margin-bottom:1px;">
                                        🌐 Platfrom: {plat_val}
                                    </div>
                                    <div style="font-size:0.70rem; color:#10b981; font-weight:700; margin-bottom:2px;">
                                        🏷️ Sasis/SKU: <code>{m.chassis_code or '-'}</code>
                                    </div>
                                    <div style="font-size:0.70rem; color:#a78bfa; margin-bottom:4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                                        🔍 Audit: <a href="{audit_url}" target="_blank" style="color:#c084fc; text-decoration:underline;">{audit_kw}</a>
                                    </div>
                                    <div style="font-size:0.75rem; color:#cbd5e1; margin-bottom:6px;">
                                        ⚙️ {m.processor_model or '-'}<br>
                                        🎮 {m.gpu_model or 'iGPU'}
                                    </div>
                                    <div style="border-top:1px solid #334155; padding-top:6px; display:flex; justify-content:space-between; align-items:center;">
                                        <span style="font-size:0.72rem; color:#94a3b8;">{ram or '-'}GB / {rom or '-'}GB</span>
                                        <span class="laptop-card-price">{'Rp ' + f'{msrp_val:,.0f}' if msrp_val > 0 else '-'}</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                if len(records) > 24:
                    st.caption(f"Menampilkan 24 dari {len(records)} produk terfilter. Pilih 'Tabel Data Lengkap' untuk melihat dan mengunduh seluruh baris.")

            table_data = []
            for m, b_name, msrp, ram, rom, vid in records:
                gpu_str = f"{m.gpu_model} ({m.vram_gb}GB, {m.tgp_watt}W)" if m.vram_gb > 0 else (m.gpu_model or "iGPU")
                ram_up = "Dual SODIMM" if m.is_ram_upgradeable else "Soldered"
                msrp_val = float(msrp) if msrp else 0
                plat_val = get_model_platform(b_name, m.series, m.name, vid)
                audit_kw = generate_audit_search_keyword(b_name, m.series, m.name, m.processor_model, m.gpu_model, m.vram_gb, ram, rom, plat_val, m.chassis_code)

                table_data.append({
                    "Brand": b_name,
                    "Model": m.name,
                    "Kode Sasis / SKU": m.chassis_code or "-",
                    "Series": m.series or "-",
                    "Platfrom": plat_val,
                    "Kata Kunci Audit": audit_kw,
                    "Tahun": m.release_year,
                    "Prosesor (CPU)": m.processor_model or "-",
                    "Cinebench R23": f"{m.cinebench_score:,} pts" if m.cinebench_score else "-",
                    "Kartu Grafis (GPU)": gpu_str,
                    "Display Panel": f"{m.display_type} ({m.screen_size_inch}\", {m.resolution})",
                    "Refresh Rate": f"{m.refresh_rate_hz} Hz",
                    "RAM Bawaan": f"{ram} GB" if ram else "-",
                    "Tipe RAM": f"{m.ram_type or '-'} ({ram_up})",
                    "Storage SSD": f"{rom} GB" if rom else "-",
                    "Baterai": f"{m.battery_wh} Wh" if m.battery_wh else "-",
                    "Bobot": f"{m.weight_kg} kg" if m.weight_kg else "-",
                    "MSRP Baru (IDR)": f"Rp {msrp_val:,.0f}" if msrp_val > 0 else "-"
                })

            df_catalog = pd.DataFrame(table_data)
            if view_mode == "Tabel Data Lengkap":
                st.dataframe(df_catalog, use_container_width=True, hide_index=True)

            # Export CSV
            csv_data = df_catalog.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Unduh Data Master Katalog (CSV)",
                data=csv_data,
                file_name=f"master_katalog_laptop_{selected_cat_brand.lower().replace(' ', '_')}.csv",
                mime="text/csv",
            )

            # 5. Detail Inspector
            with st.expander("Inspeksi Rinci Spesifikasi Hardware Model"):
                model_names_filtered = [m.name for m, _, _, _, _, _ in records[:60]]
                inspected_model_name = st.selectbox("Pilih Model untuk Dilihat Lengkap:", list(dict.fromkeys(model_names_filtered)))

                insp_entry = next(((m, b, msrp, ram, rom, vid) for m, b, msrp, ram, rom, vid in records if m.name == inspected_model_name), None)
                if insp_entry:
                    insp_m, insp_b, _, _, _, insp_vid = insp_entry
                    insp_img = insp_m.image_url or get_product_image_url(insp_b, insp_m.series, insp_m.name)
                    insp_plat = get_model_platform(insp_b, insp_m.series, insp_m.name, insp_vid)
                    insp_audit_kw = generate_audit_search_keyword(
                        insp_b, insp_m.series, insp_m.name, insp_m.processor_model, insp_m.gpu_model, insp_m.vram_gb, None, None, insp_plat, insp_m.chassis_code
                    )
                    insp_audit_url = get_audit_search_url(insp_plat, insp_audit_kw)

                    c_insp_img, c_insp1, c_insp2 = st.columns([1, 1.2, 1.2])
                    with c_insp_img:
                        st.markdown(f"""
                        <div style="background:#0f172a; border:1px solid #334155; border-radius:12px; overflow:hidden; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.25);">
                            <img src="{insp_img}" alt="{insp_m.name}" style="width:100%; height:185px; object-fit:cover; display:block;" />
                            <div style="padding:10px 12px; background:#1e293b; border-top:1px solid #334155;">
                                <div style="font-weight:800; color:#f8fafc; font-size:0.95rem;">{insp_m.name}</div>
                                <div style="color:#60a5fa; font-size:0.78rem; margin-top:2px;">{insp_m.series or '-'} ({insp_m.release_year})</div>
                                <div style="color:#38bdf8; font-size:0.75rem; margin-top:4px;">🌐 Platfrom: {insp_plat}</div>
                                <div style="color:#10b981; font-size:0.75rem; font-weight:700; margin-top:2px;">🏷️ Kode Sasis: {insp_m.chassis_code or '-'}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_insp1:
                        st.markdown(f"""
                        **Informasi Arsitektur & Performa:**
                        - **Platfrom / Sumber Data:** `{insp_plat}`
                        - **Kode Sasis / Part Number SKU:** `{insp_m.chassis_code or '-'}`
                        - **Kata Kunci Audit Lapangan:** `{insp_audit_kw}`
                        - **Verifikasi Website:** [🔍 Buka Pencarian di Website Langsung ↗]({insp_audit_url})
                        - **Prosesor:** {insp_m.processor_model} ({insp_m.processor_brand})
                        - **Arsitektur CPU:** {insp_m.cpu_architecture} ({insp_m.cpu_cores} Cores / {insp_m.cpu_threads} Threads)
                        - **Cinebench R23 Multi-Core:** {f"{insp_m.cinebench_score:,} pts" if insp_m.cinebench_score else "N/A"}
                        - **GPU:** {insp_m.gpu_model} ({insp_m.vram_gb} GB VRAM, {insp_m.tgp_watt} Watt TGP)
                        - **Display:** {insp_m.display_type} {insp_m.screen_size_inch}" {insp_m.resolution} @ {insp_m.refresh_rate_hz}Hz ({insp_m.color_gamut or '-'})
                        """)
                    with c_insp2:
                        st.markdown(f"""
                        **Memory, Portabilitas & Sasis:**
                        - **RAM:** {insp_m.ram_type} ({'Slot Dual SODIMM Upgradeable' if insp_m.is_ram_upgradeable else 'Soldered Onboard Non-Upgradeable'})
                        - **Storage:** {insp_m.storage_interface} ({insp_m.storage_slots} slot M.2)
                        - **Baterai & Daya:** {insp_m.battery_wh} Wh (Adaptor {insp_m.charger_watt} Watt)
                        - **Bobot & Material:** {insp_m.weight_kg} kg ({insp_m.chassis_material or '-'})
                        - **Sistem Operasi Rilis:** {insp_m.os_at_launch}
                        """)

            # 6. Panduan Audit & Random Check Tim Lapangan
            with st.expander("📋 Panduan Audit & Random Check Tim Lapangan (Kata Kunci Pencarian & URL Langsung)", expanded=False):
                st.markdown("""
                ### 🎯 Metodologi Audit 1-to-1 untuk Tim Lapangan
                Untuk memastikan integritas data **100% data riil** tanpa data sintetis atau estimasi fiktif, tim lapangan dapat melakukan pengecekan acak (*random check*) menggunakan acuan kata kunci berikut:

                | Sumber Platfrom | Kategori Hardware Utama | Format Kata Kunci Audit (*Exact Search Query*) | Endpoint Pencarian Live |
                | :--- | :--- | :--- | :--- |
                | **Pemmz.com** | Gaming & Workstation High-Performance (ASUS ROG/TUF, Lenovo Legion/LOQ, Acer Predator/Nitro, MSI, HP Omen/Victus, Alienware, Pongo) | `[Brand] [Model] [Kode Sasis] [GPU]` <br>*(Contoh: `Lenovo Legion Pro 5 16IRX8 RTX 4070`, `ASUS ROG Strix G16 G614JV RTX 4060`)* | `https://pemmz.com/catalogsearch/result/?q={keyword}` |
                | **Tokopedia** | Business, Ultrabook, Mainstream & Productivity (ThinkPad, XPS, Zenbook, Swift, EliteBook, MateBook, Surface) | `[Brand] [Model] [Kode Sasis] [CPU Tier]` <br>*(Contoh: `Lenovo ThinkPad T14 Gen 4 21HD Core i5`, `Dell XPS 13 9320 Core i7`)* | `https://www.tokopedia.com/search?st=product&q={keyword}` |
                | **iBox ID** | Apple MacBook Series (MacBook Pro & MacBook Air lini chip M1/M2/M3/M4 & Intel) | `[Model] [Kode A-Series] [RAM]GB [Storage]GB` <br>*(Contoh: `MacBook Air 13 M2 A2681 8GB 256GB`, `MacBook Pro 14 M3 A2992 16GB 512GB`)* | `https://ibox.co.id/catalogsearch/result/?q={keyword}` |
                | **Carousell ID** | Pasar Sekunder C2C Indonesia (4.036 listing aktif terindeks) | `[Model/Brand] [Keyword]` <br>*(Contoh: `ThinkPad T480 i5`, `MacBook Air M1`)* | `https://id.carousell.com/search/{keyword}` |

                #### 🏷️ Rumus Singkat Membaca Kode Sasis / SKU Pabrikan (Cheat Sheet):
                - **ASUS ROG/TUF:** Huruf paling belakang menentukan GPU: `JU` = RTX 4050, `JV` = RTX 4060, `JVR` = RTX 4060 (Refresh Gen 14), `JIR` = RTX 4070, `JZR` = RTX 4080.
                - **Lenovo Legion:** Format `16IRX8` (`16` = 16", `I` = Intel, `R` = Raptor Lake, `X` = Discrete RTX, `8` = Gen 8).
                - **Acer Predator/Nitro:** `PHN16-71` (Helios Neo 16 Gen 13), `AN515-58` (Nitro 5).
                - **MSI Katana/Cyborg:** `B13VFK` (`13` = Gen 13, `V` = RTX 40, `E` = 4050, `F` = 4060, `G` = 4070, `H` = 4080).
                - **Apple MacBook:** Model Number A-Series (`A2681` = Air 13 M2, `A2941` = Air 15 M2, `A2992` = Pro 14 M3 Pro, `A2337` = Air 13 M1).
                """)
        else:
            st.info("Tidak ada model laptop yang cocok dengan kriteria filter.")
    except Exception as e:
        st.error(f"Terjadi kesalahan pada modul Master Catalog Data: {e}")
