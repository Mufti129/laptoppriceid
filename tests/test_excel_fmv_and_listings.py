import unittest
from pathlib import Path
import openpyxl

ROOT_DIR = Path(__file__).resolve().parent.parent
EXCEL_PRIMARY = Path("/Users/macbookair/Downloads/pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx")
EXCEL_EXPORT = ROOT_DIR / "exports" / "pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx"


class TestExcelFmvAndListings(unittest.TestCase):
    """Pengujian integritas berkas Excel dengan sheet 'list harga tarikan' dan rumus FMV berbasis tahun rilis."""

    @classmethod
    def setUpClass(cls):
        cls.excel_path = EXCEL_PRIMARY if EXCEL_PRIMARY.exists() else EXCEL_EXPORT
        cls.wb = openpyxl.load_workbook(cls.excel_path, data_only=False)

    def test_workbook_sheets_exist(self):
        """Verifikasi bahwa sheet baru 'list harga tarikan' dan sheet eksisting lengkap."""
        expected_sheets = [
            "Ringkasan & Analisis",
            "Pemetaan Lengkap (713 Tipe)",
            "Tipe Belum Ada (Flag Y)",
            "Katalog Seri LaptopMedia",
            "list harga tarikan"
        ]
        for s in expected_sheets:
            self.assertIn(s, self.wb.sheetnames, f"Sheet '{s}' harus ada di workbook.")

    def test_list_harga_tarikan_integrity(self):
        """Verifikasi bahwa sheet 'list harga tarikan' memuat ribuan listing riil terverifikasi dengan parameter tahun rilis."""
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

        # Cek sampel baris data
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

    def test_katalog_seri_laptopmedia_fmv_formulas(self):
        """Verifikasi penambahan kolom FMV dan keabsahan rumus kriteria ganda (Model + Tahun) di sheet 'Katalog Seri LaptopMedia'."""
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

        # Periksa rumus kriteria ganda pada baris 2, 10, 100, 500
        for r in [2, 10, 100, 500, 1000]:
            f_count = ws.cell(r, 8).value
            f_min = ws.cell(r, 9).value
            f_max = ws.cell(r, 10).value
            f_mean = ws.cell(r, 11).value
            f_fmv = ws.cell(r, 12).value
            f_method = ws.cell(r, 13).value

            self.assertTrue(str(f_count).startswith("=COUNTIFS('list harga tarikan'!$D$2:$D$"), f"Rumus COUNTIFS salah pada baris {r}: {f_count}")
            self.assertIn(f"'list harga tarikan'!$E$2:$E$", str(f_count), f"Parameter Tahun hilang dari COUNTIFS pada baris {r}: {f_count}")
            self.assertTrue(str(f_min).startswith(f"=IF(H{r}>0, MINIFS('list harga tarikan'!$H$2:$H$"), f"Rumus MINIFS salah pada baris {r}: {f_min}")
            self.assertTrue(str(f_max).startswith(f"=IF(H{r}>0, MAXIFS('list harga tarikan'!$H$2:$H$"), f"Rumus MAXIFS salah pada baris {r}: {f_max}")
            self.assertTrue(str(f_mean).startswith(f"=IF(H{r}>0, ROUND(AVERAGEIFS('list harga tarikan'!$H$2:$H$"), f"Rumus AVERAGEIFS salah pada baris {r}: {f_mean}")
            self.assertTrue(str(f_fmv).startswith(f"=IF(H{r}>0, ROUND(MEDIAN(IF(('list harga tarikan'!$D$2:$D$"), f"Rumus MEDIAN IF salah pada baris {r}: {f_fmv}")
            self.assertIn(f"('list harga tarikan'!$E$2:$E$", str(f_fmv), f"Parameter Tahun hilang dari MEDIAN IF pada baris {r}: {f_fmv}")
            self.assertTrue(str(f_method).startswith(f"=IF(H{r}>0,"), f"Rumus Metode FMV salah pada baris {r}: {f_method}")


if __name__ == "__main__":
    unittest.main()
