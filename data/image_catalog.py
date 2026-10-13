"""
High-resolution Product Image Mapping for Laptop Brands & Series (2010 - 2026).
Curated and CDN-optimized for high-speed delivery on Streamlit Cloud and local dashboards.
"""

IMAGE_SERIES_MAP = {
    # Apple
    ("Apple", "MacBook Pro"): "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
    ("Apple", "MacBook Air"): "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=800&q=80",
    ("Apple", "MacBook 12"): "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80",
    
    # Lenovo
    ("Lenovo", "ThinkPad X1 Carbon"): "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "ThinkPad T-Series (T14/T480/T450)"): "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "ThinkPad X-Series (X13/X280/X230)"): "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "ThinkPad P-Series Workstation"): "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "ThinkPad E-Series (E14/E480)"): "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "Legion 7 / Legion Pro 7i"): "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "Legion 5 / Legion 5 Pro"): "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "Lenovo LOQ 15"): "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "IdeaPad Slim 3"): "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "IdeaPad Slim 5"): "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "IdeaPad Gaming 3"): "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "Yoga 9i Convertible"): "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",
    ("Lenovo", "Yoga Slim 7 / Carbon"): "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",

    # ASUS
    ("ASUS", "ROG Strix SCAR"): "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "ROG Strix G15/G16"): "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "ROG Zephyrus G14"): "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "ROG Zephyrus G16/M16"): "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "ROG Flow X13/Z13"): "https://images.unsplash.com/photo-1585060544812-6b45742d762f?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "TUF Gaming A15/FA506"): "https://images.unsplash.com/photo-1595327656903-2f54e3dce986?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "TUF Gaming F15/FX506"): "https://images.unsplash.com/photo-1595327656903-2f54e3dce986?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "ZenBook 14 OLED"): "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "ZenBook Duo Dual Screen"): "https://images.unsplash.com/photo-1585060544812-6b45742d762f?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "VivoBook 14"): "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "VivoBook S14 OLED"): "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "VivoBook Pro 15 OLED"): "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
    ("ASUS", "ExpertBook B9"): "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80",

    # Acer
    ("Acer", "Predator Helios 16/300"): "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Predator Triton 14/500"): "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Nitro 5 AN515"): "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Nitro 16 AMD"): "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Nitro V 15"): "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Swift Go 14 OLED"): "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Swift Edge 16 OLED"): "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Swift 3 Infinity"): "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Swift X Creator"): "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Aspire 3"): "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Aspire 5"): "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Aspire 7 Gaming"): "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80",
    ("Acer", "Aspire Vero Eco"): "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=800&q=80",

    # HP
    ("HP", "OMEN 16 Gaming"): "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=800&q=80",
    ("HP", "OMEN Transcend 16"): "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=800&q=80",
    ("HP", "Victus 15"): "https://images.unsplash.com/photo-1616588589676-62b3bd4ff6d2?auto=format&fit=crop&w=800&q=80",
    ("HP", "Victus 16"): "https://images.unsplash.com/photo-1616588589676-62b3bd4ff6d2?auto=format&fit=crop&w=800&q=80",
    ("HP", "Pavilion Gaming 15"): "https://images.unsplash.com/photo-1616588589676-62b3bd4ff6d2?auto=format&fit=crop&w=800&q=80",
    ("HP", "Spectre x360 14"): "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80",
    ("HP", "Envy 14/16"): "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80",
    ("HP", "Envy x360 13/14"): "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",
    ("HP", "EliteBook 840 Series"): "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80",
    ("HP", "ZBook Firefly Workstation"): "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80",
    ("HP", "Pavilion 14"): "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
    ("HP", "Pavilion Aero 13"): "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
    ("HP", "Pavilion x360"): "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",

    # Dell
    ("Dell", "Dell XPS 13 Plus"): "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Dell XPS 15"): "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Dell XPS 16"): "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Alienware m16/m15"): "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Alienware x14/x15"): "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Dell G15 Gaming"): "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Dell G16 Gaming"): "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Latitude 7420/7490"): "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Latitude 5420/5480"): "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Precision 5550/5570"): "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Inspiron 14"): "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Inspiron 14 Plus"): "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
    ("Dell", "Inspiron 15"): "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",

    # MSI
    ("MSI", "MSI Titan GT77"): "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
    ("MSI", "MSI Raider GE78/GE76"): "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
    ("MSI", "MSI Stealth 16/14 Studio"): "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80",
    ("MSI", "MSI Katana 15"): "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
    ("MSI", "MSI Cyborg 15"): "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
    ("MSI", "MSI Prestige 14/16"): "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
    ("MSI", "MSI Modern 14"): "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",

    # Axioo
    ("Axioo", "Axioo Pongo 960"): "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
    ("Axioo", "Axioo Pongo 760"): "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
    ("Axioo", "Axioo Pongo 725"): "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
    ("Axioo", "Axioo Hype 7"): "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80",
    ("Axioo", "Axioo Hype 5"): "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80",
    ("Axioo", "Axioo MyBook Hype 3"): "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80",
    ("Axioo", "Axioo MyBook Pro"): "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80",

    # Huawei
    ("Huawei", "Huawei MateBook X Pro"): "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",
    ("Huawei", "Huawei MateBook 14s"): "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80",
    ("Huawei", "Huawei MateBook 13"): "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80",
    ("Huawei", "Huawei MateBook D14"): "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
    ("Huawei", "Huawei MateBook D15"): "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
    ("Huawei", "Huawei MateBook D16"): "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
    ("Huawei", "Huawei MateBook E 2-in-1"): "https://images.unsplash.com/photo-1585060544812-6b45742d762f?auto=format&fit=crop&w=800&q=80",

    # Microsoft
    ("Microsoft", "Surface Pro 9"): "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
    ("Microsoft", "Surface Pro 8"): "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
    ("Microsoft", "Surface Pro X"): "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
    ("Microsoft", "Surface Laptop 5"): "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=800&q=80",
    ("Microsoft", "Surface Laptop Go"): "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=800&q=80",
    ("Microsoft", "Surface Laptop Studio 2"): "https://images.unsplash.com/photo-1585060544812-6b45742d762f?auto=format&fit=crop&w=800&q=80",
    ("Microsoft", "Surface Book"): "https://images.unsplash.com/photo-1585060544812-6b45742d762f?auto=format&fit=crop&w=800&q=80",
}

# Brand default fallbacks
BRAND_DEFAULT_IMAGES = {
    "Apple": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
    "Lenovo": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80",
    "ASUS": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?auto=format&fit=crop&w=800&q=80",
    "Acer": "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=800&q=80",
    "HP": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80",
    "Dell": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
    "MSI": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
    "Axioo": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
    "Huawei": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",
    "Microsoft": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
}

DEFAULT_FALLBACK = "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80"

def get_product_image_url(brand_name: str, series_name: str = None, model_name: str = None) -> str:
    """Resolve the most accurate product image URL for a given laptop brand, series, and model."""
    if brand_name and series_name:
        key = (brand_name.strip(), series_name.strip())
        if key in IMAGE_SERIES_MAP:
            return IMAGE_SERIES_MAP[key]
    
    # Partial matching on series
    if brand_name and series_name:
        for (b, s), url in IMAGE_SERIES_MAP.items():
            if b.lower() == brand_name.strip().lower() and (s.lower() in series_name.lower() or series_name.lower() in s.lower()):
                return url
                
    # Fallback to model name matching
    if brand_name and model_name:
        m_lower = model_name.lower()
        if "pro" in m_lower and brand_name == "Apple":
            return IMAGE_SERIES_MAP[("Apple", "MacBook Pro")]
        if "air" in m_lower and brand_name == "Apple":
            return IMAGE_SERIES_MAP[("Apple", "MacBook Air")]
        if "thinkpad" in m_lower:
            return IMAGE_SERIES_MAP[("Lenovo", "ThinkPad X1 Carbon")]
        if "legion" in m_lower:
            return IMAGE_SERIES_MAP[("Lenovo", "Legion 5 / Legion 5 Pro")]
        if "rog" in m_lower:
            return IMAGE_SERIES_MAP[("ASUS", "ROG Zephyrus G14")]
        if "tuf" in m_lower:
            return IMAGE_SERIES_MAP[("ASUS", "TUF Gaming A15/FA506")]
        if "zenbook" in m_lower:
            return IMAGE_SERIES_MAP[("ASUS", "ZenBook 14 OLED")]
        if "predator" in m_lower:
            return IMAGE_SERIES_MAP[("Acer", "Predator Helios 16/300")]
        if "nitro" in m_lower:
            return IMAGE_SERIES_MAP[("Acer", "Nitro 5 AN515")]
        if "xps" in m_lower:
            return IMAGE_SERIES_MAP[("Dell", "Dell XPS 15")]
        if "alienware" in m_lower:
            return IMAGE_SERIES_MAP[("Dell", "Alienware m16/m15")]
        if "omen" in m_lower:
            return IMAGE_SERIES_MAP[("HP", "OMEN 16 Gaming")]
        if "victus" in m_lower:
            return IMAGE_SERIES_MAP[("HP", "Victus 15")]
        if "pongo" in m_lower:
            return IMAGE_SERIES_MAP[("Axioo", "Axioo Pongo 760")]
        if "surface" in m_lower:
            return IMAGE_SERIES_MAP[("Microsoft", "Surface Pro 9")]
            
    # Brand default
    return BRAND_DEFAULT_IMAGES.get(brand_name, DEFAULT_FALLBACK)
