import unittest
import sqlite3
import os
import re
from data.generation_taxonomy import resolve_generation_and_canonical_name

class TestGenerationTaxonomy(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "laptop_bekas.db")

    def test_database_generation_integrity(self):
        """Verifikasi bahwa 1.000 master model memiliki generation yang terisi 100%."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM master_models WHERE generation IS NOT NULL AND generation != \x27\x27;")
        filled_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM master_models;")
        total_count = cursor.fetchone()[0]

        conn.close()

        self.assertEqual(total_count, 1000)
        self.assertEqual(filled_count, 1000, "Seluruh 1.000 model wajib memiliki kolom generation yang terisi!")

    def test_zero_redundant_year_suffixes_in_model_names(self):
        """Verifikasi bahwa tidak ada lagi nama model yang berakhiran redundan (YYYY)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM master_models;")
        names = [r[0] for r in cursor.fetchall()]
        conn.close()

        for n in names:
            self.assertFalse(bool(re.search(r"\s*\(\d{4}\)$", n)), f"Model \x27{n}\x27 masih memiliki akhiran tahun (YYYY)!")

    def test_lenovo_generation_mapping(self):
        """Verifikasi taksonomi generasi Lenovo ThinkPad & Legion."""
        # ThinkPad T480 (2018)
        m1, g1 = resolve_generation_and_canonical_name("Lenovo", "ThinkPad T-Series", "ThinkPad T-Series (T14/T480/T450) (2018)", 2018, "Core i5-8250U", "", "T480 (20L5)")
        self.assertEqual(m1, "ThinkPad T480")
        self.assertEqual(g1, "Classic Gen 8")

        # ThinkPad T14 Gen 4 (2023)
        m2, g2 = resolve_generation_and_canonical_name("Lenovo", "ThinkPad T-Series", "ThinkPad T-Series (T14/T480/T450) (2023)", 2023, "Core i7-13700H", "", "21HD")
        self.assertEqual(m2, "ThinkPad T14 Gen 4")
        self.assertEqual(g2, "Gen 4")

        # Legion Pro 5 Gen 8 (2023)
        m3, g3 = resolve_generation_and_canonical_name("Lenovo", "Legion", "Legion 5 / Legion 5 Pro (2023)", 2023, "Core i7-13700H", "RTX 4070", "16IRX8")
        self.assertEqual(m3, "Legion Pro 5 16IRX8")
        self.assertEqual(g3, "Gen 8")

    def test_other_brands_generation_mapping(self):
        """Verifikasi taksonomi generasi HP, Apple, Dell, Axioo."""
        # HP EliteBook G5 & G10
        _, g_hp5 = resolve_generation_and_canonical_name("HP", "EliteBook 840", "EliteBook 840 Series (2018)", 2018)
        self.assertEqual(g_hp5, "G5")
        _, g_hp10 = resolve_generation_and_canonical_name("HP", "EliteBook 840", "EliteBook 840 Series (2023)", 2023)
        self.assertEqual(g_hp10, "G10")

        # Apple M2
        _, g_apple = resolve_generation_and_canonical_name("Apple", "MacBook Air", "MacBook Air 13 M2", 2022, "Apple M2")
        self.assertEqual(g_apple, "Apple Silicon M2")

        # Dell XPS 13 9360
        m_dell, g_dell = resolve_generation_and_canonical_name("Dell", "XPS 13", "XPS 13 Ultrabook (2017)", 2017)
        self.assertEqual(m_dell, "XPS 13 9360")
        self.assertEqual(g_dell, "Gen 9360")

        # Axioo Pongo 760 v2
        m_axioo, g_axioo = resolve_generation_and_canonical_name("Axioo", "Pongo", "Axioo Pongo 760 (2024)", 2024, chassis_code="Pongo 760 v2")
        self.assertEqual(m_axioo, "Axioo Pongo 760 v2")
        self.assertEqual(g_axioo, "Gen 3 (v2)")

if __name__ == "__main__":
    unittest.main()
