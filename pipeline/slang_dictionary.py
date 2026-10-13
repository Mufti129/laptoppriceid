"""
Kamus Slang & Terminologi Khusus Pasar Jual Beli Laptop Bekas & Baru di Indonesia.
Digunakan oleh NLP Normalizer dan Scam Detector untuk ekstraksi metadata spesifikasi pasar sekunder laptop.
"""

WARRANTY_PATTERNS = {
    "resmi_indonesia": [
        r"\bgaransi\s*resmi\b", r"\basus\s*indonesia\b", r"\basus\s*id\b",
        r"\blenovo\s*indonesia\b", r"\blenovo\s*id\b", r"\bacer\s*id\b",
        r"\bibox\b", r"\bdigimap\b", r"\btam\b", r"\bdatascrip\b",
        r"\bdell\s*indonesia\b", r"\bhp\s*indonesia\b", r"\bresmi\s*indo(?:nesia)?\b"
    ],
    "ex_inter": [
        r"\bex\s*inter\b", r"\binter\b", r"\bkeyboard\s*japan\b", r"\bkeyboard\s*jepang\b",
        r"\bkeyboard\s*kanji\b", r"\bkeyboard\s*korea\b", r"\bimport\b", r"\bnon\s*resmi\b"
    ],
    "distributor": [
        r"\bgaransi\s*distributor\b", r"\bdistri\b", r"\bbless\b", r"\bplatinum\b"
    ]
}

BATTERY_PATTERNS = {
    "cycle_count": [
        r"\bcc\s*[:\s]?\s*(\d{1,4})\b",
        r"\bcycle\s*count\s*[:\s]?\s*(\d{1,4})\b",
        r"\bsiklus\s*[:\s]?\s*(\d{1,4})\b"
    ],
    "health_pct": [
        r"\bbh\s*[:\s]?\s*(\d{2,3})\s*%?\b",
        r"\bbattery\s*health\s*[:\s]?\s*(\d{2,3})\s*%?\b",
        r"\bkesehatan\s*baterai\s*[:\s]?\s*(\d{2,3})\s*%?\b",
        r"\bwear\s*level\s*[:\s]?\s*(\d{1,2})\s*%"
    ],
    "drop_or_plugged": [
        r"\bcolok\s*(?:charger|cas|adaptor)\s*(?:terus|aja|mulu)\b",
        r"\bharus\s*sambil\s*(?:cas|charge|colok)\b",
        r"\bbaterai\s*(?:drop|bocor|mati|rusak|soak|habis)\b",
        r"\bbatre\s*(?:drop|bocor|mati|rusak)\b",
        r"\btanpa\s*baterai\b"
    ],
    "swollen": [
        r"\bbaterai\s*kembung\b", r"\bbatre\s*kembung\b", r"\btrackpad\s*ngangkat\b"
    ],
    "healthy": [
        r"\bbaterai\s*(?:awet|normal|tahan\s*\d+\s*jam|sehat)\b",
        r"\bbatre\s*(?:awet|normal|sehat)\b",
        r"\bbattery\s*normal\b"
    ]
}

COMPLETENESS_PATTERNS = {
    "fullset_original": [
        r"\bfullset\s*ori(?:ginal)?\b", r"\bkomplit\s*dus\b", r"\bfullset\s*dus\s*ori\b",
        r"\blengkap\s*nota\b", r"\blengkap\s*dus\b", r"\bfull\s*set\b", r"\bkitab-kitab\b"
    ],
    "unit_and_charger_original": [
        r"\bunit\s*(?:\+|\&)\s*(?:charger|casan|adaptor)\s*ori(?:ginal)?\b",
        r"\bcharger\s*original\s*bawaan\b", r"\bcasan\s*ori\b", r"\bunit\s*charger\b"
    ],
    "charger_oem": [
        r"\bcharger\s*oem\b", r"\badaptor\s*kw\b", r"\bcharger\s*replacement\b",
        r"\bcasan\s*bukan\s*ori\b"
    ],
    "batangan": [
        r"\bbatangan\b", r"\bunit\s*only\b", r"\blaptop\s*(?:aja|tok|doang)\b",
        r"\btanpa\s*(?:charger|casan|adaptor)\b"
    ]
}

PHYSICAL_GRADE_PATTERNS = {
    "grade_a_plus": [
        r"\blike\s*new\b", r"\bmulus\s*99%?\b", r"\bgrade\s*a\+?\b", r"\bistimewa\b",
        r"\bno\s*minus\s*mulus\b", r"\bserasa\s*baru\b", r"\bmulus\s*banget\b"
    ],
    "grade_a": [
        r"\bmulus\s*95%?\b", r"\bmulus\s*wajar\b", r"\bno\s*minus\b", r"\bmulus\b",
        r"\bterawat\b", r"\bbaret\s*pemakaian\s*halus\b"
    ],
    "grade_b": [
        r"\bmulus\s*90%?\b", r"\blecet\s*pemakaian\b", r"\blecet\s*wajar\b", r"\bdent\s*tipis\b",
        r"\bkelupas\s*cat\b", r"\bkorosi\s*tipis\b"
    ],
    "grade_c": [
        r"\bdent\s*(?:parah|kasar|penyok)\b", r"\bbodi\s*retak\b", r"\bcasing\s*pecah\b",
        r"\bbaret\s*parah\b", r"\bpenyok\b"
    ]
}

HINGE_PATTERNS = {
    "broken": [
        r"\bengsel\s*(?:patah|kendor|macet|rusak|retak|goyang|copot)\b",
        r"\bhinge\s*(?:broken|loose|rusak)\b", r"\bbaut\s*engsel\s*dol\b"
    ],
    "normal": [
        r"\bengsel\s*(?:kokoh|aman|rapat|normal)\b"
    ]
}

SCREEN_PATTERNS = {
    "normal_jernih": [
        r"\blayar\s*jernih\b", r"\blayar\s*mulus\b", r"\bno\s*whitespot\b",
        r"\bno\s*dead\s*pixel\b", r"\blcd\s*ori(?:ginal)?\b", r"\blayar\s*normal\b"
    ],
    "whitespot_tipis": [
        r"\bwhitespot\s*tipis\b", r"\bwhite\s*spot\s*samar\b", r"\bwhitespot\s*samar\b",
        r"\bws\s*tipis\b", r"\btitik\s*putih\s*kecil\b"
    ],
    "whitespot_tebal": [
        r"\bwhitespot\s*(?:tebal|banyak|jelas|parah)\b", r"\bws\s*banyak\b"
    ],
    "dead_pixel": [
        r"\bdead\s*pixel\b", r"\bdeadpixel\b", r"\btompel\s*layar\b"
    ],
    "lines_or_flexgate": [
        r"\blayar\s*garis\b", r"\bgaris\s*layar\b", r"\blayar\s*bergaris\b",
        r"\bflexgate\b", r"\bkabel\s*fleksibel\s*layar\b", r"\blayar\s*kedip\b"
    ]
}

KEYBOARD_PATTERNS = {
    "broken": [
        r"\bkeyboard\s*(?:mati|macet|rusak|error|minus|gak\s*bisa)\b",
        r"\bhuruf\s*(?:mati|macet)\b", r"\bada\s*tombol\s*mati\b",
        r"\bbacklight\s*(?:mati|off)\b"
    ],
    "normal": [
        r"\bkeyboard\s*(?:normal|empuk|semua\s*fungsi)\b",
        r"\bbacklight\s*(?:nyala|on|rgb\s*normal)\b"
    ]
}

BIOS_SECURITY_PATTERNS = {
    "locked": [
        r"\bbios\s*(?:lock|terkunci|password)\b",
        r"\bcomputrace\s*(?:on|aktif|locked)\b",
        r"\bmdm\s*(?:lock|terkunci)\b",
        r"\blupa\s*password\s*bios\b",
        r"\bicloud\s*lock\b"
    ],
    "clean": [
        r"\bbebas\s*reset\b", r"\bbios\s*unlocked\b", r"\bno\s*password\s*bios\b",
        r"\bic转型\s*clean\b", r"\bclean\s*icloud\b"
    ]
}

RAM_PATTERNS = [
    r"\bram\s*(\d{1,2})\s*(?:gb)?\b",
    r"\b(\d{1,2})\s*gb\s*ram\b",
    r"\b(\d{1,2})\s*gb\s*(?:ddr4|ddr5|lpddr5|lpddr4x)\b",
    r"\b(\d{1,2})gb\s*/\s*\d{3,4}gb\b"
]

STORAGE_PATTERNS = [
    r"\b(2048|1024|512|256|128)\s*(?:gb)?\s*(?:ssd|nvme|m\.2|pcie)?\b",
    r"\b(1|2)\s*(?:tb|terabyte)\s*(?:ssd|nvme)?\b",
    r"\b\d{1,2}gb\s*/\s*(\d{3,4})\s*(?:gb)?\b",
    r"\b(500|1000)\s*(?:gb)?\s*hdd\b"
]

DP_SCAM_PATTERNS = [
    r"\bdp\b", r"\buang\s*muka\b", r"\bcicilan\b", r"\bangsuran\b",
    r"\bkredit\b", r"\bcredit\b", r"\bleasing\b", r"\bpaylater\b",
    r"\bakulaku\b", r"\bkredivo\b", r"\btanda\s*jadi\b"
]

PRICE_SLANG_PATTERNS = [
    (r"(\d+(?:[\.,]\d+)?)\s*(?:jt|juta)", 1_000_000),
    (r"(\d+(?:[\.,]\d+)?)\s*k\b", 1_000),
    (r"(\d+(?:[\.,]\d+)?)\s*rb\b", 1_000),
]
