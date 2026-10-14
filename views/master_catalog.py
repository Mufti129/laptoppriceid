import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from models.catalog import MasterBrand, MasterModel, MasterVariant
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

        f_col1, f_col2, f_col3 = st.columns([1, 1, 1.2])
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
            search_query = st.text_input("Pencarian Model / CPU / GPU:", placeholder="Contoh: RTX 4060, ThinkPad, M3, Core Ultra...")

        f_col4, f_col5, f_col6 = st.columns([1.2, 1, 1])
        with f_col4:
            year_range = st.slider("Rentang Tahun Rilis:", min_value=2010, max_value=2026, value=(2010, 2026))

        with f_col5:
            gpu_filter = st.selectbox("Tipe Grafis (GPU):", ["Semua GPU", "Dedicated GPU (RTX / GTX / Radeon)", "Integrated iGPU (Iris / UHD)"])

        with f_col6:
            ram_filter = st.selectbox("Arsitektur RAM:", ["Semua RAM", "Dual SODIMM (Upgradeable)", "Soldered Onboard"])

        # 2. Build Query
        q = db.query(
            MasterModel,
            MasterBrand.name.label("brand_name"),
            MasterVariant.official_msrp_new,
            MasterVariant.ram_gb,
            MasterVariant.storage_gb
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
                <div class="pro-metric-label">Brand Terpilih</div>
                <div class="pro-metric-val">{selected_cat_brand}</div>
                <div class="pro-metric-sub rose">Filter Aktif</div>
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
                        m, b_name, msrp, ram, rom = item
                        img_url = m.image_url or get_product_image_url(b_name, m.series, m.name)
                        msrp_val = float(msrp) if msrp else 0
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
            for m, b_name, msrp, ram, rom in records:
                gpu_str = f"{m.gpu_model} ({m.vram_gb}GB, {m.tgp_watt}W)" if m.vram_gb > 0 else (m.gpu_model or "iGPU")
                ram_up = "Dual SODIMM" if m.is_ram_upgradeable else "Soldered"
                msrp_val = float(msrp) if msrp else 0

                table_data.append({
                    "Brand": b_name,
                    "Model": m.name,
                    "Series": m.series or "-",
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
                model_names_filtered = [m.name for m, _, _, _, _ in records[:60]]
                inspected_model_name = st.selectbox("Pilih Model untuk Dilihat Lengkap:", list(dict.fromkeys(model_names_filtered)))

                insp_m = next((m for m, _, _, _, _ in records if m.name == inspected_model_name), None)
                if insp_m:
                    insp_img = insp_m.image_url or get_product_image_url(selected_cat_brand, insp_m.series, insp_m.name)
                    c_insp_img, c_insp1, c_insp2 = st.columns([1, 1.2, 1.2])
                    with c_insp_img:
                        st.markdown(f"""
                        <div style="background:#0f172a; border:1px solid #334155; border-radius:12px; overflow:hidden; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.25);">
                            <img src="{insp_img}" alt="{insp_m.name}" style="width:100%; height:185px; object-fit:cover; display:block;" />
                            <div style="padding:10px 12px; background:#1e293b; border-top:1px solid #334155;">
                                <div style="font-weight:800; color:#f8fafc; font-size:0.95rem;">{insp_m.name}</div>
                                <div style="color:#60a5fa; font-size:0.78rem; margin-top:2px;">{insp_m.series or '-'} ({insp_m.release_year})</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_insp1:
                        st.markdown(f"""
                        **Informasi Arsitektur & Performa:**
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
        else:
            st.info("Tidak ada model laptop yang cocok dengan kriteria filter.")
    except Exception as e:
        st.error(f"Terjadi kesalahan pada modul Master Catalog Data: {e}")
