from typing import Optional, List, Dict, Any, Tuple
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from models.catalog import MasterVariant, MasterModel, MasterBrand

class LaptopEntityMatcher:
    """
    Fuzzy Entity Matcher & Disambiguation Engine untuk Laptop.
    Menghubungkan teks judul & spesifikasi listing marketplace ke Master Variant ID.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self._variants_cache = self._load_variants()

    def _load_variants(self) -> List[Dict[str, Any]]:
        """Pre-cache master variants dengan metadata dan alias lengkap."""
        variants = self.db.query(
            MasterVariant, MasterModel, MasterBrand
        ).join(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).all()

        cache = []
        for var, model, brand in variants:
            alias_list = [a.strip().lower() for a in (var.aliases or "").split(",") if a.strip()]
            search_corpus = [
                f"{brand.name} {model.name} {var.variant_name}".lower(),
                f"{model.name} {var.ram_gb}gb {var.storage_gb}gb".lower(),
                f"{model.name} {var.variant_name}".lower(),
                var.variant_name.lower()
            ] + alias_list

            cache.append({
                "variant_id": var.id,
                "variant_name": var.variant_name,
                "model_name": model.name,
                "brand_name": brand.name,
                "ram_gb": var.ram_gb,
                "storage_gb": var.storage_gb,
                "release_year": model.release_year,
                "processor_model": model.processor_model or "",
                "gpu_model": model.gpu_model or "",
                "official_msrp": float(var.official_msrp_new) if var.official_msrp_new else None,
                "aliases_list": alias_list,
                "search_corpus": search_corpus
            })
        return cache

    def match(
        self,
        title: str,
        ram_gb: Optional[int] = None,
        storage_gb: Optional[int] = None
    ) -> Tuple[Optional[int], float, Optional[str], Optional[float]]:
        """
        Mencocokkan judul listing ke Master Variant ID.
        Returns: (variant_id, confidence_score, matched_name, official_msrp)
        """
        clean_title = title.lower()
        # Normalisasi singkatan umum pasar laptop Indonesia
        clean_title = clean_title.replace("mbp ", "macbook pro ").replace("mba ", "macbook air ")
        clean_title = clean_title.replace("x1c ", "thinkpad x1 carbon ").replace("t480 ", "thinkpad t480 ")
        clean_title = clean_title.replace("g14 ", "rog zephyrus g14 ").replace("g16 ", "rog zephyrus g16 ")
        clean_title = clean_title.replace("leno ", "lenovo ").replace("thinkpad ", "lenovo thinkpad ")

        best_match_id = None
        best_score = 0.0
        best_name = None
        best_msrp = None

        for item in self._variants_cache:
            # 1. Cek kecocokan RAM & Storage jika diekstrak
            if ram_gb and item["ram_gb"] != ram_gb:
                continue
            if storage_gb and item["storage_gb"] != storage_gb:
                continue

            # 2. Cek apakah ada keyword model / brand / alias
            brand_kw = item["brand_name"].lower()
            model_kw = item["model_name"].lower()
            
            has_relevant_kw = (
                model_kw in clean_title or
                brand_kw in clean_title or
                any(alias in clean_title for alias in item["aliases_list"])
            )
            if not has_relevant_kw:
                continue

            # 3. Hitung score fuzzy matching
            for corpus_text in item["search_corpus"]:
                score_token = fuzz.token_set_ratio(corpus_text, clean_title)
                score_partial = fuzz.partial_ratio(corpus_text, clean_title)
                final_score = (score_token * 0.7) + (score_partial * 0.3)

                # Bonus jika RAM dan Storage tepat di judul
                if str(item["ram_gb"]) in clean_title:
                    final_score += 3.0
                if str(item["storage_gb"]) in clean_title:
                    final_score += 3.0

                if final_score > best_score:
                    best_score = final_score
                    best_match_id = item["variant_id"]
                    best_name = f"{item['brand_name']} {item['model_name']} - {item['variant_name']}"
                    best_msrp = item["official_msrp"]

        if best_score >= 56.0:
            return best_match_id, best_score, best_name, best_msrp

        return None, 0.0, None, None
