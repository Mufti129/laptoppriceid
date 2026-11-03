import urllib.parse
import streamlit as st
from sqlalchemy.orm import Session
from models.catalog import MasterBrand, MasterModel, MasterVariant
from analytics.pricing_engine import LaptopPricingEngine
from analytics.buyback_engine import BuybackPricingEngine, DEFECT_CATALOG
from data.image_catalog import get_product_image_url

def render_tradein_calculator(db: Session):
    """Render modul Kalkulator Trade-In & Buyback C2B dengan parameter diagnostik lengkap."""
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Kalkulator Trade-In & Buyback C2B (Taksiran Beli Toko)</div>
        <div class="hero-subtitle">
            Penaksir instan harga jual tunai cepat ke toko (Instant Cash Buyback) dan kredit tukar tambah (Trade-In) dengan kalkulasi terperinci untuk spesifikasi hardware, kondisi fisik casing, panel layar, kesehatan baterai, fungsi keyboard/audio/port, hingga formula kanibalan laptop mati total.
        </div>
        <div class="hero-tags">
            <span class="hero-tag-pill">C2B Instant Cash Offer</span>
            <span class="hero-tag-pill">Trade-In Credit Bonus (+8%)</span>
            <span class="hero-tag-pill">Multi-Component Grading</span>
            <span class="hero-tag-pill">Salvage Kanibalan Mati Total (12.5%)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        brands = [b.name for b in db.query(MasterBrand).order_by(MasterBrand.name).all()]
        if not brands:
            st.warning("Database master katalog masih kosong. Silakan jalankan seeder terlebih dahulu.")
            return

        # ==============================================================================
        # BAGIAN 1: IDENTIFIKASI UNIT & SPESIFIKASI HARDWARE
        # ==============================================================================
        st.markdown("### 1. Identifikasi Unit & Spesifikasi Hardware")

        row1_c1, row1_c2, row1_c3, row1_c4 = st.columns([1, 1, 0.9, 1.6])
        with row1_c1:
            selected_brand = st.selectbox("Brand Laptop:", brands, index=0)

        brand_obj = db.query(MasterBrand).filter(MasterBrand.name == selected_brand).first()

        # Dynamic series for brand
        all_series_for_brand = [s[0] for s in db.query(MasterModel.series).filter(
            MasterModel.brand_id == brand_obj.id,
            MasterModel.series.isnot(None),
            MasterModel.series != ""
        ).distinct().order_by(MasterModel.series).all()] if brand_obj else []

        with row1_c2:
            selected_series = st.selectbox("Lini Seri / Kategori:", ["Semua Seri"] + all_series_for_brand)

        # Dynamic release years for brand/series
        year_query = db.query(MasterModel.release_year).filter(MasterModel.brand_id == brand_obj.id)
        if selected_series != "Semua Seri":
            year_query = year_query.filter(MasterModel.series == selected_series)
        all_years = sorted(list(set([y[0] for y in year_query.distinct().all() if y[0]])), reverse=True)

        with row1_c3:
            selected_year = st.selectbox("Tahun Rilis:", ["Semua Tahun"] + [str(y) for y in all_years])

        # Filtered model query
        model_query = db.query(MasterModel).filter(MasterModel.brand_id == brand_obj.id)
        if selected_series != "Semua Seri":
            model_query = model_query.filter(MasterModel.series == selected_series)
        if selected_year != "Semua Tahun":
            model_query = model_query.filter(MasterModel.release_year == int(selected_year))

        filtered_models = model_query.order_by(MasterModel.release_year.desc(), MasterModel.name).all()

        model_dict = {
            f"{m.name} [{m.chassis_code or m.generation or m.release_year}]": m
            for m in filtered_models
        }

        with row1_c4:
            selected_model_label = st.selectbox("Model & Kode Sasis / SKU:", list(model_dict.keys()) if model_dict else ["-"])

        model_obj = model_dict.get(selected_model_label)
        if not model_obj:
            st.info("Pilih model laptop untuk memulai penaksiran.")
            return

        # Variants for this model
        variants = db.query(MasterVariant).filter(MasterVariant.model_id == model_obj.id).all()
        default_var = variants[0] if variants else None
        base_ram = default_var.ram_gb if default_var else 8
        base_rom = default_var.storage_gb if default_var else 512

        # Row 2: Granular Hardware Configuration
        row2_c1, row2_c2, row2_c3, row2_c4 = st.columns([1.2, 0.9, 1.1, 1.2])

        with row2_c1:
            st.text_input("Prosesor (CPU Pabrikan):", value=model_obj.processor_model, disabled=True)

        with row2_c2:
            ram_options = [4, 8, 16, 32, 64]
            ram_idx = ram_options.index(base_ram) if base_ram in ram_options else 1
            selected_ram = st.selectbox("Kapasitas RAM:", ram_options, index=ram_idx, format_func=lambda x: f"{x} GB")

        with row2_c3:
            storage_options = [
                (128, "SSD", "128 GB SSD"),
                (256, "SSD", "256 GB NVMe SSD"),
                (512, "SSD", "512 GB NVMe SSD"),
                (1024, "SSD", "1 TB NVMe SSD"),
                (2048, "SSD", "2 TB NVMe SSD"),
                (500, "HDD", "500 GB Harddisk (Non-SSD)"),
                (1000, "HDD", "1 TB Harddisk (Non-SSD)")
            ]
            default_st_idx = 2
            for idx, opt in enumerate(storage_options):
                if opt[0] == base_rom and opt[1] == "SSD":
                    default_st_idx = idx
                    break
            selected_st_tuple = st.selectbox(
                "Kapasitas & Tipe Storage:",
                storage_options,
                index=default_st_idx,
                format_func=lambda x: x[2]
            )
            selected_storage_gb = selected_st_tuple[0]
            selected_storage_type = selected_st_tuple[1]

        with row2_c4:
            gpu_display = f"{model_obj.gpu_model} ({model_obj.vram_gb}GB VRAM)" if model_obj.vram_gb and model_obj.vram_gb > 0 else model_obj.gpu_model
            st.text_input("Kartu Grafis (GPU):", value=gpu_display, disabled=True)

        pricing_engine = LaptopPricingEngine(db)
        stats = pricing_engine.calculate_variant_pricing_stats(default_var.id) if default_var else None
        base_fmv = stats["price_median"] if (stats and stats.get("price_median", 0) > 0) else (float(default_var.official_msrp_new if default_var else 10000000) * 0.55)

        is_gaming = any(k in (model_obj.series or "").upper() or k in model_obj.name.upper() for k in [
            "ROG", "TUF", "LEGION", "LOQ", "PREDATOR", "NITRO", "OMEN", "VICTUS", "ALIENWARE", "GAMING", "PONGO", "TITAN", "KATANA", "CYBORG"
        ]) or (model_obj.vram_gb and model_obj.vram_gb > 0)

        img_url = model_obj.image_url or get_product_image_url(selected_brand, model_obj.series, model_obj.name)

        st.markdown("---")

        # ==============================================================================
        # BAGIAN 2: DIAGNOSTIK KONDISI OPERASIONAL & GRADE FISIK
        # ==============================================================================
        st.markdown("### 2. Diagnostik Kondisi Operasional & Grade Fisik Unit")

        op_condition = st.radio(
            "Kondisi Operasional Utama Unit:",
            [
                "Normal / Menyala (Bisa Booting & Masuk OS Windows / macOS)",
                "Mati Total / Rusak Parah / No Display (Untuk Kanibalan Sparepart)"
            ],
            index=0,
            horizontal=True
        )

        is_matot = "Mati Total" in op_condition
        selected_defects = []

        if not is_matot:
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)

            with f_col1:
                physical_grade = st.selectbox(
                    "Grade Fisik Casing & Kosmetik:",
                    [
                        "Grade A: Mulus Seperti Baru (95-100%, Tanpa Dent/Baret)",
                        "Grade B: Pemakaian Normal (85-94%, Baret Halus Wajar)",
                        "Grade C: Pemakaian Berat (70-84%, Ada Dent/Penyok Sudut)",
                        "Grade D: Rusak Fisik (Casing Retak / Engsel Patah)"
                    ],
                    index=1
                )

            with f_col2:
                battery_grade = st.selectbox(
                    "Kesehatan & Ketahanan Baterai:",
                    [
                        "Sangat Sehat (>3.5 Jam / Health >85%)",
                        "Normal Standar (1.5 - 3.5 Jam / Health 70-85%)",
                        "Baterai Drop (<45 Menit / Wajib Colok Charger)",
                        "Baterai Kembung / Rusak (Membengkak Menekan Casing)"
                    ],
                    index=1
                )

            with f_col3:
                screen_grade = st.selectbox(
                    "Kondisi Panel Layar (Display):",
                    [
                        "Layar Mulus Sempurna (100% Bersih & Normal)",
                        "White Spot / Jamur / Bekas Keyboard Nempel Tipis",
                        "Layar Bergaris / Flicker (Garis Vertikal/Horizontal)",
                        "Layar Pecah / Retak / Tompel Hitam / Blank"
                    ],
                    index=0
                )

            with f_col4:
                keyboard_grade = st.selectbox(
                    "Kondisi Keyboard & Trackpad:",
                    [
                        "Semua Tombol & Trackpad Normal 100%",
                        "Tombol Keyboard Eror / Macet / Lepas",
                        "Touchpad Eror / Klik Mati",
                        "Keyboard & Touchpad Rusak Keduanya"
                    ],
                    index=0
                )

            # ==============================================================================
            # BAGIAN 3: KELENGKAPAN, AKSESORIS, PORT & LEGALITAS
            # ==============================================================================
            st.markdown("### 3. Kelengkapan Unit, Fungsionalitas Port & Legalitas")

            k_col1, k_col2, k_col3 = st.columns(3)

            with k_col1:
                completeness = st.selectbox(
                    "Kelengkapan Unit & Charger:",
                    [
                        "Fullset Lengkap (Dus Asli Pabrik + Manual + Charger Original)",
                        "Unit + Charger Original Bawaan",
                        "Unit + Charger KW / Pengganti (Bukan Ori)",
                        "Batangan (Hanya Unit Saja Tanpa Charger)"
                    ],
                    index=1
                )

            with k_col2:
                warranty_status = st.selectbox(
                    "Status Garansi Resmi:",
                    [
                        "Garansi Resmi Indonesia Aktif > 6 Bulan",
                        "Garansi Resmi Indonesia Aktif < 6 Bulan",
                        "Garansi Toko / Garansi Distributor / Habis"
                    ],
                    index=2
                )

            with k_col3:
                bios_security = st.selectbox(
                    "Keamanan Akun & Kunci BIOS:",
                    [
                        "Bebas Kunci (BIOS Tanpa Password, iCloud/MDM Bersih)",
                        "Terkunci Password BIOS / MDM / Computrace Perusahaan"
                    ],
                    index=0
                )

            # Checklist tambahan minus fungsional port & multimedia
            with st.expander("Pemeriksaan Minus Fungsional Tambahan (Speaker, Kamera, Port USB/Type-C)", expanded=False):
                chk_c1, chk_c2, chk_c3 = st.columns(3)
                with chk_c1:
                    if st.checkbox("Speaker Sember / Suara Pecah / Mati Sebelah", help=DEFECT_CATALOG["speaker_distorted"]["description"]):
                        selected_defects.append("speaker_distorted")
                with chk_c2:
                    if st.checkbox("Kamera Webcam / Mikrofon Internal Rusak", help=DEFECT_CATALOG["webcam_broken"]["description"]):
                        selected_defects.append("webcam_broken")
                with chk_c3:
                    if st.checkbox("Port USB / Type-C Longgar atau Rusak", help=DEFECT_CATALOG["port_broken"]["description"]):
                        selected_defects.append("port_broken")

        else:
            st.info("Unit Mati Total / Kanibalan: Parameter otomatis dialihkan ke formula nilai sisa komponen (12.5% Salvage Value) untuk pemanfaatan spare part layar, RAM, SSD, adaptor, dan casing.")
            physical_grade = "Grade B"
            battery_grade = "Normal"
            screen_grade = "Normal"
            keyboard_grade = "Normal"
            completeness = "Unit + Charger Original Bawaan"
            warranty_status = "Garansi Toko / Garansi Distributor / Habis"
            bios_security = "Bebas Kunci"

        # ==============================================================================
        # BAGIAN 4: KALKULASI BUYBACK ENGINE & HASIL 3-DIMENSI
        # ==============================================================================
        res = BuybackPricingEngine.calculate_buyback_offer(
            base_fmv=base_fmv,
            condition_state="MATI_TOTAL" if is_matot else "NORMAL",
            selected_defects=selected_defects,
            completeness=completeness,
            warranty_status=warranty_status,
            brand_name=selected_brand,
            is_gaming=is_gaming,
            release_year=model_obj.release_year,
            physical_grade=physical_grade,
            battery_condition=battery_grade,
            screen_condition=screen_grade,
            keyboard_condition=keyboard_grade,
            bios_security=bios_security,
            ram_gb=selected_ram,
            storage_gb=selected_storage_gb,
            storage_type=selected_storage_type,
            base_ram_gb=base_ram,
            base_storage_gb=base_rom
        )

        st.markdown("---")
        st.markdown("### 4. Hasil Taksiran Harga Multi-Dimensi")

        if not res["is_eligible"]:
            st.error(f"Pemberitahuan: {res['ineligibility_reason']}")
            st.caption("Unit Anda tidak memenuhi ambang batas transaksi komersial tunai, namun dapat diserahkan ke program daur ulang limbah elektronik (E-Waste Recycle).")
            return

        res_col_img, res_col_cards = st.columns([1, 2.5])

        with res_col_img:
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden; padding:14px; text-align:center;">
                <img src="{img_url}" alt="{model_obj.name}" style="width:100%; height:150px; object-fit:cover; border-radius:8px; margin-bottom:10px;" />
                <div style="font-weight:700; color:#f8fafc; font-size:0.92rem;">{selected_brand} {model_obj.name}</div>
                <div style="color:#60a5fa; font-size:0.76rem;">{model_obj.series or '-'} ({model_obj.release_year})</div>
                <div style="color:#94a3b8; font-size:0.72rem; margin-top:4px;">Sasis: {model_obj.chassis_code or '-'} | Gen: {model_obj.generation or '-'}</div>
                <div style="border-top:1px solid #334155; margin-top:8px; padding-top:8px; font-size:0.74rem; color:#cbd5e1; text-align:left; line-height:1.5;">
                    • CPU: {model_obj.processor_model}<br>
                    • RAM: {selected_ram} GB<br>
                    • Storage: {selected_storage_gb} GB {selected_storage_type}<br>
                    • GPU: {model_obj.gpu_model}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with res_col_cards:
            kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
            with kpi_c1:
                st.markdown(f"""
                <div style="background:#1e293b; border:1px solid #3b82f6; border-radius:12px; padding:16px; text-align:center;">
                    <div style="font-size:0.74rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Jual Sendiri (Pasar Bebas C2C)</div>
                    <div style="font-size:1.50rem; font-weight:800; color:#ffffff; margin:6px 0;">Rp {res['retail_c2c_price']:,.0f}</div>
                    <div style="font-size:0.70rem; color:#94a3b8;">Estimasi jual mandiri di marketplace (estimasi 1 - 4 minggu)</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_c2:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(6,78,59,0.25) 100%); border:2px solid #10b981; border-radius:12px; padding:16px; text-align:center;">
                    <div style="font-size:0.74rem; text-transform:uppercase; color:#6ee7b7; font-weight:800;">Instant Cash Terima Bersih (Toko)</div>
                    <div style="font-size:1.50rem; font-weight:800; color:#34d399; margin:6px 0;">Rp {res['cash_offer_low']:,.0f} - {res['cash_offer_high']:,.0f}</div>
                    <div style="font-size:0.70rem; color:#a7f3d0;">Uang tunai / transfer langsung cair hari ini dari mitra toko</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_c3:
                st.markdown(f"""
                <div style="background:#1e293b; border:1px solid #8b5cf6; border-radius:12px; padding:16px; text-align:center;">
                    <div style="font-size:0.74rem; text-transform:uppercase; color:#c4b5fd; font-weight:700;">Kredit Tukar Tambah (Trade-In)</div>
                    <div style="font-size:1.50rem; font-weight:800; color:#a78bfa; margin:6px 0;">Rp {res['trade_in_credit']:,.0f}</div>
                    <div style="font-size:0.70rem; color:#cbd5e1;">Bonus nilai ekstra ~8-10% jika ditukar tambah dengan unit toko</div>
                </div>
                """, unsafe_allow_html=True)

            # Breakdown expander
            with st.expander("Rincian Parameter & Pemotongan Nilai Servis Toko", expanded=False):
                hw_diff_note = f"+ Rp {res.get('hw_spec_adj', 0):,.0f}" if res.get('hw_spec_adj', 0) >= 0 else f"- Rp {abs(res.get('hw_spec_adj', 0)):,.0f}"
                st.markdown(f"**Penyesuaian RAM/Storage:** `{hw_diff_note}` | **Total Akumulasi Biaya Minus:** `Rp {res['total_deductions']:,.0f}` | **Margin Pedagang Toko:** `{res['margin_rate_pct']}%`")
                table_breakdown = []
                for item in res["deductions_breakdown"]:
                    table_breakdown.append({
                        "Kategori": item.get("category", "-"),
                        "Komponen / Jenis Minus": item["name"],
                        "Estimasi Potongan Part / Servis": f"- Rp {item['cost']:,.0f}"
                    })
                if table_breakdown:
                    st.table(table_breakdown)
                else:
                    st.info("Tidak ada potongan minus fisik pada unit ini.")

        st.markdown("---")

        # ==============================================================================
        # BAGIAN 5: FORM PENGAJUAN & TIKET WHATSAPP RESMI
        # ==============================================================================
        st.markdown("### 5. Ajukan Penjualan / Jadwalkan Inspeksi Toko")
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
• Seri / Sasis: {model_obj.series or '-'} [{model_obj.chassis_code or '-'}]
• Generasi: {model_obj.generation or '-'}
• Konfigurasi: {model_obj.processor_model} | {selected_ram}GB RAM / {selected_storage_gb}GB {selected_storage_type}
• Kartu Grafis: {model_obj.gpu_model}
• Kondisi Operasional: {'Mati Total' if is_matot else 'Normal Menyala'}
• Grade Fisik: {physical_grade}
• Baterai: {battery_grade}
• Layar: {screen_grade}
• Keyboard: {keyboard_grade}
• Kelengkapan: {completeness}
• Garansi: {warranty_status}
• Rincian Minus: {minus_str}
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
