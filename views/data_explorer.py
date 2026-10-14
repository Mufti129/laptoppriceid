import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from models.catalog import ScrapedListing
from pipeline.normalizer import LaptopListingNormalizer
from pipeline.scam_detector import LaptopScamDetector

def render_data_explorer(db: Session):
    """Render modul Live Data Explorer & Scam Filter Monitor."""
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Live Data Explorer & Scam Filter Monitor</div>
        <div class="hero-subtitle">
            Audit langsung listing mentah laptop dari marketplace dan verifikasi efektivitas algoritma pendeteksi iklan pancingan DP, spek disamarkan, dan locked unit.
        </div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Audit Engine</span>
            <span class="hero-tag-pill">Regex & NLP Detection</span>
            <span class="hero-tag-pill">Marketplace Verification</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        f_status = st.radio("Saring Data Listing:", ["Semua Listing", "Listing Tunai Valid", "Iklan DP Semu / Terdeteksi Scam"], horizontal=True)

        q = db.query(ScrapedListing)
        if f_status == "Listing Tunai Valid":
            q = q.filter(ScrapedListing.is_dp_price == False)
        elif f_status == "Iklan DP Semu / Terdeteksi Scam":
            q = q.filter(ScrapedListing.is_dp_price == True)

        raw_rows = q.order_by(ScrapedListing.id.desc()).limit(150).all()

        if raw_rows:
            data = []
            for r in raw_rows:
                data.append({
                    "ID": r.id,
                    "Platform": r.source_platform.upper(),
                    "Judul Iklan": r.title,
                    "Harga (IDR)": f"Rp {r.price:,.0f}",
                    "Status": "⚠️ DP / Scam" if r.is_dp_price else "✅ Tunai Valid",
                    "Kota": r.city or "-",
                    "Garansi": r.warranty_type or "-",
                    "Baterai": r.battery_condition or "-",
                    "Engsel": r.hinge_condition or "-",
                    "Layar": r.screen_condition or "-"
                })
            df_raw = pd.DataFrame(data)
            st.dataframe(df_raw, use_container_width=True, hide_index=True)
            st.caption(f"Menampilkan {len(raw_rows)} listing terbaru dari total database.")
        else:
            st.info("Belum ada data listing yang cocok.")

        st.markdown("---")
        st.markdown("### Uji Coba Langsung Parser NLP & Detektor Scam")
        sample_txt = st.text_area(
            "Masukkan Judul / Deskripsi Iklan Marketplace untuk Diuji:",
            "Laptop ThinkPad T480 Core i5 gen 8 ram 16gb ssd 512gb mulus baterai awet double batre normal layar no whitespot charger ori dp 500rb angsuran 250rb"
        )
        sample_price = st.number_input("Harga Tertera di Iklan (Rp):", min_value=0, value=500000, step=50000)

        if st.button("Uji Parsing & Evaluasi Listing"):
            parsed_ram = LaptopListingNormalizer.extract_ram(sample_txt)
            parsed_ssd = LaptopListingNormalizer.extract_storage(sample_txt)
            is_scam, scam_type, scam_reason = LaptopScamDetector.evaluate_listing(
                sample_price, sample_txt, sample_txt, expected_msrp=12000000
            )

            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.markdown(f"""
                **Hasil Ekstraksi Spesifikasi:**
                - RAM Terdeteksi: `{parsed_ram} GB`
                - Storage SSD Terdeteksi: `{parsed_ssd} GB`
                """)
            with c_res2:
                status_color = "#ef4444" if is_scam else "#10b981"
                st.markdown(f"""
                **Evaluasi Keamanan Harga:**
                - Status: <span style='color:{status_color}; font-weight:800;'>{'⚠️ TERDETEKSI SCAM / DP SEMU' if is_scam else '✅ LISTING AMAN'}</span>
                - Alasan: `{scam_reason}`
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Terjadi kesalahan pada modul Data Explorer: {e}")
