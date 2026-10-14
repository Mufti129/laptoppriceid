import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from models.catalog import MasterBrand, MasterModel, MasterVariant
from analytics.pricing_engine import LaptopPricingEngine
from views.common import apply_dark_plotly_layout

def render_price_corridors(db: Session):
    """Render modul 3-Tier Price Corridors & Quantiles."""
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">3-Tier Price Corridors & Quantiles</div>
        <div class="hero-subtitle">
            Rentang harga kuantil statistik pasar: Batas Bawah Murah (P25 - Target Bargain Hunter), Nilai Pasar Wajar (P50 - Median FMV), dan Batas Atas Istimewa (P75 - Pristine Condition).
        </div>
        <div class="hero-tags">
            <span class="hero-tag-pill">P25 Bargain Price</span>
            <span class="hero-tag-pill">P50 Median FMV</span>
            <span class="hero-tag-pill">P75 Pristine Quality</span>
            <span class="hero-tag-pill">Tukey IQR Filtered</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        engine = LaptopPricingEngine(db)
        stats_map = engine.get_all_variant_stats_map()

        all_variants = db.query(
            MasterVariant.id,
            MasterVariant.variant_name,
            MasterModel.name.label("model_name"),
            MasterBrand.name.label("brand_name"),
            MasterModel.release_year
        ).join(MasterModel, MasterVariant.model_id == MasterModel.id)\
         .join(MasterBrand, MasterModel.brand_id == MasterBrand.id)\
         .order_by(MasterBrand.name, MasterModel.release_year.desc()).all()

        corridor_data = []
        for v in all_variants:
            st_data = stats_map.get(v.id)
            if st_data and st_data["sample_count"] >= 2:
                corridor_data.append({
                    "Brand": v.brand_name,
                    "Model": v.model_name,
                    "Varian RAM/Storage": v.variant_name,
                    "Tahun": v.release_year,
                    "P25 Target Beli Murah": f"Rp {st_data['price_p25']:,.0f}",
                    "P50 FMV Median": f"Rp {st_data['price_median']:,.0f}",
                    "P75 Unit Pristine": f"Rp {st_data['price_p75']:,.0f}",
                    "Sample Listing": st_data["sample_count"],
                    "P25_num": st_data["price_p25"],
                    "FMV_num": st_data["price_median"],
                    "P75_num": st_data["price_p75"]
                })

        if corridor_data:
            df_corr = pd.DataFrame(corridor_data)

            all_brands = ["Semua Brand"] + sorted(list(df_corr["Brand"].unique()))
            sel_b = st.selectbox("Saring Berdasarkan Brand:", all_brands)

            filtered_df = df_corr if sel_b == "Semua Brand" else df_corr[df_corr["Brand"] == sel_b]

            display_cols = ["Brand", "Model", "Varian RAM/Storage", "Tahun", "P25 Target Beli Murah", "P50 FMV Median", "P75 Unit Pristine", "Sample Listing"]
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

            # Visual Bar Chart Koridor
            st.markdown("### Visualisasi Koridor Harga 3-Tier")
            subset = filtered_df.head(15)
            if not subset.empty:
                fig_cor = go.Figure()
                fig_cor.add_trace(go.Bar(
                    name="P25 Target Beli Murah",
                    x=subset["Varian RAM/Storage"],
                    y=subset["P25_num"],
                    marker_color="#10b981"
                ))
                fig_cor.add_trace(go.Bar(
                    name="P50 FMV Median",
                    x=subset["Varian RAM/Storage"],
                    y=subset["FMV_num"],
                    marker_color="#3b82f6"
                ))
                fig_cor.add_trace(go.Bar(
                    name="P75 Unit Pristine",
                    x=subset["Varian RAM/Storage"],
                    y=subset["P75_num"],
                    marker_color="#1e3a8a"
                ))
                fig_cor.update_layout(barmode="group", xaxis_tickangle=-45)
                apply_dark_plotly_layout(fig_cor, height=480)
                st.plotly_chart(fig_cor, use_container_width=True)
        else:
            st.info("Data statistik kuantil sedang dipersiapkan.")
    except Exception as e:
        st.error(f"Terjadi kesalahan pada modul Price Corridors: {e}")
