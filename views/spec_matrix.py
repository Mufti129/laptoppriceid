import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from models.catalog import MasterBrand, MasterModel
from data.image_catalog import get_product_image_url

def render_spec_matrix(db: Session):
    """Render modul Spec Matrix & Model Comparison."""
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Laptop Hardware Spec Matrix</div>
        <div class="hero-subtitle">
            Komparasi mendalam matriks spesifikasi hardware laptop secara berdampingan: CPU, benchmark Cinebench, GPU & TGP, RAM upgradeability, panel display, dan bobot (2010 - 2026).
        </div>
        <div class="hero-tags">
            <span class="hero-tag-pill">2010 - 2026 Hardware Archive</span>
            <span class="hero-tag-pill">CPU & Cinebench R23</span>
            <span class="hero-tag-pill">GPU & TGP Wattage</span>
            <span class="hero-tag-pill">RAM Upgradeability</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        all_models = db.query(MasterModel, MasterBrand).join(MasterBrand, MasterModel.brand_id == MasterBrand.id).order_by(MasterModel.release_year.desc(), MasterBrand.name).all()

        model_choice_map = {
            f"{b.name} {m.name} ({m.release_year})": m.id
            for m, b in all_models
        }
        choice_keys = list(model_choice_map.keys())

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            dev1_key = st.selectbox("Pilih Laptop 1:", choice_keys, index=0 if choice_keys else 0)
        with col_c2:
            dev2_key = st.selectbox("Pilih Laptop 2:", choice_keys, index=min(1, len(choice_keys)-1) if choice_keys else 0)

        if dev1_key and dev2_key:
            id1 = model_choice_map[dev1_key]
            id2 = model_choice_map[dev2_key]

            m1 = db.query(MasterModel).filter(MasterModel.id == id1).first()
            m2 = db.query(MasterModel).filter(MasterModel.id == id2).first()

            if m1 and m2:
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    img1 = m1.image_url or get_product_image_url(m1.brand.name if m1.brand else "", m1.series, m1.name)
                    st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden; margin-bottom:14px; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
                        <img src="{img1}" alt="{dev1_key}" style="width:100%; height:190px; object-fit:cover; display:block;" />
                        <div style="padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-weight:700; color:#f8fafc; font-size:0.95rem;">{m1.brand.name if m1.brand else ''} {m1.name}</div>
                                <div style="font-size:0.75rem; color:#94a3b8;">{m1.series or '-'}</div>
                            </div>
                            <span style="color:#38bdf8; font-family:'JetBrains Mono',monospace; font-size:0.8rem; background:rgba(56,189,248,0.12); padding:3px 10px; border-radius:8px; border:1px solid rgba(56,189,248,0.3); font-weight:700;">{m1.release_year}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_p2:
                    img2 = m2.image_url or get_product_image_url(m2.brand.name if m2.brand else "", m2.series, m2.name)
                    st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden; margin-bottom:14px; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
                        <img src="{img2}" alt="{dev2_key}" style="width:100%; height:190px; object-fit:cover; display:block;" />
                        <div style="padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-weight:700; color:#f8fafc; font-size:0.95rem;">{m2.brand.name if m2.brand else ''} {m2.name}</div>
                                <div style="font-size:0.75rem; color:#94a3b8;">{m2.series or '-'}</div>
                            </div>
                            <span style="color:#a855f7; font-family:'JetBrains Mono',monospace; font-size:0.8rem; background:rgba(168,85,247,0.12); padding:3px 10px; border-radius:8px; border:1px solid rgba(168,85,247,0.3); font-weight:700;">{m2.release_year}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                spec_data = {
                    "Parameter Spesifikasi Hardware": [
                        "Tahun Peluncuran", "Prosesor / CPU", "Arsitektur CPU & Cores", "Cinebench R23 Multi-Core",
                        "Kartu Grafis (GPU)", "VRAM & TGP Wattage", "Panel Display & Ukuran", "Refresh Rate & Resolusi",
                        "Color Gamut Display", "Tipe RAM", "Upgradeability RAM", "Interface Storage & Slot",
                        "Kapasitas Baterai", "Daya Charger / Adaptor", "Bobot Total (kg)", "Material Sasis", "Sistem Operasi Bawaan"
                    ],
                    dev1_key: [
                        str(m1.release_year), m1.processor_model or "-", m1.cpu_architecture or "-",
                        f"{m1.cinebench_score:,} pts" if m1.cinebench_score else "-",
                        m1.gpu_model or "-", f"{m1.vram_gb} GB ({m1.tgp_watt}W)" if m1.vram_gb > 0 else "Integrated iGPU",
                        f"{m1.display_type} ({m1.screen_size_inch} inci)", f"{m1.refresh_rate_hz} Hz ({m1.resolution})",
                        m1.color_gamut or "-", m1.ram_type or "-", "Dual SODIMM (Upgradeable)" if m1.is_ram_upgradeable else "Soldered Onboard",
                        f"{m1.storage_interface} ({m1.storage_slots} slot)", f"{m1.battery_wh} Wh" if m1.battery_wh else "-",
                        f"{m1.charger_watt} Watt", f"{m1.weight_kg} kg" if m1.weight_kg else "-",
                        m1.chassis_material or "-", m1.os_at_launch or "-"
                    ],
                    dev2_key: [
                        str(m2.release_year), m2.processor_model or "-", m2.cpu_architecture or "-",
                        f"{m2.cinebench_score:,} pts" if m2.cinebench_score else "-",
                        m2.gpu_model or "-", f"{m2.vram_gb} GB ({m2.tgp_watt}W)" if m2.vram_gb > 0 else "Integrated iGPU",
                        f"{m2.display_type} ({m2.screen_size_inch} inci)", f"{m2.refresh_rate_hz} Hz ({m2.resolution})",
                        m2.color_gamut or "-", m2.ram_type or "-", "Dual SODIMM (Upgradeable)" if m2.is_ram_upgradeable else "Soldered Onboard",
                        f"{m2.storage_interface} ({m2.storage_slots} slot)", f"{m2.battery_wh} Wh" if m2.battery_wh else "-",
                        f"{m2.charger_watt} Watt", f"{m2.weight_kg} kg" if m2.weight_kg else "-",
                        m2.chassis_material or "-", m2.os_at_launch or "-"
                    ]
                }
                df_spec = pd.DataFrame(spec_data)
                st.dataframe(df_spec, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Terjadi kesalahan pada modul Spec Matrix: {e}")
