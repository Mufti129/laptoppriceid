import streamlit as st
from sqlalchemy.orm import Session
from models.catalog import MasterBrand, MasterModel, MasterVariant
from analytics.pricing_engine import LaptopPricingEngine
from analytics.depreciation_engine import LaptopDepreciationEngine
from data.image_catalog import get_product_image_url

def render_fmv_calculator(db: Session):
    """Render modul Fair Market Value & Hedonic Calculator."""
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Fair Market Value & Hedonic Calculator</div>
        <div class="hero-subtitle">
            Kalkulator valuasi presisi tinggi dengan penyesuaian hedonik kualitas laptop: kesehatan baterai (cycle count/drop), kondisi layar (whitespot/dead pixel), engsel bodi, kelengkapan charger, dan status BIOS lock.
        </div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Hedonic Quality Adjustment</span>
            <span class="hero-tag-pill">Battery Cycle & Health Depr</span>
            <span class="hero-tag-pill">Display Whitespot Penalty</span>
            <span class="hero-tag-pill">Hinge & Chassis Evaluation</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        brands = [b.name for b in db.query(MasterBrand).order_by(MasterBrand.name).all()]
        if not brands:
            st.warning("Database master katalog masih kosong. Silakan jalankan seeder terlebih dahulu.")
            return

        col_select1, col_select2, col_select3 = st.columns(3)

        with col_select1:
            selected_brand = st.selectbox("Pilih Brand Laptop:", brands, index=0)

        brand_obj = db.query(MasterBrand).filter(MasterBrand.name == selected_brand).first()
        models = db.query(MasterModel).filter(MasterModel.brand_id == brand_obj.id).order_by(MasterModel.release_year.desc(), MasterModel.name).all() if brand_obj else []

        model_names = [m.name for m in models]
        with col_select2:
            selected_model_name = st.selectbox("Pilih Model Laptop:", model_names if model_names else ["-"])

        model_obj = next((m for m in models if m.name == selected_model_name), None)

        if model_obj:
            variants = db.query(MasterVariant).filter(MasterVariant.model_id == model_obj.id).all()
            variant_dict = {f"{v.variant_name} ({v.ram_gb}GB / {v.storage_gb}GB)": v for v in variants}

            with col_select3:
                selected_variant_name = st.selectbox("Pilih Varian RAM/Storage:", list(variant_dict.keys()) if variant_dict else ["-"])

            st.markdown("---")

            selected_var_obj = variant_dict.get(selected_variant_name)

            if selected_var_obj and model_obj:
                col_specs, col_inputs = st.columns([1.1, 1.9])

                with col_specs:
                    gpu_str = f"{model_obj.gpu_model} ({model_obj.vram_gb}GB, {model_obj.tgp_watt}W)" if model_obj.vram_gb > 0 else (model_obj.gpu_model or "Integrated iGPU")
                    ram_up_str = "Dual SODIMM (Upgradeable)" if model_obj.is_ram_upgradeable else "Soldered Onboard (Non-Upgradeable)"
                    img_url = model_obj.image_url or get_product_image_url(selected_brand, model_obj.series, model_obj.name)

                    st.markdown(f"""
                    <div style="border-radius:12px; overflow:hidden; border:1px solid #334155; margin-bottom:14px; background:#0f172a; box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                        <img src="{img_url}" alt="{selected_brand} {model_obj.name}" style="width:100%; height:195px; object-fit:cover; display:block;" />
                        <div style="padding:8px 12px; background:rgba(30,41,59,0.9); font-size:0.78rem; color:#94a3b8; font-weight:600; display:flex; justify-content:space-between; align-items:center;">
                            <span>💻 {selected_brand} {model_obj.series or ''}</span>
                            <span style="color:#60a5fa; background:rgba(59,130,246,0.15); padding:2px 8px; border-radius:12px; border:1px solid rgba(59,130,246,0.3);">Rilis {model_obj.release_year}</span>
                        </div>
                    </div>
                    <div class="spec-card-container">
                        <div class="spec-card-header">Spesifikasi Bawaan Pabrik</div>
                        <div class="spec-item">
                            <span class="spec-item-key">Merk & Model</span>
                            <span class="spec-item-val">{selected_brand} {model_obj.name}</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">Tahun Peluncuran</span>
                            <span class="spec-item-val">{model_obj.release_year}</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">MSRP Baru</span>
                            <span class="spec-item-val" style="color:#60a5fa;">Rp {float(selected_var_obj.official_msrp_new):,.0f}</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">Prosesor / CPU</span>
                            <span class="spec-item-val">{model_obj.processor_model or '-'}</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">Kartu Grafis (GPU)</span>
                            <span class="spec-item-val">{gpu_str}</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">Kapasitas RAM / SSD</span>
                            <span class="spec-item-val">{selected_var_obj.ram_gb} GB / {selected_var_obj.storage_gb} GB</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">Arsitektur RAM</span>
                            <span class="spec-item-val">{ram_up_str}</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">Display Panel</span>
                            <span class="spec-item-val">{model_obj.display_type or '-'} ({model_obj.refresh_rate_hz}Hz, {model_obj.resolution})</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">Daya Baterai & Charger</span>
                            <span class="spec-item-val">{model_obj.battery_wh or '-'} Wh ({model_obj.charger_watt}W Adaptor)</span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-item-key">Bobot & Material</span>
                            <span class="spec-item-val">{model_obj.weight_kg or '-'} kg | {model_obj.chassis_material or '-'}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_inputs:
                    st.markdown("### Penyesuaian Kualitas & Kondisi Fisik Laptop")

                    c_in1, c_in2 = st.columns(2)
                    with c_in1:
                        w_type = st.selectbox("1. Status Garansi Resmi:", [
                            "Resmi Indonesia (Aktif >6 bln)", "Habis Garansi Resmi", "Ex-Inter / Distributor"
                        ])
                        b_cond = st.selectbox("2. Kondisi Baterai:", [
                            "Normal Awet (Health >=85%)", "Standar Wajar", "Baterai Drop (Harus Sambil Colok)", "Baterai Kembung (Swollen)"
                        ])
                        bh_val = st.slider("Battery Health Estimasi (%):", min_value=40, max_value=100, value=85)
                        comp_val = st.selectbox("3. Kelengkapan Unit:", [
                            "Fullset Original (Dus + Charger Ori)", "Unit + Charger Original", "Charger OEM / KW", "Batangan (Unit Only)"
                        ])

                    with c_in2:
                        p_grade = st.selectbox("4. Grade Fisik Bodi:", [
                            "Grade A+ (Mulus Like New 99%)", "Grade A (Mulus Standar 95%)", "Grade B (Lecet Pemakaian Wajar)", "Grade C (Dent / Baret Kasar / Penyok)"
                        ])
                        h_cond = st.selectbox("5. Kondisi Engsel Sasis (Hinge):", [
                            "Normal Kokoh", "Engsel Patah / Kendor / Retak"
                        ])
                        s_cond = st.selectbox("6. Kondisi Layar Display:", [
                            "Normal Jernih Bebas Minus", "Whitespot Tipis / Samar", "Whitespot Tebal / Parah", "Dead Pixel", "Layar Bergaris / Flexgate"
                        ])
                        k_cond = st.selectbox("7. Kondisi Keyboard & Backlight:", [
                            "Semua Normal Berfungsi", "Backlight Mati", "Tombol Macet / Minus"
                        ])
                        sec_cond = st.selectbox("8. Keamanan BIOS & Akun:", [
                            "Clean Bebas Reset", "BIOS Lock / Computrace / MDM Locked"
                        ])

                    pricing_engine = LaptopPricingEngine(db)
                    stats = pricing_engine.calculate_variant_pricing_stats(selected_var_obj.id)
                    msrp_num = float(selected_var_obj.official_msrp_new)

                    if stats and stats["sample_count"] >= 2:
                        base_median_fmv = stats["price_median"]
                    else:
                        ret_ratio = LaptopDepreciationEngine.calculate_theoretical_retention(
                            selected_brand, model_obj.name, model_obj.release_year, current_year=2026, processor_model=model_obj.processor_model or ""
                        )
                        base_median_fmv = msrp_num * ret_ratio

                    hedonic_res = pricing_engine.calculate_hedonic_adjusted_price(
                        base_fmv=base_median_fmv,
                        warranty_type=w_type,
                        battery_condition=b_cond,
                        battery_health_pct=bh_val,
                        completeness=comp_val,
                        physical_grade=p_grade,
                        hinge_condition=h_cond,
                        screen_condition=s_cond,
                        keyboard_condition=k_cond,
                        bios_security=sec_cond
                    )

                    adj_price = hedonic_res["adjusted_price"]
                    tot_delta_pct = hedonic_res["total_delta_pct"]
                    tot_depr = LaptopDepreciationEngine.calculate_real_depreciation(msrp_num, adj_price)

                    st.markdown(f"""
                    <div class="val-hero-container">
                        <div class="val-hero-title">Rekomendasi Nilai Pasar Wajar (FMV)</div>
                        <div class="val-hero-price">Rp {adj_price:,.0f}</div>
                        <div class="val-hero-meta">
                            Base FMV Pasar: <b>Rp {base_median_fmv:,.0f}</b> | Penyesuaian Hedonik: <b style="color:{'#34d399' if tot_delta_pct>=0 else '#f87171'}">{tot_delta_pct:+.1f}%</b> | Depresiasi dari MSRP Baru: <b>{tot_depr:.1f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("Lihat Rincian Koefisien Bobot Hedonik Kualitas"):
                        for item, delta in hedonic_res["breakdown"].items():
                            c_color = "#34d399" if delta > 0 else ("#f87171" if delta < 0 else "#94a3b8")
                            st.markdown(f"- **{item}:** <span style='color:{c_color}; font-weight:700;'>{delta:+.1f}%</span>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Terjadi kesalahan pada modul FMV Calculator: {e}")
