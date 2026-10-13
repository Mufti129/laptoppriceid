import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant

from data.catalog_apple import BRAND_DATA as APPLE_DATA
from data.catalog_lenovo import BRAND_DATA as LENOVO_DATA
from data.catalog_asus import BRAND_DATA as ASUS_DATA
from data.catalog_acer import BRAND_DATA as ACER_DATA
from data.catalog_hp import BRAND_DATA as HP_DATA
from data.catalog_dell import BRAND_DATA as DELL_DATA
from data.catalog_others import OTHERS_BRAND_DATA
from data.image_catalog import get_product_image_url

ALL_BRAND_CATALOGS = [
    APPLE_DATA,
    LENOVO_DATA,
    ASUS_DATA,
    ACER_DATA,
    HP_DATA,
    DELL_DATA
] + OTHERS_BRAND_DATA

def seed_master_catalog():
    """Menyemai katalog laptop 2010 - 2026 (100+ model per brand utama)."""
    init_db()
    db = SessionLocal()
    brand_count = 0
    model_count = 0
    variant_count = 0

    try:
        for b_data in ALL_BRAND_CATALOGS:
            b_name = b_data.get("name") or b_data.get("brand_name")
            country = b_data.get("country_origin", "International")
            tier = b_data.get("tier_category", "Mainstream")

            brand = db.query(MasterBrand).filter(MasterBrand.name == b_name).first()
            if not brand:
                brand = MasterBrand(
                    name=b_name,
                    country_origin=country,
                    tier_category=tier
                )
                db.add(brand)
                db.flush()
                brand_count += 1

            for model_info in b_data["models"]:
                model = db.query(MasterModel).filter(
                    MasterModel.brand_id == brand.id,
                    MasterModel.name == model_info["name"]
                ).first()

                if not model:
                    model = MasterModel(
                        brand_id=brand.id,
                        name=model_info["name"],
                        series=model_info.get("series"),
                        release_year=model_info["release_year"],
                        processor_brand=model_info.get("processor_brand"),
                        processor_model=model_info.get("processor_model"),
                        cpu_architecture=model_info.get("cpu_architecture"),
                        cpu_cores=model_info.get("cpu_cores"),
                        cpu_threads=model_info.get("cpu_threads"),
                        cinebench_score=model_info.get("cinebench_score"),
                        gpu_brand=model_info.get("gpu_brand"),
                        gpu_model=model_info.get("gpu_model"),
                        vram_gb=model_info.get("vram_gb", 0),
                        tgp_watt=model_info.get("tgp_watt", 0),
                        display_type=model_info.get("display_type"),
                        screen_size_inch=model_info.get("screen_size_inch"),
                        refresh_rate_hz=model_info.get("refresh_rate_hz", 60),
                        resolution=model_info.get("resolution"),
                        color_gamut=model_info.get("color_gamut"),
                        ram_type=model_info.get("ram_type"),
                        is_ram_upgradeable=model_info.get("is_ram_upgradeable", True),
                        storage_interface=model_info.get("storage_interface"),
                        storage_slots=model_info.get("storage_slots", 1),
                        battery_wh=model_info.get("battery_wh"),
                        charger_watt=model_info.get("charger_watt", 65),
                        weight_kg=model_info.get("weight_kg"),
                        chassis_material=model_info.get("chassis_material"),
                        os_at_launch=model_info.get("os_at_launch"),
                        image_url=get_product_image_url(brand_name, model_info.get("series"), model_info["name"])
                    )
                    db.add(model)
                    db.flush()
                    model_count += 1
                else:
                    if not model.image_url:
                        model.image_url = get_product_image_url(brand_name, model_info.get("series"), model_info["name"])

                for v_info in model_info.get("variants", []):
                    variant = db.query(MasterVariant).filter(
                        MasterVariant.model_id == model.id,
                        MasterVariant.variant_name == v_info["variant_name"]
                    ).first()

                    if not variant:
                        variant = MasterVariant(
                            model_id=model.id,
                            variant_name=v_info["variant_name"],
                            ram_gb=v_info["ram_gb"],
                            storage_gb=v_info["storage_gb"],
                            official_msrp_new=v_info["official_msrp_new"],
                            aliases=v_info.get("aliases"),
                            image_url=model.image_url
                        )
                        db.add(variant)
                        variant_count += 1
                    else:
                        if not variant.image_url:
                            variant.image_url = model.image_url

        db.commit()
        print(f"[SUCCESS] Seeding Master Selesai: {brand_count} Brand Baru, Total Model Baru: {model_count}, Total Varian Baru: {variant_count}")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Gagal Seeding Master: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_catalog()
