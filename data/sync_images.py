"""
Script to synchronize product image URLs into SQLite database (master_models & master_variants).
"""
import sys
import os

# Ensure root directory is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models.database import get_db
from models.catalog import MasterModel, MasterVariant, MasterBrand
from data.image_catalog import get_product_image_url

def sync_images():
    print("=== Syncing Product Images to SQLite Database ===")
    with next(get_db()) as db:
        models = db.query(MasterModel).all()
        brand_map = {b.id: b.name for b in db.query(MasterBrand).all()}
        
        updated_models = 0
        for m in models:
            brand_name = brand_map.get(m.brand_id, "")
            img_url = get_product_image_url(brand_name, m.series, m.name)
            m.image_url = img_url
            updated_models += 1
            
        # Also update variants
        variants = db.query(MasterVariant).all()
        updated_variants = 0
        for v in variants:
            if v.model:
                v.image_url = v.model.image_url
            else:
                v.image_url = img_url
            updated_variants += 1
            
        db.commit()
        print(f"[SUCCESS] Updated {updated_models} models and {updated_variants} variants with product image URLs.")

if __name__ == "__main__":
    sync_images()
