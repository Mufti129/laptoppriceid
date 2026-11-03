import urllib.parse
import streamlit as st
from sqlalchemy.orm import Session
from models.catalog import MasterBrand, MasterModel, MasterVariant
from analytics.pricing_engine import LaptopPricingEngine
from analytics.buyback_engine import BuybackPricingEngine, DEFECT_CATALOG
from data.image_catalog import get_product_image_url

def render_tradein_calculator(db: Session):
    """Render modul Kalkulator Trade-In & Buyback C2B (Taksiran Beli Toko & Tukar Tambah)."""
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Kalkulator Trade-In & Buyback C2B (Taksiran Beli Toko)</div>
        <div class="hero-subtitle">
            Penaksir instan harga jual tunai cepat ke toko (Instant Cash Buyback) dan kredit tukar tambah (Trade-In) dengan kalkulasi potongan kerusakan fisik, biaya sparepart servis, dan formula kanibalan laptop mati total.
        </div>
        <div class="hero-tags">
            <span class="hero-tag-pill">C2B Instant Cash Offer</span>
            <span class="hero-tag-pill">Trade-In Credit Bonus</span>
            <span class="hero-tag-pill">Component Defect Deductions</span>
            <span class="hero-tag-pill">Mati Total Salvage Formula (12.5%)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        brands = [b.name for b in db.query(MasterBrand).order_by(MasterBrand.name).all()]
        if not brands:
            st.warning("Database master katalog masih kosong. Silakan jalankan seeder terlebih dahulu.")
            return

        # 1. Selection Header
        c1, c2, c3 = st.columns([1, 1.3, 1.2])
        with c1:
            selected_brand = st.selectbox("1. Brand Laptop:", brands, index=0)

        brand_obj = db.query(MasterBrand).filter(MasterBrand.name == selected_brand).first()
        models = db.query(MasterModel).filter(MasterModel.brand_id == brand_obj.id).order_by(MasterModel.release_year.desc(), MasterModel.name).all() if brand_obj else []

        model_dict = {f"{m.name} [{m.chassis_code or m.generation or m.release_year}]": m for m in models}
        with c2:
            selected_model_label = st.selectbox("2. Model Laptop:", list(model_dict.keys()) if model_dict else ["-"])

        model_obj = model_dict.get(selected_model_label)
        if not model_obj:
            st.info("Pilih model laptop untuk memulai penaksiran.")
            return

        variants = db.query(MasterVariant).filter(MasterVariant.model_id == model_obj.id).all()
        variant_dict = {f"{v.variant_name} ({v.ram_gb}GB / {v.storage_gb}GB)": v for v in variants}

        with c3:
            selected_variant_name = st.selectbox("3. Varian RAM/Storage:", list(variant_dict.keys()) if variant_dict else ["-"])

        selected_var = variant_dict.get(selected_variant_name)
        if not selected_var:
            st.info("Pilih varian untuk melanjutkan.")
            return

        pricing_engine = LaptopPricingEngine(db)
        stats = pricing_engine.calculate_variant_pricing_stats(selected_var.id)
        base_fmv = stats["price_median"] if (stats and stats.get("price_median", 0) > 0) else (float(selected_var.official_msrp_new or 10000000) * 0.55)

        is_gaming = any(k in (model_obj.series or "").upper() or k in model_obj.name.upper() for k in [
            "ROG", "TUF", "LEGION", "LOQ", "PREDATOR", "NITRO", "OMEN", "VICTUS", "ALIENWARE", "GAMING", "PONGO", "TITAN", "KATANA", "CYBORG"
        ]) or (model_obj.vram_gb and model_obj.vram_gb > 0)

        img_url = model_obj.image_url or get_product_image_url(selected_brand, model_obj.series, model_obj.name)

        st.markdown("---")

        col_specs, col_form = st.columns([1, 2])

        with col_specs:
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden; padding:16px;">
                <img src="{img_url}" alt="{model_obj.name}" style="width:100%; height:180px; object-fit:cover; border-radius:8px; margin-bottom:12px;" />
                <h4 style="margin:0 0 4px 0; color:#ffffff; font-size:1.05rem;">{selected_brand} {model_obj.name}</h4>
                <div style="color:#60a5fa; font-size:0.80rem; font-weight:700;">{model_obj.series or '-'} ({model_obj.release_year})</div>
                <div style="color:#10b981; font-size:0.75rem; font-weight:700; margin-top:2px;">Sasis: {model_obj.chassis_code or '-'} | Generasi: {model_obj.generation or '-'}</div>
                <hr style="border-color:#334155; margin:10px 0;" />
                <div style="font-size:0.78rem; color:#cbd5e1; line-height:1.6;">
                    • <b>CPU:</b> {model_obj.processor_model}<br>
                    • <b>GPU:</b> {model_obj.gpu_model} ({model_obj.vram_gb}GB)<br>
                    • <b>RAM/SSD:</b> {selected_var.ram_gb}GB / {selected_var.storage_gb}GB<br>
                    • <b>Layar:</b> {model_obj.display_type} ({model_obj.screen_size_inch}\")<br>
                    • <b>MSRP Baru:</b> Rp {float(selected_var.official_msrp_new or 0):,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_form:
            st.markdown("### Triage Kondisi Fisik & Kerusakan Unit")

            op_condition = st.radio(
                "Kondisi Operasional Utama:",
                ["Normal / Menyala (Bisa Masuk OS)", "Mati Total / Blank / Rusak Parah (Kanibalan)"],
                index=0,
                horizontal=True
            )

            is_matot = "Mati Total" in op_condition
            selected_defects = []

            if not is_matot:
                st.markdown("#### Checklist Kerusakan Fisik & Fungsional (Pilihan Multi-Komponen):")
                
                tab_layar, tab_daya, tab_bodi, tab_fungsi, tab_lain = st.tabs([
                    "Layar & Display", "Baterai & Daya", "Casing & Engsel", "Input & Audio", "Aksesoris & Storage"
                ])

                with tab_layar:
                    c_l1, c_l2, c_l3 = st.columns(3)
                    with c_l1:
                        if st.checkbox("Layar Pecah / Retak", help=DEFECT_CATALOG["lcd_broken"]["description"]):
                            selected_defects.append("lcd_broken")
                    with c_l2:
                        if st.checkbox("Layar Bergaris / Flicker", help=DEFECT_CATALOG["lcd_lines"]["description"]):
                            selected_defects.append("lcd_lines")
                    with c_l3:
                        if st.checkbox("White Spot / Dead Pixel", help=DEFECT_CATALOG["white_spot"]["description"]):
                            selected_defects.append("white_spot")

                with tab_daya:
                    c_d1, c_d2 = st.columns(2)
                    with c_d1:
                        if st.checkbox("Baterai Drop (<30 Menit)", help=DEFECT_CATALOG["battery_drop"]["description"]):
                            selected_defects.append("battery_drop")
                    with c_d2:
                        if st.checkbox("Baterai Kembung", help=DEFECT_CATALOG["battery_swollen"]["description"]):
                            selected_defects.append("battery_swollen")

                with tab_bodi:
                    c_b1, c_b2, c_b3 = st.columns(3)
                    with c_b1:
                        if st.checkbox("Engsel Patah / Rusak", help=DEFECT_CATALOG["hinge_broken"]["description"]):
                            selected_defects.append("hinge_broken")
                    with c_b2:
                        if st.checkbox("Casing Penyok / Retak (Dent)", help=DEFECT_CATALOG["casing_dent"]["description"]):
                            selected_defects.append("casing_dent")
                    with c_b3:
                        if st.checkbox("Bodi Lecet / Baret Kasar", help=DEFECT_CATALOG["casing_scratch"]["description"]):
                            selected_defects.append("casing_scratch")

                with tab_fungsi:
                    c_f1, c_f2 = st.columns(2)
                    with c_f1:
                        if st.checkbox("Keyboard Eror / Tombol Mati", help=DEFECT_CATALOG["keyboard_faulty"]["description"]):
                            selected_defects.append("keyboard_faulty")
                        if st.checkbox("Touchpad Mati / Eror", help=DEFECT_CATALOG["touchpad_broken"]["description"]):
                            selected_defects.append("touchpad_broken")
                    with c_f2:
                        if st.checkbox("Speaker Sember / Mati", help=DEFECT_CATALOG["speaker_distorted"]["description"]):
                            selected_defects.append("speaker_distorted")
                        if st.checkbox("Kamera / Mic Rusak", help=DEFECT_CATALOG["webcam_broken"]["description"]):
                            selected_defects.append("webcam_broken")
                        if st.checkbox("Port USB / Type-C Rusak", help=DEFECT_CATALOG["port_broken"]["description"]):
                            selected_defects.append("port_broken")

                with tab_lain:
                    c_o1, c_o2 = st.columns(2)
                    with c_o1:
                        if st.checkbox("Charger KW / Bukan Ori", help=DEFECT_CATALOG["charger_kw"]["description"]):
                            selected_defects.append("charger_kw")
                    with c_o2:
                        if st.checkbox("Masih Harddisk (Non-SSD)", help=DEFECT_CATALOG["storage_hdd"]["description"]):
                            selected_defects.append("storage_hdd")

                st.markdown("#### Kelengkapan & Garansi:")
                col_kel, col_gar = st.columns(2)
                with col_kel:
                    completeness = st.selectbox(
                        "Kelengkapan Unit:",
                        ["Unit + Charger Original", "Fullset (Dus Buku + Charger Original)", "Unit Batangan (Hanya Unit)"],
                        index=0
                    )
                with col_gar:
                    warranty_status = st.selectbox(
                        "Status Garansi Resmi:",
                        ["Tidak Ada Garansi / Habis", "Garansi Resmi > 6 Bulan", "Garansi Resmi < 6 Bulan"],
                        index=0
                    )
            else:
                st.info("**Unit Mati Total / Kanibalan:** Perhitungan dialihkan otomatis ke formula nilai sisa komponen (12.5% Salvage Value) untuk pemanfaatan spare part layar, RAM, SSD, adaptor, dan casing.")
                completeness = "Unit + Charger Original"
                warranty_status = "Tidak Ada Garansi / Habis"

        # 3. Hitung Valuasi Buyback
        res = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="MATI_TOTAL" if is_matot else "NORMAL",
            selected_defects=selected_defects,
            completeness=completeness,
            warranty_status=warranty_status,
            brand_name=selected_brand,
            is_gaming=is_gaming,
            release_year=model_obj.release_year
        )

        st.markdown("---")

        # 4. Presentasi Hasil Valuasi 3-Dimensi
        st.markdown("### Hasil Taksiran Harga Multi-Dimensi")

        if not res["is_eligible"]:
            st.error(f"**Pemberitahuan:** {res['ineligibility_reason']}")
            st.caption("Unit Anda tidak memenuhi ambang batas transaksi komersial tunai, namun dapat diserahkan ke program daur ulang limbah elektronik (E-Waste Recycle).")
            return

        kpi_c1, kpi_c2, kpi_c3 = st.columns(3)

        with kpi_c1:
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #3b82f6; border-radius:12px; padding:18px; text-align:center;">
                <div style="font-size:0.75rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Jual Sendiri (Pasar Bebas C2C)</div>
                <div style="font-size:1.60rem; font-weight:800; color:#ffffff; margin:6px 0;">Rp {res['retail_c2c_price']:,.0f}</div>
                <div style="font-size:0.72rem; color:#94a3b8;">Estimasi jual mandiri di marketplace (estimasi 1 - 4 minggu)</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_c2:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(6,78,59,0.25) 100%); border:2px solid #10b981; border-radius:12px; padding:18px; text-align:center;">
                <div style="font-size:0.75rem; text-transform:uppercase; color:#6ee7b7; font-weight:800;">Instant Cash Terima Bersih (Toko)</div>
                <div style="font-size:1.60rem; font-weight:800; color:#34d399; margin:6px 0;">Rp {res['cash_offer_low']:,.0f} - {res['cash_offer_high']:,.0f}</div>
                <div style="font-size:0.72rem; color:#a7f3d0;">Uang tunai / transfer langsung cair hari ini dari mitra toko</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_c3:
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #8b5cf6; border-radius:12px; padding:18px; text-align:center;">
                <div style="font-size:0.75rem; text-transform:uppercase; color:#c4b5fd; font-weight:700;">Kredit Tukar Tambah (Trade-In)</div>
                <div style="font-size:1.60rem; font-weight:800; color:#a78bfa; margin:6px 0;">Rp {res['trade_in_credit']:,.0f}</div>
                <div style="font-size:0.72rem; color:#cbd5e1;">Bonus nilai ekstra ~8-10% jika ditukar tambah dengan unit toko</div>
            </div>
            """, unsafe_allow_html=True)

        # 5. Rincian Pemotongan & Breakdown Transparan
        if res["deductions_breakdown"]:
            with st.expander("Rincian Pemotongan Nilai & Estimasi Biaya Servis Toko", expanded=False):
                st.markdown(f"**Total Akumulasi Biaya Minus:** `Rp {res['total_deductions']:,.0f}` (Margin Pedagang Toko: `{res['margin_rate_pct']}%`)")
                table_breakdown = []
                for item in res["deductions_breakdown"]:
                    table_breakdown.append({
                        "Kategori": item.get("category", "-"),
                        "Komponen / Jenis Minus": item["name"],
                        "Estimasi Potongan Part / Servis": f"- Rp {item['cost']:,.0f}"
                    })
                st.table(table_breakdown)

        st.markdown("---")

        # 6. Form Pengajuan Tiket WhatsApp
        st.markdown("### Ajukan Penjualan / Jadwalkan Inspeksi Toko")
        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            nama_user = st.text_input("Nama Lengkap:", placeholder="Contoh: Budi Santoso")
        with f_c2:
            nomor_wa = st.text_input("Nomor WhatsApp:", placeholder="Contoh: 081234567890")
        with f_c3:
            kota_user = st.text_input("Kota / Domisili:", placeholder="Contoh: Jakarta Selatan / Surabaya")

        minus_str = ", ".join([d["name"] for d in res["deductions_breakdown"]]) if res["deductions_breakdown"] else "Normal Mulus Tanpa Minus"
        wa_text = f"""Halo Admin LaptopPrice ID,
Saya ingin mengajukan penjualan/tukar tambah laptop dengan taksiran sistem sebagai berikut:

• Nama: {nama_user or '-'}
• No WA: {nomor_wa or '-'}
• Kota: {kota_user or '-'}
• Unit: {selected_brand} {model_obj.name}
• Sasis/SKU: {model_obj.chassis_code or '-'}
• Spek: {model_obj.processor_model} | {selected_var.ram_gb}GB RAM / {selected_var.storage_gb}GB SSD
• Kondisi: {'Mati Total' if is_matot else 'Normal Menyala'}
• Rincian Minus: {minus_str}
• Kelengkapan: {completeness}
• Estimasi Instant Cash: Rp {res['cash_offer_low']:,.0f} - Rp {res['cash_offer_high']:,.0f}
• Nilai Tukar Tambah: Rp {res['trade_in_credit']:,.0f}

Bagaimana prosedur inspeksi dan penyerahan unit selanjutnya? Terima kasih."""

        encoded_wa = urllib.parse.quote(wa_text)
        admin_wa_number = "6281285180588"
        wa_url = f"https://api.whatsapp.com/send?phone={admin_wa_number}&text={encoded_wa}"

        st.markdown(f"""
        <div style="margin-top:10px;">
            <a href="{wa_url}" target="_blank" style="display:inline-block; background-color:#10b981; color:#ffffff; font-weight:700; font-size:0.95rem; padding:12px 24px; border-radius:8px; text-decoration:none; box-shadow:0 4px 12px rgba(16,185,129,0.3);">
                Ajukan Penjualan via WhatsApp
            </a>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan pada modul Kalkulator Trade-In & Buyback: {e}")
