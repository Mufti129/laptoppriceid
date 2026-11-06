import unittest
from pathlib import Path
import openpyxl

ROOT_DIR = Path(__file__).resolve().parent.parent
EXCEL_PRIMARY = Path("/Users/macbookair/Downloads/pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx")
EXCEL_EXPORT = ROOT_DIR / "exports" / "pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx"


class TestExcelFmvAndListings(unittest.TestCase):
    """Pengujian integritas berkas Excel dengan sheet 'list harga tarikan', 'Matriks FMV (Model & Tahun)', dan rumus FMV katalog."""

    @classmethod
    def setUpClass(cls):
        cls.excel_path = EXCEL_PRIMARY if EXCEL_PRIMARY.exists() else EXCEL_EXPORT
        cls.wb = openpyxl.load_workbook(cls.excel_path, data_only=False)

    def test_workbook_sheets_exist(self):
        """Verifikasi bahwa sheet baru 'Matriks FMV (Model & Tahun)' dan sheet lainnya lengkap."""
        expected_sheets = [
            "Ringkasan & Analisis",
            "Pemetaan Lengkap (713 Tipe)",
            "Tipe Belum Ada (Flag Y)",
            "Katalog Seri LaptopMedia",
            "list harga tarikan",
            "Matriks FMV (Model & Tahun)"
        ]
        for s in expected_sheets:
            self.assertIn(s, self.wb.sheetnames, f"Sheet '{s}' harus ada di workbook.")

    def test_list_harga_tarikan_integrity(self):
        """Verifikasi bahwa sheet 'list harga tarikan' memuat ribuan listing riil terverifikasi."""
        ws = self.wb["list harga tarikan"]
        self.assertGreaterEqual(ws.max_row, 2000, "Sheet 'list harga tarikan' harus memiliki minimal 2.000 listing.")
        self.assertEqual(ws.max_column, 13, "Sheet 'list harga tarikan' harus memiliki tepat 13 kolom.")

        expected_headers = [
            "No", "Platform Sumber", "Brand", "Model Terkait (LaptopMedia)", "Tahun Rilis Model",
            "Nama Seri / Tipe Target", "Nama Produk / Judul Iklan", "Harga (Rp)",
            "Nama Toko / Seller", "Lokasi / Kota", "Status Seller", "URL Produk", "Waktu Tarikan"
        ]
        actual_headers = [ws.cell(1, c).value for c in range(1, 14)]
        self.assertEqual(actual_headers, expected_headers)

        for r in [2, 50, 100, 500, 1000]:
            no_val = ws.cell(r, 1).value
            platform_val = ws.cell(r, 2).value
            year_val = ws.cell(r, 5).value
            price_val = ws.cell(r, 8).value
            self.assertIsNotNone(no_val)
            self.assertIsNotNone(platform_val)
            self.assertIsInstance(year_val, int)
            self.assertTrue(2010 <= year_val <= 2026, f"Tahun rilis tidak valid pada baris {r}: {year_val}")
            self.assertIsInstance(price_val, (int, float))
            self.assertGreaterEqual(price_val, 800000)

    def test_matriks_fmv_sheet_integrity(self):
        """Verifikasi struktur dan isi tab 'Matriks FMV (Model & Tahun)'."""
        ws = self.wb["Matriks FMV (Model & Tahun)"]
        self.assertGreaterEqual(ws.max_row, 500, "Sheet 'Matriks FMV (Model & Tahun)' harus memiliki minimal 500 entri.")
        self.assertEqual(ws.max_column, 11, "Sheet 'Matriks FMV (Model & Tahun)' harus memiliki tepat 11 kolom.")

        expected_headers = [
            "Merek", "Model Terkait (LaptopMedia)", "Mapping Kategori Internal", "Tahun Rilis", "Sampel Riil",
            "Harga Minimum (Rp)", "Harga Bawah P25 (Rp)", "Harga FMV Median (Rp)", "Harga Atas P75 (Rp)",
            "Harga Maksimum (Rp)", "Harga Rata-Rata (Rp)"
        ]
        actual_headers = [ws.cell(1, c).value for c in range(1, 12)]
        self.assertEqual(actual_headers, expected_headers)

        for r in [2, 20, 50, 100, 200]:
            brand = ws.cell(r, 1).value
            model = ws.cell(r, 2).value
            tier = ws.cell(r, 3).value
            year = ws.cell(r, 4).value
            samples = ws.cell(r, 5).value
            p_min = ws.cell(r, 6).value
            p_med = ws.cell(r, 8).value
            p_max = ws.cell(r, 10).value

            self.assertIsNotNone(brand)
            self.assertIsNotNone(model)
            self.assertIn(tier, ['Laptop Gaming', 'Laptop Premium / Ultrabook', 'Laptop Bisnis / Commercial', 'Laptop Consumer'])
            self.assertIsInstance(year, int)
            self.assertIsInstance(samples, int)
            self.assertGreaterEqual(samples, 1)
            self.assertIsInstance(p_med, (int, float))
            self.assertTrue(p_min <= p_med <= p_max, f"Distribusi harga tidak valid pada baris {r}: min={p_min}, med={p_med}, max={p_max}")

    def test_katalog_seri_laptopmedia_lookup_formulas(self):
        """Verifikasi bahwa rumus katalog mereferensikan 'Matriks FMV (Model & Tahun)' secara universal bebas dari #NAME?."""
        ws = self.wb["Katalog Seri LaptopMedia"]
        self.assertGreaterEqual(ws.max_row, 4800, "Sheet Katalog Seri harus memiliki > 4800 baris.")
        self.assertGreaterEqual(ws.max_column, 13, "Sheet Katalog Seri harus memiliki 13 kolom.")

        headers = [ws.cell(1, c).value for c in range(8, 14)]
        expected_new_headers = [
            "Jumlah Sampel Iklan (Model + Tahun)",
            "Harga Pasar Terendah (Min)",
            "Harga Pasar Tertinggi (Max)",
            "Harga Rata-Rata (Mean Rp)",
            "Harga (FMV Rp)",
            "Metode Kalkulasi FMV"
        ]
        self.assertEqual(headers, expected_new_headers)

        # Periksa rumus pada baris 2, 273, 500, 1000
        for r in [2, 273, 500, 1000]:
            f_count = ws.cell(r, 8).value
            f_min = ws.cell(r, 9).value
            f_max = ws.cell(r, 10).value
            f_mean = ws.cell(r, 11).value
            f_fmv = ws.cell(r, 12).value
            f_method = ws.cell(r, 13).value

            self.assertTrue(str(f_count).startswith("=SUMIFS('Matriks FMV (Model & Tahun)'!$E$2:$E$"), f"Rumus COUNT salah pada baris {r}: {f_count}")
            self.assertTrue(str(f_min).startswith(f"=IF(H{r}>0, SUMIFS('Matriks FMV (Model & Tahun)'!$F$2:$F$"), f"Rumus MIN salah pada baris {r}: {f_min}")
            self.assertTrue(str(f_max).startswith(f"=IF(H{r}>0, SUMIFS('Matriks FMV (Model & Tahun)'!$J$2:$J$"), f"Rumus MAX salah pada baris {r}: {f_max}")
            self.assertTrue(str(f_mean).startswith(f"=IF(H{r}>0, SUMIFS('Matriks FMV (Model & Tahun)'!$K$2:$K$"), f"Rumus MEAN salah pada baris {r}: {f_mean}")
            self.assertTrue(str(f_fmv).startswith(f"=IF(H{r}>0, SUMIFS('Matriks FMV (Model & Tahun)'!$H$2:$H$"), f"Rumus FMV salah pada baris {r}: {f_fmv}")
            self.assertTrue(str(f_method).startswith(f"=IF(H{r}>0,"), f"Rumus Metode FMV salah pada baris {r}: {f_method}")


if __name__ == "__main__":
    unittest.main()
