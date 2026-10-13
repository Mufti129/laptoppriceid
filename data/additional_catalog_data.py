"""
Dataset Tambahan Komprehensif Laptop Pasar Indonesia (2010 - 2026).
Menambahkan model ikonik dan volume tinggi dari Dell, MSI, Axioo (Brand Lokal), Huawei, Microsoft,
serta ekspansi varian Apple, Lenovo, dan ASUS.
"""

ADDITIONAL_CATALOG_LAPTOPS = [
    # ==================== 6. DELL ====================
    {
        "brand_name": "Dell",
        "country_origin": "United States",
        "tier_category": "Business-Enterprise",
        "models": [
            {
                "name": "Dell XPS 15 9530", "series": "XPS Premium", "release_year": 2023,
                "processor_brand": "Intel", "processor_model": "Intel Core i7-13700H",
                "cpu_architecture": "14-Core (6P + 8E) Turbo 5.0GHz", "cpu_cores": 14, "cpu_threads": 20, "cinebench_score": 16200,
                "gpu_brand": "NVIDIA", "gpu_model": "NVIDIA GeForce RTX 4050 Laptop", "vram_gb": 6, "tgp_watt": 50,
                "display_type": "OLED 3.5K Touch, 400 nits, InfinityEdge", "screen_size_inch": 15.6, "refresh_rate_hz": 60,
                "resolution": "3456 x 2160 3.5K", "color_gamut": "100% DCI-P3",
                "ram_type": "DDR5-4800 Dual SODIMM", "is_ram_upgradeable": True, "storage_interface": "Dual M.2 PCIe Gen4 NVMe", "storage_slots": 2,
                "battery_wh": 86, "charger_watt": 130, "weight_kg": 1.92, "chassis_material": "CNC Aluminum & Carbon Fiber Palmrest",
                "os_at_launch": "Windows 11 Home",
                "variants": [
                    {"variant_name": "Dell XPS 15 9530 i7 RTX 4050 16GB/512GB", "ram_gb": 16, "storage_gb": 512, "official_msrp_new": 34999000, "aliases": "xps 15 9530, dell xps 15 2023, xps 15 4050"},
                    {"variant_name": "Dell XPS 15 9530 i7 RTX 4050 32GB/1TB", "ram_gb": 32, "storage_gb": 1024, "official_msrp_new": 41999000, "aliases": "xps 15 9530 32gb, dell xps 15 1tb"}
                ]
            },
            {
                "name": "Alienware m16 R1", "series": "Alienware Gaming", "release_year": 2023,
                "processor_brand": "Intel", "processor_model": "Intel Core i7-13700HX",
                "cpu_architecture": "16-Core (8P + 8E) Turbo 5.0GHz", "cpu_cores": 16, "cpu_threads": 24, "cinebench_score": 21800,
                "gpu_brand": "NVIDIA", "gpu_model": "NVIDIA GeForce RTX 4070 Laptop", "vram_gb": 8, "tgp_watt": 140,
                "display_type": "QHD+ 240Hz, G-Sync, 3ms, ComfortView Plus", "screen_size_inch": 16.0, "refresh_rate_hz": 240,
                "resolution": "2560 x 1600 QHD+ 16:10", "color_gamut": "100% DCI-P3",
                "ram_type": "DDR5-4800 Dual Channel", "is_ram_upgradeable": True, "storage_interface": "Quad M.2 PCIe NVMe", "storage_slots": 2,
                "battery_wh": 86, "charger_watt": 330, "weight_kg": 3.25, "chassis_material": "Dark Metallic Moon Anodized Aluminum",
                "os_at_launch": "Windows 11 Home",
                "variants": [
                    {"variant_name": "Alienware m16 R1 i7 RTX 4070 16GB/1TB", "ram_gb": 16, "storage_gb": 1024, "official_msrp_new": 39999000, "aliases": "alienware m16 r1, dell alienware m16 4070, m16 r1 1tb"}
                ]
            },
            {
                "name": "Dell Latitude 7420", "series": "Latitude Business", "release_year": 2021,
                "processor_brand": "Intel", "processor_model": "Intel Core i7-1185G7",
                "cpu_architecture": "Quad-Core / 8-Threads Turbo 4.8GHz vPro", "cpu_cores": 4, "cpu_threads": 8, "cinebench_score": 5900,
                "gpu_brand": "Intel", "gpu_model": "Intel Iris Xe Graphics 96EUs", "vram_gb": 0, "tgp_watt": 28,
                "display_type": "IPS Anti-Glare 400 nits, Super Low Power", "screen_size_inch": 14.0, "refresh_rate_hz": 60,
                "resolution": "1920 x 1080 FHD", "color_gamut": "100% sRGB",
                "ram_type": "LPDDR4x-4266 Soldered", "is_ram_upgradeable": False, "storage_interface": "M.2 PCIe Gen3 NVMe", "storage_slots": 1,
                "battery_wh": 63, "charger_watt": 65, "weight_kg": 1.22, "chassis_material": "Carbon Fiber / Aluminum",
                "os_at_launch": "Windows 10 Pro",
                "variants": [
                    {"variant_name": "Dell Latitude 7420 i7 16GB/512GB", "ram_gb": 16, "storage_gb": 512, "official_msrp_new": 24500000, "aliases": "latitude 7420, dell latitude 7420 i7, lat 7420 16/512"}
                ]
            }
        ]
    },

    # ==================== 7. MSI ====================
    {
        "brand_name": "MSI",
        "country_origin": "Taiwan",
        "tier_category": "Gaming-Powerhouse",
        "models": [
            {
                "name": "MSI Katana 15 B13V", "series": "Katana Gaming", "release_year": 2023,
                "processor_brand": "Intel", "processor_model": "Intel Core i7-13620H",
                "cpu_architecture": "10-Core (6P + 4E) Turbo 4.9GHz", "cpu_cores": 10, "cpu_threads": 16, "cinebench_score": 15400,
                "gpu_brand": "NVIDIA", "gpu_model": "NVIDIA GeForce RTX 4060 Laptop", "vram_gb": 8, "tgp_watt": 105,
                "display_type": "IPS-Level 144Hz, Thin Bezel", "screen_size_inch": 15.6, "refresh_rate_hz": 144,
                "resolution": "1920 x 1080 FHD", "color_gamut": "45% NTSC",
                "ram_type": "DDR5-5200 Dual SODIMM", "is_ram_upgradeable": True, "storage_interface": "Dual M.2 PCIe Gen4 NVMe", "storage_slots": 2,
                "battery_wh": 53, "charger_watt": 200, "weight_kg": 2.25, "chassis_material": "Core Black Polycarbonate",
                "os_at_launch": "Windows 11 Home",
                "variants": [
                    {"variant_name": "MSI Katana 15 i7 RTX 4060 16GB/1TB", "ram_gb": 16, "storage_gb": 1024, "official_msrp_new": 20999000, "aliases": "msi katana 15, katana 15 rtx 4060, b13v 4060"}
                ]
            },
            {
                "name": "MSI Modern 14 C12M", "series": "Modern Productivity", "release_year": 2022,
                "processor_brand": "Intel", "processor_model": "Intel Core i5-1235U",
                "cpu_architecture": "10-Core (2P + 8E) Turbo 4.4GHz", "cpu_cores": 10, "cpu_threads": 12, "cinebench_score": 7600,
                "gpu_brand": "Intel", "gpu_model": "Intel Iris Xe Graphics", "vram_gb": 0, "tgp_watt": 15,
                "display_type": "IPS-Level 60Hz, Anti-Glare", "screen_size_inch": 14.0, "refresh_rate_hz": 60,
                "resolution": "1920 x 1080 FHD", "color_gamut": "45% NTSC",
                "ram_type": "DDR4-3200 Onboard", "is_ram_upgradeable": False, "storage_interface": "M.2 PCIe Gen3 NVMe", "storage_slots": 1,
                "battery_wh": 39, "charger_watt": 65, "weight_kg": 1.40, "chassis_material": "Classic Black Aluminum",
                "os_at_launch": "Windows 11 Home",
                "variants": [
                    {"variant_name": "MSI Modern 14 i5 8GB/512GB", "ram_gb": 8, "storage_gb": 512, "official_msrp_new": 8799000, "aliases": "msi modern 14, modern 14 c12m, msi modern 14 i5"}
                ]
            }
        ]
    },

    # ==================== 8. AXIOO (BRAND LOKAL INDONESIA) ====================
    {
        "brand_name": "Axioo",
        "country_origin": "Indonesia",
        "tier_category": "Value-Local",
        "models": [
            {
                "name": "Axioo Pongo 760", "series": "Pongo Gaming", "release_year": 2023,
                "processor_brand": "Intel", "processor_model": "Intel Core i7-12650H",
                "cpu_architecture": "10-Core (6P + 4E) Turbo 4.7GHz", "cpu_cores": 10, "cpu_threads": 16, "cinebench_score": 14900,
                "gpu_brand": "NVIDIA", "gpu_model": "NVIDIA GeForce RTX 4060 Laptop", "vram_gb": 8, "tgp_watt": 140,
                "display_type": "IPS 144Hz, 100% sRGB", "screen_size_inch": 15.6, "refresh_rate_hz": 144,
                "resolution": "1920 x 1080 FHD", "color_gamut": "100% sRGB",
                "ram_type": "DDR4-3200 Dual SODIMM Slot", "is_ram_upgradeable": True, "storage_interface": "Dual M.2 PCIe Gen4 NVMe", "storage_slots": 2,
                "battery_wh": 54, "charger_watt": 180, "weight_kg": 2.05, "chassis_material": "Clevo Barebone Matte Black",
                "os_at_launch": "Windows 11 Home",
                "variants": [
                    {"variant_name": "Axioo Pongo 760 i7 RTX 4060 16GB/512GB", "ram_gb": 16, "storage_gb": 512, "official_msrp_new": 15999000, "aliases": "pongo 760, axioo pongo 760, pongo 4060, axioo pongo 16/512"}
                ]
            },
            {
                "name": "Axioo Hype 5", "series": "Hype Consumer", "release_year": 2023,
                "processor_brand": "AMD", "processor_model": "AMD Ryzen 5 5500U",
                "cpu_architecture": "6-Core / 12-Threads Zen 2 Turbo 4.0GHz", "cpu_cores": 6, "cpu_threads": 12, "cinebench_score": 6800,
                "gpu_brand": "AMD", "gpu_model": "AMD Radeon Vega 7 Graphics", "vram_gb": 0, "tgp_watt": 15,
                "display_type": "IPS Anti-Glare 250 nits", "screen_size_inch": 14.0, "refresh_rate_hz": 60,
                "resolution": "1920 x 1080 FHD", "color_gamut": "45% NTSC",
                "ram_type": "DDR4-3200 Dual SODIMM Slot", "is_ram_upgradeable": True, "storage_interface": "M.2 PCIe Gen3 NVMe", "storage_slots": 2,
                "battery_wh": 45, "charger_watt": 65, "weight_kg": 1.41, "chassis_material": "Polycarbonate Slim",
                "os_at_launch": "Windows 11 Home",
                "variants": [
                    {"variant_name": "Axioo Hype 5 Ryzen 5 8GB/256GB", "ram_gb": 8, "storage_gb": 256, "official_msrp_new": 4999000, "aliases": "axioo hype 5, hype 5 ryzen, axioo hype r5 256gb"}
                ]
            }
        ]
    },

    # ==================== 9. HUAWEI ====================
    {
        "brand_name": "Huawei",
        "country_origin": "China",
        "tier_category": "Mainstream",
        "models": [
            {
                "name": "Huawei MateBook D14", "series": "MateBook D", "release_year": 2023,
                "processor_brand": "Intel", "processor_model": "Intel Core i5-1240P",
                "cpu_architecture": "12-Core (4P + 8E) Turbo 4.4GHz", "cpu_cores": 12, "cpu_threads": 16, "cinebench_score": 9200,
                "gpu_brand": "Intel", "gpu_model": "Intel Iris Xe Graphics", "vram_gb": 0, "tgp_watt": 28,
                "display_type": "IPS FullView 16:10, 300 nits, TUV Rheinland", "screen_size_inch": 14.0, "refresh_rate_hz": 60,
                "resolution": "1920 x 1200 WUXGA", "color_gamut": "100% sRGB",
                "ram_type": "LPDDR4x-4266 Soldered", "is_ram_upgradeable": False, "storage_interface": "M.2 NVMe PCIe", "storage_slots": 1,
                "battery_wh": 56, "charger_watt": 65, "weight_kg": 1.39, "chassis_material": "Mystic Silver Metal Body",
                "os_at_launch": "Windows 11 Home",
                "variants": [
                    {"variant_name": "Huawei MateBook D14 i5 8GB/512GB", "ram_gb": 8, "storage_gb": 512, "official_msrp_new": 9499000, "aliases": "matebook d14 2023, huawei d14 i5, matebook d14 512gb"}
                ]
            }
        ]
    },

    # ==================== 10. MICROSOFT ====================
    {
        "brand_name": "Microsoft",
        "country_origin": "United States",
        "tier_category": "Business-Enterprise",
        "models": [
            {
                "name": "Surface Pro 9", "series": "Surface 2-in-1", "release_year": 2022,
                "processor_brand": "Intel", "processor_model": "Intel Core i5-1235U",
                "cpu_architecture": "10-Core (2P + 8E) Intel Evo Platform", "cpu_cores": 10, "cpu_threads": 12, "cinebench_score": 7500,
                "gpu_brand": "Intel", "gpu_model": "Intel Iris Xe Graphics", "vram_gb": 0, "tgp_watt": 15,
                "display_type": "PixelSense Flow 120Hz Touch, 450 nits, Dolby Vision IQ", "screen_size_inch": 13.0, "refresh_rate_hz": 120,
                "resolution": "2880 x 1920 (3:2 Aspect Ratio)", "color_gamut": "100% sRGB",
                "ram_type": "LPDDR5-5200 Soldered", "is_ram_upgradeable": False, "storage_interface": "Removable M.2 2230 PCIe Gen4", "storage_slots": 1,
                "battery_wh": 48, "charger_watt": 65, "weight_kg": 0.88, "chassis_material": "Anodized Aluminum Kickstand",
                "os_at_launch": "Windows 11 Home",
                "variants": [
                    {"variant_name": "Surface Pro 9 i5 8GB/256GB", "ram_gb": 8, "storage_gb": 256, "official_msrp_new": 18499000, "aliases": "surface pro 9, microsoft surface pro 9 256gb, sp9 i5 8/256"}
                ]
            }
        ]
    }
]
