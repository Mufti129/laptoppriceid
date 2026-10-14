import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from analytics.pricing_engine import LaptopPricingEngine
from data.image_catalog import get_product_image_url

def render_arbitrage_radar(db: Session):
    """Render modul Arbitrage & Hot Deals Radar."""
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Laptop Arbitrage & Hot Deals Radar</div>
        <div class="hero-subtitle">
            Radar otomatis pendeteksi peluang beli murah di bawah harga wajar pasar (Undervalued Listing) untuk margin keuntungan optimal reseller laptop.
        </div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Margin Arbitrase</span>
            <span class="hero-tag-pill">Underpriced Alert</span>
            <span class="hero-tag-pill">Anti-Scam Verified</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        disc_thresh = st.slider("Ambang Batas Minimum Diskon Arbitrase (%):", min_value=8, max_value=30, value=12)
        engine = LaptopPricingEngine(db)
        deals = engine.find_hot_deals(discount_threshold_pct=float(disc_thresh))

        if deals:
            st.markdown(f"""
            <div class="info-box-green">
                <div class="info-box-title">Terverifikasi {len(deals)} Unit Peluang Arbitrase Laptop Aktif</div>
                <div class="info-box-desc">Seluruh listing telah melewati validasi non-DP dan verifikasi anti-spek palsu. Potensi keuntungan dihitung dari selisih harga penawaran terhadap FMV.</div>
            </div>
            """, unsafe_allow_html=True)

            # Top 3 Visual Deal Cards
            st.markdown("#### 🔥 Rekomendasi Hot Deals Pilihan")
            c_deal_cards = st.columns(min(3, len(deals)))
            for idx, col in enumerate(c_deal_cards):
                deal = deals[idx]
                d_img = get_product_image_url(deal.get("brand", ""), model_name=deal.get("model", ""))
                tier_badge_color = "#10b981" if "Tier 1" in deal.get("deal_tier", "") else "#3b82f6"
                with col:
                    st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden; margin-bottom:18px; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
                        <div style="position:relative;">
                            <img src="{d_img}" alt="{deal['model']}" style="width:100%; height:140px; object-fit:cover; display:block;" />
                            <div style="position:absolute; top:8px; right:8px; background:{tier_badge_color}; color:#fff; font-size:0.72rem; font-weight:800; padding:3px 8px; border-radius:8px;">
                                Hemat {deal['discount_pct']:.1f}%
                            </div>
                        </div>
                        <div style="padding:12px 14px;">
                            <div style="font-weight:700; color:#f8fafc; font-size:0.92rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{deal['brand']} {deal['model']}</div>
                            <div style="font-size:0.75rem; color:#94a3b8; margin:2px 0 8px 0;">{deal['city']} • {deal['platform'].upper()}</div>
                            <div style="display:flex; justify-content:space-between; align-items:baseline; border-top:1px solid rgba(51,65,85,0.4); padding-top:8px;">
                                <div>
                                    <div style="font-size:0.68rem; color:#94a3b8;">Harga Beli</div>
                                    <div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem; font-weight:800; color:#38bdf8;">Rp {deal['price']:,.0f}</div>
                                </div>
                                <div style="text-align:right;">
                                    <div style="font-size:0.68rem; color:#34d399;">Estimasi Margin</div>
                                    <div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem; font-weight:800; color:#34d399;">+Rp {deal['potential_profit']:,.0f}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            df_deals = pd.DataFrame(deals)

            display_df = df_deals[[
                "deal_tier", "brand", "model", "variant", "price", "fmv_price", "discount_pct", "potential_profit", "city", "platform", "warranty_type", "battery_condition", "hinge_condition", "screen_condition"
            ]].copy()

            display_df.columns = [
                "Tier Peluang", "Brand", "Model", "Varian", "Harga Listing", "FMV Pasar", "Diskon (%)", "Potensi Margin (IDR)", "Kota", "Platform", "Garansi", "Baterai", "Engsel", "Layar"
            ]

            display_df["Harga Listing"] = display_df["Harga Listing"].apply(lambda x: f"Rp {x:,.0f}")
            display_df["FMV Pasar"] = display_df["FMV Pasar"].apply(lambda x: f"Rp {x:,.0f}")
            display_df["Potensi Margin (IDR)"] = display_df["Potensi Margin (IDR)"].apply(lambda x: f"Rp {x:,.0f}")
            display_df["Diskon (%)"] = display_df["Diskon (%)"].apply(lambda x: f"{x:.1f}%")

            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info(f"Tidak ada listing yang memenuhi kriteria diskon >= {disc_thresh}%.")
    except Exception as e:
        st.error(f"Terjadi kesalahan pada modul Arbitrage Radar: {e}")
