import unittest
import sqlite3
import os
from data.chassis_taxonomy import resolve_chassis_code

class TestChassisTaxonomy(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "laptop_bekas.db")

    def test_database_chassis_code_integrity(self):
        """Verifikasi bahwa 1.000 master model memiliki chassis_code yang terisi."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM master_models WHERE chassis_code IS NOT NULL AND chassis_code != '';")
        filled_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM master_models;")
        total_count = cursor.fetchone()[0]

        conn.close()

        self.assertEqual(total_count, 1000)
        self.assertEqual(filled_count, 1000, "Seluruh 1.000 model wajib memiliki kode sasis yang terisi!")

    def test_asus_chassis_resolution(self):
        """Verifikasi taksonomi sasis ASUS ROG Strix dan kasta GPU."""
        # 1. RTX 4060 Gen 13 -> G614JV
        c1 = resolve_chassis_code("ASUS", "ROG Strix G16", "ROG Strix G16 G614", 2023, "Intel Core i7-13650HX", "NVIDIA GeForce RTX 4060")
        self.assertEqual(c1, "G614JV")

        # 2. RTX 4060 Gen 14 Refresh -> G614JVR
        c2 = resolve_chassis_code("ASUS", "ROG Strix G16", "ROG Strix G16 G614", 2024, "Intel Core i9-14900HX", "NVIDIA GeForce RTX 4060")
        self.assertEqual(c2, "G614JVR")

        # 3. RTX 4070 -> G614JIR
        c3 = resolve_chassis_code("ASUS", "ROG Strix G16", "ROG Strix G16 G614", 2024, "Intel Core i9-14900HX", "NVIDIA GeForce RTX 4070")
        self.assertEqual(c3, "G614JIR")

        # 4. RTX 4080 Flagship -> G614JZR
        c4 = resolve_chassis_code("ASUS", "ROG Strix G16", "ROG Strix G16 G614", 2024, "Intel Core i9-14900HX", "NVIDIA GeForce RTX 4080")
        self.assertEqual(c4, "G614JZR")

        # 5. RTX 4050 Entry -> G614JU
        c5 = resolve_chassis_code("ASUS", "ROG Strix G16", "ROG Strix G16 G614", 2023, "Intel Core i7-13650HX", "NVIDIA GeForce RTX 4050")
        self.assertEqual(c5, "G614JU")

    def test_other_brands_chassis_resolution(self):
        """Verifikasi resolusi kode sasis pada Lenovo, Acer, Apple, MSI."""
        # Lenovo Legion Pro 5 Gen 8
        c_lenovo = resolve_chassis_code("Lenovo", "Legion", "Legion Pro 5", 2023, "Intel Core i7-13700HX", "RTX 4070")
        self.assertEqual(c_lenovo, "16IRX8")

        # Acer Predator Helios Neo 16 Gen 13
        c_acer = resolve_chassis_code("Acer", "Predator", "Helios Neo 16", 2023, "Intel Core i7-13700HX", "RTX 4060")
        self.assertEqual(c_acer, "PHN16-71")

        # Apple MacBook Air 13 M2
        c_apple = resolve_chassis_code("Apple", "MacBook Air", "MacBook Air 13 M2", 2022, "Apple M2", "Apple 8-Core GPU")
        self.assertEqual(c_apple, "A2681")

        # MSI Katana 15 Gen 13 RTX 4060
        c_msi = resolve_chassis_code("MSI", "Katana", "Katana 15", 2023, "Intel Core i7-13620H", "RTX 4060")
        self.assertEqual(c_msi, "B13VFK")

if __name__ == "__main__":
    unittest.main()
