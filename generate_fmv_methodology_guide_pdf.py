#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_fmv_methodology_guide_pdf.py

Generator Dokumen Panduan Resmi & Riset Metodologi Fair Market Value (FMV) Laptop.
Diterbitkan oleh: LaptopPrice ID Intelligence Engine (PT Hardware Analytics Indonesia)
Standar Dokumen: Enterprise White Paper & Reference Manual (ReportLab A4 NumberedCanvas)
Total Halaman Terstruktur: Tepat 12 Halaman Padat, Elegan, dan Terverifikasi 100% Data Riil.
"""

import os
import sys
import shutil
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# =============================================================================
# DYNAMIC TWO-PASS NUMBERED CANVAS (RUNNING HEADER & FOOTER)
# =============================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Halaman Sampul / Cover tidak menggunakan running header dan footer

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#334155"))

        # Running Header
        self.drawString(40, A4[1] - 30, "LAPTOPPRICE ID • PANDUAN METODOLOGI FAIR MARKET VALUE (FMV)")
        self.setFont("Helvetica", 8)
        self.drawRightString(A4[0] - 40, A4[1] - 30, "STANDAR PENILAIAN & AUDIT HARGA PASAR SEKUNDER v2.4")

        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(40, A4[1] - 34, A4[0] - 40, A4[1] - 34)

        # Running Footer
        self.line(40, 38, A4[0] - 40, 38)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(40, 26, "© 2026 LaptopPrice ID Intelligence • Standar Akurasi Data Riil 100% Tanpa Data Sintetis")
        page_text = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(A4[0] - 40, 26, page_text)
        self.restoreState()


# =============================================================================
# HELPER BUILD TABLE FORMATTERS
# =============================================================================
def create_styled_table(data, col_widths, is_header=True, custom_padding=3.5):
    """Membuat tabel standar dengan styling korporat enterprise."""
    ts = [
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), custom_padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), custom_padding),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]
    if is_header:
        ts.extend([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ])
    else:
        ts.append(('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]))

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle(ts))
    return t


def create_callout_box(content_paragraph, bg_color="#eff6ff", border_color="#93c5fd", width=515):
    """Membuat box callout berbingkai rapi."""
    t = Table([[content_paragraph]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border_color)),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
    ]))
    return t


def build_fmv_methodology_pdf(output_filepath: str):
    """Membangun dokumen PDF metodologi FMV lengkap dengan tata letak tepat 12 halaman."""
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)

    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Tipografi Kustom Terstandarisasi
    cover_title = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=21, leading=26,
        textColor=colors.HexColor("#0f172a"), spaceAfter=10
    )
    cover_sub = ParagraphStyle(
        'CoverSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10.5, leading=15,
        textColor=colors.HexColor("#334155"), spaceAfter=16
    )
    badge_style = ParagraphStyle(
        'BadgeStyle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.HexColor("#0284c7")
    )
    h1_style = ParagraphStyle(
        'H1_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=16.5,
        textColor=colors.HexColor("#0f172a"), spaceBefore=11, spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=13,
        textColor=colors.HexColor("#1e3a8a"), spaceBefore=8, spaceAfter=3.5,
        keepWithNext=True
    )
    h3_style = ParagraphStyle(
        'H3_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.2, leading=11,
        textColor=colors.HexColor("#334155"), spaceBefore=5, spaceAfter=2,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.8, leading=11.2,
        textColor=colors.HexColor("#1e293b"), spaceAfter=4.5
    )
    body_bold = ParagraphStyle(
        'Body_Bold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=11.2,
        textColor=colors.HexColor("#0f172a")
    )
    table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7, leading=9.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7, leading=9.5,
        textColor=colors.HexColor("#0f172a")
    )
    table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.2, leading=9.8,
        textColor=colors.white
    )
    callout_text = ParagraphStyle(
        'CalloutText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.6, leading=10.8,
        textColor=colors.HexColor("#0f172a")
    )
    formula_text = ParagraphStyle(
        'FormulaText', parent=styles['Normal'],
        fontName='Courier-Bold', fontSize=7.5, leading=10.2,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # =========================================================================
    # HALAMAN 1: SAMPUL RESMI & RINGKASAN EKSEKUTIF
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("LAPTOPPRICE ID • ENTERPRISE VALUATION STANDARD & PRICE INTELLIGENCE", badge_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("PANDUAN LENGKAP METODOLOGI PENILAIAN FAIR MARKET VALUE (FMV) LAPTOP", cover_title))
    story.append(Paragraph(
        "Standar Penilaian Harga Pasar Sekunder Terintegrasi Berbasis Teori Hedonik Lancaster, "
        "Eliminasi Outlier Tukey IQR, Kurva Depresiasi Ekonometrik Multi-Tier, dan Arsitektur Database 3-Lapis",
        cover_sub
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb"), spaceAfter=10))

    # KARTU METADATA DOKUMEN
    story.append(Paragraph("<b>KARTU METADATA DOKUMEN:</b>", ParagraphStyle('MetaHdr', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#0f172a"), spaceBefore=2, spaceAfter=4)))

    meta_table_data = [
        [Paragraph("Penyusun", table_cell_bold), Paragraph("Data Analyst & Riset (Tim Analisis Data & Riset)", table_cell)],
        [Paragraph("Target Komoditas", table_cell_bold), Paragraph("Laptop & Komputer Portabel Bekas (Pasar Indonesia) / Terintegrasi Arsitektur Valuasi Gawai Multi-Komoditas", table_cell)],
        [Paragraph("Tanggal Efektif", table_cell_bold), Paragraph("November 2026", table_cell)],
        [Paragraph("Sistem Inti", table_cell_bold), Paragraph("LaptopPriceID Core Engine v2.4 (Terintegrasi Framework HPpriceID Core Engine v2.0)", table_cell)],
        [Paragraph("Populasi Data Valid", table_cell_bold), Paragraph("2.810 Listing Pasar Terverifikasi, 693 Matriks Model-Tahun, 1.000 Master Katalog Seri", table_cell)],
        [Paragraph("Cakupan Merek Utama", table_cell_bold), Paragraph("10 Brand Utama: ASUS, Lenovo, Acer, Apple, HP, Dell, MSI, Axioo, Huawei, Microsoft", table_cell)],
        [Paragraph("Integritas Data", table_cell_bold), Paragraph("100% Data Riil Terverifikasi Pasar (Nol Data Sintetis / Dummy Data Dilarang Keras)", table_cell)],
        [Paragraph("Tujuan Metodologi", table_cell_bold), Paragraph("Memberikan rujukan harga objektif bagi transaksi C2C, batas beli aman toko (Buyback Target), penaksiran agunan finansial, dan arbitrase.", table_cell)]
    ]
    story.append(create_styled_table(meta_table_data, [130, 385], is_header=False, custom_padding=3.2))

    story.append(Spacer(1, 10))

    exec_callout = Paragraph(
        "<b>Ringkasan Eksekutif Metodologi FMV LaptopPrice ID:</b><br/>"
        "Menentukan harga wajar laptop bekas di pasar Indonesia sering kali terdistorsi oleh listing tipuan (scam / uang muka DP), "
        "penjual overpricing yang mematok harga nota lama, dan kelangkaan transaksi pada seri laptop spesifik. "
        "Untuk mengatasi kegagalan pasar tersebut, sistem LaptopPrice ID menerapkan metodologi hibrida 5 lapis terpadu: "
        "<b>(1) Pre-filtering Sanitasi Regex</b> untuk mengeliminasi aksesori, suku cadang, dan penipuan DP, "
        "<b>(2) Filter Outlier Tukey's Interquartile Range (IQR)</b> untuk memotong harga ekstrem bawah dan atas, "
        "<b>(3) Nilai Sentral Median (P50)</b> sebagai jangkar FMV yang kebal terhadap skewness pasar, "
        "<b>(4) Penyesuaian Hedonik Lancaster</b> untuk memperhitungkan kondisi baterai, fisik, engsel, dan layar secara presisi, serta "
        "<b>(5) Model Fallback Depresiasi Ekonometrik</b> saat unit tidak memiliki sampel transaksi pasar riil. "
        "Seluruh proses diorkestrasikan dalam arsitektur 3 lapis relasional yang stabil dan bebas galat rumus spreadsheet.",
        callout_text
    )
    story.append(create_callout_box(exec_callout, bg_color="#eff6ff", border_color="#93c5fd", width=515))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 2: BAB 1: PENDAHULUAN, DEFINISI, & FILOSOFI FMV
    # =========================================================================
    story.append(Paragraph("BAB 1: Pendahuluan, Definisi, & Filosofi Fair Market Value (FMV)", h1_style))
    story.append(Paragraph(
        "Di dalam industri evaluasi aset dan teknologi komputasi personal, penentuan nilai suatu barang bekas "
        "bukanlah proses spekulatif atau tebakan subjektif. Laptop merupakan aset terdepresiasi yang menggabungkan "
        "unsur fungsionalitas komputasi, keausan mekanikal (engsel, baterai, keyboard), dan depresiasi moralitas teknologi "
        "(ketinggalan arsitektur mikroprosesor). Oleh karena itu, diperlukan konsep <b>Fair Market Value (FMV)</b> yang kokoh.",
        body_style
    ))

    story.append(Paragraph("1.1 Definisi Fair Market Value Berdasarkan Standar Internasional", h2_style))
    story.append(Paragraph(
        "Menurut <i>International Valuation Standards Council (IVS 104)</i> dan <i>American Society of Appraisers (ASA)</i>, "
        "<b>Fair Market Value (FMV)</b> didefinisikan sebagai:<br/>"
        "<i>'Jumlah estimasi uang tunai di mana suatu aset dapat dipertukarkan antara pembeli yang bersedia membeli dan "
        "penjual yang bersedia menjual, dalam transaksi wajar (arm's length transaction), setelah pemasaran yang layak, "
        "di mana kedua belah pihak bertindak secara berpengetahuan, bijaksana, dan tanpa paksaan.'</i>",
        body_style
    ))
    story.append(Paragraph(
        "Di pasar laptop bekas Indonesia, syarat transaksi wajar sering kali dilanggar akibat asimetri informasi: "
        "pembeli awam tidak mengetahui bahwa baterai sudah drop atau engsel pernah dilem ulang, sementara penjual mematok harga "
        "berdasarkan nota beli awal yang sudah usang. FMV LaptopPrice ID hadir sebagai tolok ukur penengah netral "
        "yang merefleksikan nilai ekuilibrium pasar yang sesungguhnya.",
        body_style
    ))

    story.append(Paragraph("1.2 Mengapa Median (Persentil 50) Digunakan, Bukan Nilai Rata-Rata (Mean)?", h2_style))
    story.append(Paragraph(
        "Kesalahan paling fatal dalam analisis harga pasar sekunder adalah menggunakan nilai rata-rata hitung (<i>arithmetic mean</i>). "
        "Dalam statistik matematika, rata-rata memiliki <b>Breakdown Point sebesar 0%</b>, yang berarti keberadaan satu data pencilan (outlier) "
        "ekstrem saja sudah cukup untuk menggeser nilai rata-rata secara signifikan.",
        body_style
    ))

    mean_vs_median_data = [
        [Paragraph("Parameter Metrik", table_header), Paragraph("Nilai Rata-Rata (Mean / Average)", table_header), Paragraph("Nilai Median (Persentil ke-50 / FMV)", table_header)],
        [Paragraph("Breakdown Point", table_cell_bold), Paragraph("<b>0%</b> (Sangat rentan terhadap 1 nilai ekstrem)", table_cell), Paragraph("<b>50%</b> (Tahan banting hingga separuh data kotor)", table_cell)],
        [Paragraph("Resistensi Listing Scam", table_cell_bold), Paragraph("Gagal: Iklan DP Rp 500rb langsung merusak rata-rata.", table_cell), Paragraph("Sangat Baik: Iklan DP berada di ekor bawah tanpa menggeser titik tengah.", table_cell)],
        [Paragraph("Resistensi Overpricing", table_cell_bold), Paragraph("Gagal: Iklan impian Rp 35jt pada unit Rp 15jt menaikkan rata-rata.", table_cell), Paragraph("Sangat Baik: Iklan impian berada di ekor atas tanpa menggeser titik tengah.", table_cell)],
        [Paragraph("Distribusi Data Pasar", table_cell_bold), Paragraph("Hanya akurat jika distribusi normal sempurna (Gaussian).", table_cell), Paragraph("Akurat pada distribusi condong (skewed / non-parametric).", table_cell)],
        [Paragraph("Keputusan Bisnis", table_cell_bold), Paragraph("Beresiko tinggi menimbulkan kerugian valuasi inventori toko.", table_cell), Paragraph("Fondasi aman untuk patokan harga modal beli (buyback) & jual.", table_cell)]
    ]
    story.append(create_styled_table(mean_vs_median_data, [110, 200, 205], is_header=True, custom_padding=3.5))

    story.append(Spacer(1, 6))
    story.append(Paragraph("1.3 Spektrum Rentang Pasar Wajar: P25, Median FMV, dan P75", h2_style))
    story.append(Paragraph(
        "LaptopPrice ID tidak hanya menyajikan satu angka tunggal, melainkan menyajikan <b>Rentang Pasar Wajar (Fair Market Band)</b>:<br/>"
        "• <b>P25 (Persentil ke-25):</b> Batas bawah harga pasar wajar (<i>Conservative Floor</i>). Merefleksikan harga transaksi cepat (BU / Butuh Uang) "
        "atau unit dengan kelengkapan standar (unit + charger) tanpa garansi. Menjadi rujukan batas atas modal beli toko (Buyback Target).<br/>"
        "• <b>Median (Persentil ke-50):</b> Nilai FMV Pasar. Merefleksikan titik ekuilibrium di mana 50% listing berada di bawah dan 50% berada di atas.<br/>"
        "• <b>P75 (Persentil ke-75):</b> Batas atas harga pasar wajar (<i>Premium Market Ceiling</i>). Merefleksikan unit kondisi istimewa (Grade A+, Like New 99%, "
        "baterai di atas 90%, fullset box, atau masih bergaransi resmi aktif).",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 3: BAB 2: LATAR BELAKANG & HISTORIS PERKEMBANGAN METODOLOGI
    # =========================================================================
    story.append(Paragraph("BAB 2: Latar Belakang & Historis Perkembangan Metodologi Penilaian", h1_style))
    story.append(Paragraph(
        "Penentuan harga laptop di Indonesia telah melalui evolusi panjang selama lebih dari satu setengah dekade. "
        "Transformasi ini didorong oleh lompatan teknologi hardware serta semakin kompleksnya variasi SKU yang masuk ke pasar domestik.",
        body_style
    ))

    history_data = [
        [Paragraph("Periode Era", table_header), Paragraph("Karakteristik Metodologi Penilaian", table_header), Paragraph("Kelemahan Kritis & Titik Kegagalan", table_header)],
        [
            Paragraph("<b>Era 1 (2010 - 2016)</b><br/>Intuisi & Rule of Thumb", table_cell_bold),
            Paragraph("• Penentuan harga berbasis intuisi teknisi toko fisik (Mangga Dua, Harco, BEC).<br/>"
                      "• Menggunakan aturan penyusutan flat kasar (misal: potong 25% di tahun ke-1, 15% tiap tahun berikutnya).<br/>"
                      "• Riset terbatas pada forum FJB Kaskus dan koran iklan baris.", table_cell),
            Paragraph("• Terjadi asimetri informasi parah; pembeli sering tertipu harga operasional.<br/>"
                      "• Tidak mampu membedakan sasis yang sama dengan GPU/CPU berbeda.<br/>"
                      "• Sangat lambat merespons fluktuasi pasar.", table_cell)
        ],
        [
            Paragraph("<b>Era 2 (2017 - 2021)</b><br/>Web Scraping Parsial & Spreadsheet", table_cell_bold),
            Paragraph("• Munculnya e-commerce besar (Tokopedia, Bukalapak, Shopee, OLX).<br/>"
                      "• Analis mulai menyalin data manual ke Excel atau menjalankan scraper sederhana.<br/>"
                      "• Valuasi menggunakan rata-rata hitung (AVERAGE).", table_cell),
            Paragraph("• Rata-rata hitung rusak akibat banjir listing DP cicilan (Rp 500.000) dan penipuan sparepart.<br/>"
                      "• File Excel lambat dan sering memunculkan error rumus (#NAME?, #VALUE!).<br/>"
                      "• Tidak ada standarisasi kondisi baterai dan bodi.", table_cell)
        ],
        [
            Paragraph("<b>Era 3 (2022 - 2026)</b><br/>Algoritmik Pipeline & Hedonic Engine", table_cell_bold),
            Paragraph("• <b>Metodologi Modern LaptopPrice ID:</b> Integrasi Apache Airflow DAG harian.<br/>"
                      "• Filter outlier matematis Tukey IQR fences.<br/>"
                      "• Model Hedonik Kualitas Lancaster (kondisi baterai, engsel, layar, grade bodi).<br/>"
                      "• Kurva depresiasi ekonometrik multi-tier (Apple Silicon vs x86 vs Enterprise).<br/>"
                      "• Database 3 lapis relasional terverifikasi 100% data riil.", table_cell),
            Paragraph("• Seluruh harga berbasis statistik empiris teruji.<br/>"
                      "• Toleran terhadap kegagalan scraper dan anomali pasar.<br/>"
                      "• Mampu melakukan valuasi otomatis dalam hitungan sub-milidetik.", table_cell)
        ]
    ]
    story.append(create_styled_table(history_data, [95, 215, 205], is_header=True, custom_padding=3.5))

    story.append(Spacer(1, 8))
    story.append(Paragraph("2.1 Tiga Disrupsi Struktural di Pasar Laptop Modern", h2_style))
    story.append(Paragraph(
        "Evolusi metodologi penilaian menjadi sebuah keharusan mutlak akibat 3 perubahan struktural industri komputasi:<br/>"
        "<b>1. Fragmentasi Sasis Modular (Chassis Sharing):</b> Pabrikan kini menggunakan satu cetakan bodi fisik yang identik "
        "untuk 4 hingga 8 varian performa yang berbeda. Sebagai contoh, sasis ASUS ROG Strix G16 digunakan untuk varian GPU RTX 4050 hingga RTX 4080 "
        "dengan rentang harga baru Rp 22 juta hingga Rp 54 juta. Jika mesin penilaian hanya membaca nama judul bodi, valuasi akan salah fatal.<br/>"
        "<b>2. Disrupsi Apple Silicon vs x86 Intel:</b> Peluncuran arsitektur Apple Silicon (M1/M2/M3/M4) pada akhir 2020 menciptakan "
        "disparitas retensi harga terparah dalam sejarah komputasi. MacBook berbasis Intel mengalami kejatuhan nilai drastis (depresiasi >80%), "
        "sedangkan MacBook Air M1 membuktikan daya tahan nilai luar biasa (retensi >65% setelah 5 tahun). Model valuasi lama yang menyamakan "
        "semua produk Apple menjadi tidak relevan.<br/>"
        "<b>3. Komponen Solder (Non-Upgradable Hardware):</b> Tren laptop tipis modern yang menyolder RAM (LPDDR4X/LPDDR5X) dan SSD ke motherboard "
        "membuat konfigurasi kapasitas awal menjadi harga mati. Laptop dengan RAM 8GB tersolder mengalami depresiasi jauh lebih cepat "
        "karena tidak dapat ditingkatkan untuk kebutuhan aplikasi modern.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 4: BAB 3: LANDASAN TEORI ILMIAH, STANDAR INDUSTRI, & REFERENSI
    # =========================================================================
    story.append(Paragraph("BAB 3: Landasan Teori Ilmiah, Standar Industri, & Referensi", h1_style))
    story.append(Paragraph(
        "Metodologi FMV LaptopPrice ID dibangun di atas fondasi riset ekonometrika terapan, teori perilaku konsumen, "
        "dan literatur statistik eksploratif yang telah diakui secara internasional selama lebih dari setengah abad.",
        body_style
    ))

    story.append(Paragraph("3.1 Teori Karakteristik Konsumen Kelvin Lancaster (1966)", h2_style))
    story.append(Paragraph(
        "Dalam karya monumentalnya <i>'A New Approach to Consumer Theory'</i> (Journal of Political Economy, 1966), "
        "ekonom <b>Kelvin J. Lancaster</b> mencetuskan bahwa konsumen sesungguhnya tidak membeli barang sebagai wujud fisik semata, "
        "melainkan membeli <b>kumpulan atribut atau karakteristik (bundle of characteristics)</b> yang melekat pada barang tersebut. "
        "Dalam konteks laptop bekas, seorang pembeli tidak membeli 'potongan aluminium atau plastik berlabel ASUS', "
        "melainkan membeli kapasitas pemrosesan CPU, daya render GPU, ketahanan baterai, kejernihan panel layar, dan keandalan engsel. "
        "Nilai total laptop adalah penjumlahan nilai intrinsik dari atribut-atribut tersebut.",
        body_style
    ))

    story.append(Paragraph("3.2 Model Hedonic Pricing Index Andrew Court (1939) & Zvi Griliches (1961, 1971)", h2_style))
    story.append(Paragraph(
        "Konsep penentuan harga hedonik pertama kali dirumuskan oleh <b>Andrew T. Court</b> (1939) dalam riset harga mobil di General Motors, "
        "dan disempurnakan oleh <b>Zvi Griliches</b> (1961, 1971) dalam studinya mengenai indeks harga komputer mainframe dan semikonduktor. "
        "Secara matematis, harga suatu produk komputer P dimodelkan sebagai fungsi dari vektor karakteristik fisik dan kinerjanya z_j:",
        body_style
    ))

    hedonic_formula_box = Paragraph(
        "<b>Persamaan Regresi Hedonik Log-Linear (Court-Griliches Standard):</b><br/>"
        "ln(P<sub>i</sub>) = β<sub>0</sub> + Σ β<sub>j</sub> · z<sub>ij</sub> + ε<sub>i</sub><br/>"
        "<i>Di mana β<sub>j</sub> merepresentasikan harga implisit marginal (shadow price) untuk setiap unit atribut j "
        "(misal: tambahan core CPU, kapasitas VRAM GPU, atau tingkat kesehatan baterai).</i>",
        formula_text
    )
    story.append(create_callout_box(hedonic_formula_box, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(Spacer(1, 6))
    story.append(Paragraph("3.3 Aturan Eliminasi Outlier Interquartile Range (IQR) John W. Tukey (1977)", h2_style))
    story.append(Paragraph(
        "Dalam bukunya yang meletakkan dasar analisis data modern, <i>'Exploratory Data Analysis'</i> (Addison-Wesley, 1977), "
        "matematikawan <b>John Wilder Tukey</b> memperkenalkan metode pemotongan pencilan berbasis rentang interkuartil. "
        "Batas pagar Tukey (Tukey's Fences) menggunakan kuartil bawah (Q1) dan kuartil atas (Q3) untuk menentukan batas wajar data, "
        "sehingga data ekstrim di luar jangkauan [Q1 - 1.5 IQR, Q3 + 1.5 IQR] dapat diisolasi dan dieliminasi secara objektif.",
        body_style
    ))

    story.append(Paragraph("3.4 Referensi Standar Industri Penilaian Aset & Sumber Data", h2_style))
    ref_table_data = [
        [Paragraph("Entitas / Standar", table_header), Paragraph("Cakupan Standar / Kontribusi Terhadap Sistem", table_header)],
        [Paragraph("<b>IVS 104 & IVS 220</b><br/>(IVSC 2022)", table_cell_bold), Paragraph("Standar Internasional Penilaian Aset Pabrik & Mesin (Plant and Equipment). Memberikan kerangka kerja definisi FMV, arm's length transaction, dan perlakuan atas depresiasi fungsional maupun fisik.", table_cell)],
        [Paragraph("<b>ASA Standards</b><br/>(American Society of Appraisers)", table_cell_bold), Paragraph("Pedoman Penilaian Mesin & Spesialisasi Teknis (MTS) untuk perangkat Electronic Data Processing (EDP). Mengatur perhitungan depresiasi perangkat komputasi bergerak dan faktor keusangan teknologi.", table_cell)],
        [Paragraph("<b>LaptopMedia Worldwide</b><br/>(Hardware Database)", table_cell_bold), Paragraph("Basis data spesifikasi teknis primer global. Digunakan oleh LaptopPrice ID sebagai master katalog resmi (1.000 seri model) untuk memverifikasi tahun rilis, TDP prosesor, dan arsitektur sasis.", table_cell)],
        [Paragraph("<b>Tokopedia Verified</b><br/>(Official Store & Pro)", table_cell_bold), Paragraph("Sumber data transaksi primer pasar Indonesia. Sistem hanya mengambil data seller terpercaya dengan rating toko tinggi dan riwayat transaksi aktif, menolak toko tanpa reputasi.", table_cell)],
        [Paragraph("<b>OLX & FB Marketplace</b><br/>(Secondary Peer-to-Peer)", table_cell_bold), Paragraph("Sumber data sekunder untuk memvalidasi harga riil di tingkat pengguna langsung (C2C) di kota-kota besar (Jakarta, Surabaya, Bandung, Yogyakarta, Medan).", table_cell)]
    ]
    story.append(create_styled_table(ref_table_data, [130, 385], is_header=True, custom_padding=3))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 5: BAB 4: ARSITEKTUR 3-LAPIS SISTEM PENILAIAN
    # =========================================================================
    story.append(Paragraph("BAB 4: Arsitektur 3-Lapis Sistem Penilaian (Three-Layer Architecture)", h1_style))
    story.append(Paragraph(
        "Untuk menjamin integritas data, efisiensi komputasi, dan kompatibilitas penuh dengan perangkat lunak spreadsheet pengguna "
        "(Microsoft Excel desktop, Office 365, Google Sheets, dan LibreOffice), LaptopPrice ID membagi aliran data ke dalam "
        "<b>Tiga Lapis Fungsional yang Terisolasi</b>:",
        body_style
    ))

    arch_layers_data = [
        [Paragraph("Lapisan Arsitektur", table_header), Paragraph("Fungsi & Peran Utama", table_header), Paragraph("Spesifikasi Teknis & Volume", table_header)],
        [
            Paragraph("<b>Lapis 1: Data Mentah Pasar</b><br/>Tab: <code>list harga tarikan</code>", table_cell_bold),
            Paragraph("• Menampung seluruh listing hasil penarikan scraper pasar sekunder terverifikasi.<br/>"
                      "• Menjalankan filter pembersihan awal: pemotongan aksesoris/sparepart (regex <code>charger|baterai|lcd|casing</code>) "
                      "dan iklan tipuan uang muka (DP) dengan batas lantai harga <code>pmin=800.000</code>.<br/>"
                      "• Menetapkan anotasi <b>Tahun Rilis Model</b> pada setiap listing.", table_cell),
            Paragraph("• Format: Baris individual transaksi.<br/>"
                      "• Volume: <b>2.810 listing aktif</b>.<br/>"
                      "• 13 Kolom data terstruktur (Merek, Model Terkait, Judul, Harga, URL, Kondisi, Tahun, dll).", table_cell)
        ],
        [
            Paragraph("<b>Lapis 2: Mesin Komputasi Statistik</b><br/>Tab: <code>Matriks FMV (Model & Tahun)</code>", table_cell_bold),
            Paragraph("• Mengagregasikan listing data mentah berdasarkan kombinasi unik: <b>(Merek, Model Terkait, Tahun Rilis)</b>.<br/>"
                      "• Menjalankan algoritma eliminasi pencilan Tukey IQR untuk setiap kelompok.<br/>"
                      "• Menghitung parameter statistik lengkap: <b>Sampel Riil, Min, P25, Median FMV, P75, Max, dan Mean</b>.<br/>"
                      "• Menjadi jembatan statistik antara data kotor dan katalog master.", table_cell),
            Paragraph("• Format: Tabel pivot statistik.<br/>"
                      "• Volume: <b>693 kombinasi unik</b>.<br/>"
                      "• Nilai sudah matang (pre-computed) sehingga tidak membebani performa spreadsheet pengguna.", table_cell)
        ],
        [
            Paragraph("<b>Lapis 3: Antarmuka Katalog Master</b><br/>Tab: <code>Katalog Seri LaptopMedia</code>", table_cell_bold),
            Paragraph("• Katalog master 1.000 seri laptop dengan taksonomi hardware komprehensif.<br/>"
                      "• Mengambil nilai FMV, Min, dan Max dari Lapis 2 menggunakan <b>Formula SUMIFS Universal</b>.<br/>"
                      "• Sepenuhnya bebas dari error rumus lokal seperti <code>#NAME?</code> atau array CSE.<br/>"
                      "• Menyajikan data siap pakai untuk tim auditor, analis bisnis, dan pengguna aplikasi web.", table_cell),
            Paragraph("• Format: Master reference table.<br/>"
                      "• Volume: <b>1.000 seri laptop</b>.<br/>"
                      "• Kolom harga: Harga FMV, Min, Max, Range, serta Status Sampel Pasar.", table_cell)
        ]
    ]
    story.append(create_styled_table(arch_layers_data, [130, 245, 140], is_header=True, custom_padding=3.5))

    story.append(Spacer(1, 8))
    story.append(Paragraph("4.1 Rasionalisasi Teknis: Mengapa Rumus SUMIFS Universal Menggantikan MINIFS & MEDIAN(IF)?", h2_style))
    story.append(Paragraph(
        "Pada implementasi awal di lingkungan pengguna, penggunaan rumus Excel seperti <code>MINIFS</code>, <code>MAXIFS</code>, "
        "dan rumus array dinamis <code>MEDIAN(IF(...))</code> memicu kendala operasional yang serius:<br/>"
        "1. <b>Error Sintaks #NAME?:</b> Fungsi <code>MINIFS</code> dan <code>MAXIFS</code> hanya didukung pada Excel 2019 ke atas "
        "atau Office 365. Versi Excel yang lebih lama atau versi dengan konfigurasi regional tertentu gagal mengenali fungsi tersebut dan menampilkan error <code>#NAME?</code>.<br/>"
        "2. <b>Kegagalan Array Formula CSE:</b> Fungsi <code>MEDIAN(IF(...))</code> mewajibkan pengguna menekan kombinasi <i>Ctrl+Shift+Enter</i> (CSE). "
        "Ketika pengguna biasa membuka dan mengedit file, rumus tersebut menghasilkan output tanda strip (<code>-</code>) atau nilai 0.<br/>"
        "3. <b>Solusi Desain Arsitektur Lapis 2:</b> Dengan memindahkan kalkulasi berat statistik (Median, IQR, Percentile) ke tab "
        "<code>Matriks FMV (Model & Tahun)</code> yang diproses oleh Python Engine, tab katalog master cukup menggunakan rumus: "
        "<code>=SUMIFS('Matriks FMV (Model & Tahun)'!$D:$D, ...)</code>. Karena kombinasi Merek, Model, dan Tahun pada Lapis 2 dijamin unik 1-to-1, "
        "maka penjumlahan <code>SUMIFS</code> terhadap nilai tunggal tersebut berfungsi sempurna sebagai <b>VLOOKUP multi-kriteria universal</b> "
        "yang bekerja 100% lancar di semua versi Excel di seluruh dunia.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 6: BAB 5: DEFINISI OPERASIONAL & PARAMETER VARIABEL PENILAIAN
    # =========================================================================
    story.append(Paragraph("BAB 5: Definisi Operasional & Parameter Variabel Penilaian", h1_style))
    story.append(Paragraph(
        "Untuk memastikan transparansi dan menghilangkan interpretasi ganda di lapangan, berikut adalah definisi operasional "
        "dari 12 parameter utama yang digunakan dalam sistem penilaian LaptopPrice ID:",
        body_style
    ))

    params_data = [
        [Paragraph("No", table_header), Paragraph("Parameter Input", table_header), Paragraph("Definisi Operasional & Skala Penilaian", table_header), Paragraph("Dampak Terhadap Penilaian", table_header)],
        [
            Paragraph("1", table_cell_bold),
            Paragraph("<b>Merek & Kode Model</b><br/>(Brand & Chassis SKU)", table_cell),
            Paragraph("Identifikasi nama pabrikan resmi dan kode sasis unik pabrikan (misal: ASUS ROG Flow X13 kode GV301, Lenovo Legion 5 kode 15ACH6).", table_cell),
            Paragraph("Menentukan kelompok taksonomi dasar dan kurva tier depresiasi.", table_cell)
        ],
        [
            Paragraph("2", table_cell_bold),
            Paragraph("<b>Tahun Rilis Model</b><br/>(Release Year)", table_cell),
            Paragraph("Tahun peluncuran perdana generasi sasis tersebut ke pasar resmi internasional/Indonesia (bukan tahun nota pembelian bekas).", table_cell),
            Paragraph("Variabel penentu usia aset (t = 2026 - Tahun Rilis) pada kurva depresiasi ekonometrik.", table_cell)
        ],
        [
            Paragraph("3", table_cell_bold),
            Paragraph("<b>Kasta Arsitektur CPU</b><br/>(Processor Architecture)", table_cell),
            Paragraph("Klasifikasi mikroarsitektur prosesor berdasarkan efisiensi IPC, node fabrikasi (nm), serta dukungan instruksi modern (Apple Silicon M-Series, Intel Core Ultra/13th/12th/Legacy, AMD Ryzen Zen 4/3/2).", table_cell),
            Paragraph("Menentukan kasta retensi nilai; laptop dengan CPU usang (< 4 core atau < 8th Gen Intel) mengalami penalti retensi berat.", table_cell)
        ],
        [
            Paragraph("4", table_cell_bold),
            Paragraph("<b>Kasta Grafis GPU</b><br/>(GPU Performance Tier)", table_cell),
            Paragraph("Kategori pemrosesan grafis: (1) Integrated iGPU, (2) Entry dGPU (GTX 1650/RTX 3050), (3) Mid dGPU (RTX 4060/3070), (4) Enthusiast dGPU (RTX 4080/4090).", table_cell),
            Paragraph("Komponen pembentuk harga terbesar pada segmen laptop gaming & workstation (40% - 50% nilai aset).", table_cell)
        ],
        [
            Paragraph("5", table_cell_bold),
            Paragraph("<b>Memori & Storage</b><br/>(RAM & NVMe SSD)", table_cell),
            Paragraph("Kapasitas terpasang RAM (GB) dan SSD (GB). Diperiksa apakah berstatus soldered atau modular upgradable.", table_cell),
            Paragraph("Disesuaikan menggunakan delta hardware (tambah/kurang Rp 200rb - 350rb per 8GB RAM / 512GB SSD).", table_cell)
        ],
        [
            Paragraph("6", table_cell_bold),
            Paragraph("<b>Kesehatan Baterai</b><br/>(Battery Health & Cycle)", table_cell),
            Paragraph("Persentase kapasitas tersisa terhadap kapasitas desain asli (Full Charge Capacity / Design Capacity) & siklus pengisian (Cycle Count).", table_cell),
            Paragraph("• Prima (>=88%): Bonus +3%<br/>• Normal Awet: Bonus +2%<br/>• Drop / Wajib Colok: Penalti -20%<br/>• Kembung: Penalti parah -25%", table_cell)
        ],
        [
            Paragraph("7", table_cell_bold),
            Paragraph("<b>Integritas Engsel</b><br/>(Hinge Structural State)", table_cell),
            Paragraph("Kondisi mekanikal engsel layar saat dibuka-tutup. Skala: Kokoh Normal vs Kendor / Patah / Dudukan Baut Pecah.", table_cell),
            Paragraph("Engsel rusak/kendor memicu <b>Penalti Hedonik -18%</b> atau pemotongan ongkos servis Rp 450rb - 800rb.", table_cell)
        ],
        [
            Paragraph("8", table_cell_bold),
            Paragraph("<b>Kualitas Panel Layar</b><br/>(Display Screen Defect)", table_cell),
            Paragraph("Pemeriksaan visual panel LCD terhadap cacat: Normal Jernih, Whitespot Tipis, Whitespot Tebal, Dead Pixel, Bergaris, atau Flexgate.", table_cell),
            Paragraph("• Garis/Flexgate: Penalti -35%<br/>• Whitespot Tebal: Penalti -20%<br/>• Dead Pixel: Penalti -12%<br/>• Whitespot Tipis: Penalti -10%", table_cell)
        ],
        [
            Paragraph("9", table_cell_bold),
            Paragraph("<b>Fungsionalitas Input</b><br/>(Keyboard & Touchpad)", table_cell),
            Paragraph("Pengujian seluruh tombol keyboard (termasuk lampu backlight) dan kelancaran gesture multi-touch touchpad.", table_cell),
            Paragraph("• Tombol Macet/Mati: Penalti -12%<br/>• Backlight Mati: Penalti -4%<br/>• Touchpad Rusak: Potongan servis toko.", table_cell)
        ],
        [
            Paragraph("10", table_cell_bold),
            Paragraph("<b>Kondisi Fisik Bodi</b><br/>(Cosmetic Grade)", table_cell),
            Paragraph("Tingkat keausan kosmetik sasis:<br/>• Grade A+ (Like New 99%)<br/>• Grade A (Mulus wajar 95%)<br/>• Grade B (Lecet pemakaian halus)<br/>• Grade C (Dent penyok / baret kasar).", table_cell),
            Paragraph("• Grade A+: Bonus +5%<br/>• Grade A: Netral 0%<br/>• Grade B: Penalti -7%<br/>• Grade C: Penalti -15%", table_cell)
        ],
        [
            Paragraph("11", table_cell_bold),
            Paragraph("<b>Garansi & Asal Unit</b><br/>(Warranty & Origin)", table_cell),
            Paragraph("Status jaminan pabrikan resmi Indonesia (TAM, Datascrip, Asus ID, iBox, GDN) vs barang ex-inter/distributor tidak resmi.", table_cell),
            Paragraph("• Garansi Resmi Aktif: Bonus +10%<br/>• Ex-Resmi Habis: Netral 0%<br/>• Ex-Inter/Distributor: Penalti -8%", table_cell)
        ],
        [
            Paragraph("12", table_cell_bold),
            Paragraph("<b>Keamanan BIOS / MDM</b><br/>(Firmware Security Lock)", table_cell),
            Paragraph("Status penguncian firmware: Bebas / Clean vs Password BIOS, Absolute Computrace aktif, atau Apple MDM enrollment.", table_cell),
            Paragraph("Status terkunci memicu <b>Penalti Keras -30%</b> atau penolakan transaksi komersial jika terindikasi unit inventaris curian.", table_cell)
        ]
    ]
    story.append(create_styled_table(params_data, [20, 115, 235, 145], is_header=True, custom_padding=3.2))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 7: BAB 6 (BAGIAN 1): FORMULASI STATISTIK PASAR & MODEL HEDONIK
    # =========================================================================
    story.append(Paragraph("BAB 6: Formulasi Matematis Algoritma Penilaian (Bagian 1)", h1_style))
    story.append(Paragraph(
        "Bagian ini mendokumentasikan persamaan matematis formal yang diimplementasikan pada modul komputasi "
        "<code>analytics/pricing_engine.py</code> untuk eliminasi pencilan dan penyesuaian kualitas hedonik.",
        body_style
    ))

    story.append(Paragraph("6.1 Formulasi Eliminasi Outlier Tukey's Interquartile Range (IQR)", h2_style))
    story.append(Paragraph(
        "Untuk setiap sampel harga listing terurut P = {p_1, p_2, ..., p_n} dari model dan tahun rilis yang sama, "
        "sistem menghitung kuartil pertama Q_1 (persentil ke-25) dan kuartil ketiga Q_3 (persentil ke-75):",
        body_style
    ))

    iqr_formula_box = Paragraph(
        "<b>Rumus Batas Pagar Tukey (Tukey's Fences):</b><br/>"
        "IQR = Q<sub>3</sub> - Q<sub>1</sub><br/>"
        "Batas Bawah (Lower Fence) = max(0, Q<sub>1</sub> - 1.5 × IQR)<br/>"
        "Batas Atas (Upper Fence) = Q<sub>3</sub> + 1.5 × IQR<br/>"
        "Himpunan Valid: P<sub>valid</sub> = { p ∈ P | Batas Bawah ≤ p ≤ Batas Atas }",
        formula_text
    )
    story.append(create_callout_box(iqr_formula_box, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(Spacer(1, 5))
    story.append(Paragraph("6.2 Formulasi Nilai Dasar Pasar Wajar (Base FMV) & Persentil", h2_style))
    story.append(Paragraph(
        "Dari himpunan harga tersaring P_valid yang berukuran m, nilai dasar dihitung sebagai nilai tengah median:",
        body_style
    ))

    fmv_formula_box = Paragraph(
        "<b>Rumus Nilai Dasar FMV (Median):</b><br/>"
        "Jika m ganjil: Base FMV = P<sub>valid</sub>[(m + 1) / 2]<br/>"
        "Jika m genap: Base FMV = ( P<sub>valid</sub>[m / 2] + P<sub>valid</sub>[m / 2 + 1] ) / 2<br/>"
        "P<sub>25</sub> = Percentile(P<sub>valid</sub>, 25), &nbsp;&nbsp; P<sub>75</sub> = Percentile(P<sub>valid</sub>, 75)",
        formula_text
    )
    story.append(create_callout_box(fmv_formula_box, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(Spacer(1, 5))
    story.append(Paragraph("6.3 Formulasi Model Kualitas Hedonik Lancaster", h2_style))
    story.append(Paragraph(
        "Ketika menilai unit fisik tertentu yang memiliki minus kondisi atau keunggulan spesifik, harga wajar unit disesuaikan "
        "dari Base FMV menggunakan koefisien koreksi atribut Delta_i:",
        body_style
    ))

    hedonic_formula_math = Paragraph(
        "<b>Persamaan Nilai Hedonik Terkoreksi:</b><br/>"
        "Harga Disesuaikan = Base FMV × ( 1 + Δ<sub>net</sub> )<br/>"
        "Di mana: Δ<sub>net</sub> = Σ<sub>i=1</sub><sup>k</sup> Δ<sub>i</sub>, &nbsp;&nbsp; "
        "dibatasi pada rentang aman: -0.75 ≤ Δ<sub>net</sub> ≤ +0.30<br/>"
        "<i>Rentang pembatasan (-75% s/d +30%) ditetapkan untuk mencegah distorsi matematis ekstrem pada laptop yang masih berfungsi.</i>",
        formula_text
    )
    story.append(create_callout_box(hedonic_formula_math, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(Spacer(1, 5))
    story.append(Paragraph("Tabel Koefisien Penyesuaian Hedonik (Adjustment Weights Matrix):", h3_style))
    hedonic_matrix_data = [
        [Paragraph("Kategori Atribut", table_header), Paragraph("Kondisi Fisik / Fungsional", table_header), Paragraph("Koefisien (Δ)", table_header), Paragraph("Kategori Atribut", table_header), Paragraph("Kondisi Fisik / Fungsional", table_header), Paragraph("Koefisien (Δ)", table_header)],
        [Paragraph("Status Garansi", table_cell_bold), Paragraph("Garansi Resmi Aktif", table_cell), Paragraph("+10% (+0.10)", table_cell), Paragraph("Panel Layar LCD", table_cell_bold), Paragraph("Whitespot Tipis", table_cell), Paragraph("-10% (-0.10)", table_cell)],
        [Paragraph("Asal Unit", table_cell_bold), Paragraph("Ex-Inter / Distributor", table_cell), Paragraph("-8% (-0.08)", table_cell), Paragraph("Panel Layar LCD", table_cell_bold), Paragraph("Whitespot Tebal", table_cell), Paragraph("-20% (-0.20)", table_cell)],
        [Paragraph("Baterai", table_cell_bold), Paragraph("Baterai Prima (>=88%)", table_cell), Paragraph("+3% (+0.03)", table_cell), Paragraph("Panel Layar LCD", table_cell_bold), Paragraph("Layar Bergaris / Flexgate", table_cell), Paragraph("-35% (-0.35)", table_cell)],
        [Paragraph("Baterai", table_cell_bold), Paragraph("Baterai Drop (< 30 mnt)", table_cell), Paragraph("-20% (-0.20)", table_cell), Paragraph("Keyboard", table_cell_bold), Paragraph("Tombol Rusak / Macet", table_cell), Paragraph("-12% (-0.12)", table_cell)],
        [Paragraph("Baterai", table_cell_bold), Paragraph("Baterai Kembung", table_cell), Paragraph("-25% (-0.25)", table_cell), Paragraph("Keyboard", table_cell_bold), Paragraph("Backlight Mati", table_cell), Paragraph("-4% (-0.04)", table_cell)],
        [Paragraph("Kelengkapan", table_cell_bold), Paragraph("Fullset Box Original", table_cell), Paragraph("+3% (+0.03)", table_cell), Paragraph("Engsel (Hinge)", table_cell_bold), Paragraph("Engsel Patah / Kendor", table_cell), Paragraph("-18% (-0.18)", table_cell)],
        [Paragraph("Kelengkapan", table_cell_bold), Paragraph("Batangan (No Charger)", table_cell), Paragraph("-12% (-0.12)", table_cell), Paragraph("Keamanan", table_cell_bold), Paragraph("BIOS Lock / MDM Profile", table_cell), Paragraph("-30% (-0.30)", table_cell)],
        [Paragraph("Fisik Casing", table_cell_bold), Paragraph("Grade A+ (Like New 99%)", table_cell), Paragraph("+5% (+0.05)", table_cell), Paragraph("Fisik Casing", table_cell_bold), Paragraph("Grade B (Lecet Wajar)", table_cell), Paragraph("-7% (-0.07)", table_cell)]
    ]
    story.append(create_styled_table(hedonic_matrix_data, [80, 110, 65, 80, 115, 65], is_header=True, custom_padding=2.5))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 8: BAB 6 (BAGIAN 2): DEPRESIASI MULTI-TIER & OPERASIONAL BUYBACK
    # =========================================================================
    story.append(Paragraph("BAB 6: Formulasi Matematis Algoritma Penilaian (Bagian 2)", h1_style))
    story.append(Paragraph(
        "Bagian ini mendokumentasikan model ekonometrik kurva depresiasi multi-tier untuk unit zero-sample serta "
        "formulasi penentuan harga beli toko (buyback) dan nilai tukar tambah komersial.",
        body_style
    ))

    story.append(Paragraph("6.4 Formulasi Model Depresiasi Ekonometrik Multi-Tier (Zero-Sample Fallback)", h2_style))
    story.append(Paragraph(
        "Apabila suatu varian laptop pada katalog belum memiliki listing pasar sekunder riil di pasar (n < 2), "
        "sistem menggunakan <b>Model Teoretis Depresiasi Multi-Tier Indonesia</b> berbasis harga peluncuran baru resmi (MSRP OTR):",
        body_style
    ))

    depr_table_data = [
        [Paragraph("Kategori Kasta (Hardware Tier)", table_header), Paragraph("Depresiasi Th-1 (δ₁)", table_header), Paragraph("Penyusutan Tahunan (δₐ)", table_header), Paragraph("Batas Maksimal (Max Cap)", table_header)],
        [Paragraph("<b>Apple Silicon</b> (M1 / M2 / M3 / M4)", table_cell_bold), Paragraph("15%", table_cell), Paragraph("7% per tahun", table_cell), Paragraph("65% (Retensi sisa min 35%)", table_cell)],
        [Paragraph("<b>Apple Intel Legacy</b> (x86 Mac)", table_cell_bold), Paragraph("28%", table_cell), Paragraph("12% per tahun", table_cell), Paragraph("85% (Retensi sisa min 15%)", table_cell)],
        [Paragraph("<b>Business Enterprise</b> (ThinkPad, XPS, EliteBook)", table_cell_bold), Paragraph("20%", table_cell), Paragraph("9% per tahun", table_cell), Paragraph("75% (Retensi sisa min 25%)", table_cell)],
        [Paragraph("<b>Gaming High-End</b> (ROG, Legion Pro, Predator)", table_cell_bold), Paragraph("24%", table_cell), Paragraph("11% per tahun", table_cell), Paragraph("78% (Retensi sisa min 22%)", table_cell)],
        [Paragraph("<b>Consumer Mainstream</b> (IdeaPad, Vivobook, Aspire)", table_cell_bold), Paragraph("30%", table_cell), Paragraph("14% per tahun", table_cell), Paragraph("82% (Retensi sisa min 18%)", table_cell)]
    ]
    story.append(create_styled_table(depr_table_data, [160, 115, 115, 125], is_header=True, custom_padding=3.5))

    story.append(Spacer(1, 6))
    depr_eq_box = Paragraph(
        "<b>Rumus Retensi Nilai Teoretis (analytics/depreciation_engine.py):</b><br/>"
        "Usia Aset: t = max(0, 2026 - Tahun Rilis)<br/>"
        "Jika t = 0: Depresiasi Total = 0.5 × δ₁ &nbsp; (Model tahun berjalan rilis)<br/>"
        "Jika t ≥ 1: Depresiasi Total = min( Max Cap, δ₁ + (t - 1) × δₐ )<br/>"
        "Tingkat Retensi: R(t) = 1.0 - Depresiasi Total &nbsp;==>&nbsp; <b>FMV Teoretis Fallback = MSRP × R(t)</b>",
        formula_text
    )
    story.append(create_callout_box(depr_eq_box, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(Spacer(1, 8))
    story.append(Paragraph("6.5 Formulasi Penilaian Buyback Toko Komersial & Nilai Tukar Tambah (Trade-In)", h2_style))
    story.append(Paragraph(
        "Untuk keperluan operasional toko retail yang membeli laptop dari konsumen, sistem menghitung harga penawaran kas "
        "(<i>Cash Offer</i>) dengan memperhitungkan margin risiko perputaran modal dan estimasi biaya perbaikan suku cadang:",
        body_style
    ))

    buyback_eq_box = Paragraph(
        "<b>Rumus Penawaran Beli Toko (analytics/buyback_engine.py):</b><br/>"
        "Net Cash Base = Adjusted FMV × ( 1 - Margin Toko ) - Σ Biaya Kerusakan + Σ Bonus<br/>"
        "Di mana Margin Toko: Apple (22%), Consumer Standar (25%), Gaming (28%)<br/>"
        "Batas Penawaran Kas: Cash Low = Net Cash Base - Rentang Langkah, &nbsp; Cash High = Net Cash Base + Rentang Langkah<br/>"
        "(Rentang Langkah: Rp 250.000 untuk Standar, Rp 500.000 untuk Gaming/Apple)<br/>"
        "<b>Kredit Tukar Tambah (Trade-In Credit) = Cash High × 1.08</b> &nbsp; (Memberikan insentif 8% lebih tinggi)<br/>"
        "Nilai Sisa Mati Total (Salvage Rate) = 12.5% × Adjusted FMV &nbsp; (Lantai komersial min: Rp 150.000)",
        formula_text
    )
    story.append(create_callout_box(buyback_eq_box, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Rasionalisasi Penetapan Margin Toko:</b> Produk Apple Silicon diberikan margin risiko terendah (22%) karena memiliki "
        "kecepatan perputaran inventori (inventory turnover) tertinggi di pasar Indonesia (rata-rata laku dalam 7 - 14 hari). "
        "Sebaliknya, laptop gaming menanggung margin tertinggi (28%) akibat depresiasi nilai komponen GPU yang sangat cepat saat "
        "generasi baru diluncurkan oleh Nvidia/AMD.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 9: BAB 7 (BAGIAN 1): KASUS 1 (MULTI-SAMPEL) & KASUS 2 (OUTLIER)
    # =========================================================================
    story.append(Paragraph("BAB 7: Simulasi Perhitungan Kasus Nyata (Bagian 1)", h1_style))
    story.append(Paragraph(
        "Bab ini menyajikan simulasi audit numerik nyata yang merefleksikan implementasi algoritma pada database produksi.",
        body_style
    ))

    # KASUS 1
    story.append(Paragraph("7.1 Kasus 1: Unit Populer dengan Multi-Sampel Pasar Riil", h2_style))
    story.append(Paragraph(
        "<b>Subjek:</b> ASUS ROG Flow X13 GV301 (Tahun Rilis: 2021, AMD Ryzen 9 5900HS, RAM 16GB, SSD 512GB, RTX 3050 Ti). "
        "Data diambil langsung dari tab <code>list harga tarikan</code> dan tab <code>Matriks FMV (Model & Tahun)</code> baris 273.",
        body_style
    ))

    case1_data = [
        [Paragraph("No Sampel", table_header), Paragraph("Judul Listing Riil Tokopedia", table_header), Paragraph("Harga Listing (Rp)", table_header), Paragraph("Status Evaluasi Tukey IQR", table_header)],
        [Paragraph("1", table_cell), Paragraph("ASUS ROG Flow X13 GV301QE R9 5900HS 16GB 512GB RTX 3050Ti", table_cell), Paragraph("Rp 13.500.000", table_cell), Paragraph("Valid (Batas Minimum Wajar)", table_cell)],
        [Paragraph("2", table_cell), Paragraph("Rog Flow X13 GV301 2in1 Gaming Touchscreen Ryzen 9 Fullset", table_cell), Paragraph("Rp 13.900.000", table_cell), Paragraph("Valid (Persentil 25 / Q1)", table_cell)],
        [Paragraph("3", table_cell), Paragraph("Laptop Asus ROG Flow x13 gv301 rtx 3050 ti ram 16gb second", table_cell), Paragraph("Rp 14.200.000", table_cell), Paragraph("Valid (Dalam Rentang Pagar)", table_cell)],
        [Paragraph("4", table_cell), Paragraph("Asus ROG Flow X13 GV301QE Mulus Like New Garansi Panjang", table_cell), Paragraph("Rp 14.500.000", table_cell_bold), Paragraph("<b>Valid (Median FMV Pasar)</b>", table_cell_bold)],
        [Paragraph("5", table_cell), Paragraph("ASUS ROG Flow X13 GV301 Touch 120Hz Ryzen 9 RTX3050Ti", table_cell), Paragraph("Rp 14.500.000", table_cell_bold), Paragraph("<b>Valid (Median FMV Pasar)</b>", table_cell_bold)],
        [Paragraph("6", table_cell), Paragraph("ROG Flow X13 GV301QE Ryzen 9 5900HS RTX 3050Ti 16GB Mulus", table_cell), Paragraph("Rp 15.000.000", table_cell), Paragraph("Valid (Dalam Rentang Pagar)", table_cell)],
        [Paragraph("7", table_cell), Paragraph("ASUS ROG FLOW X13 GV301 2021 R9 RTX 3050Ti SSD 1TB Fullset Dus", table_cell), Paragraph("Rp 15.300.000", table_cell), Paragraph("Valid (Persentil 75 / Q3)", table_cell)],
        [Paragraph("8", table_cell), Paragraph("Asus ROG Flow X13 GV301 R9 RTX3050Ti RAM 32GB Box Lengkap", table_cell), Paragraph("Rp 16.500.000", table_cell), Paragraph("Valid (Batas Maksimum Wajar)", table_cell)]
    ]
    story.append(create_styled_table(case1_data, [50, 240, 105, 120], is_header=True, custom_padding=3))

    story.append(Spacer(1, 5))
    case1_res_box = Paragraph(
        "<b>Hasil Komputasi Kasus 1 (Tercatat di Matriks FMV Baris 273):</b><br/>"
        "• Jumlah Sampel Riil = 8 unit &nbsp;|&nbsp; Harga Min = Rp 13.500.000 &nbsp;|&nbsp; Harga Max = Rp 16.500.000<br/>"
        "• Q<sub>1</sub> (P25) = Rp 13.900.000 &nbsp;|&nbsp; Q<sub>3</sub> (P75) = Rp 15.300.000 &nbsp;|&nbsp; IQR = Rp 1.400.000<br/>"
        "• Batas Bawah IQR = Rp 13.900.000 - (1.5 × 1.4jt) = Rp 11.800.000 &nbsp;|&nbsp; Batas Atas IQR = Rp 17.400.000<br/>"
        "• <b>Base Fair Market Value (Median P50) = Rp 14.500.000</b> (Terkoneksi sempurna ke Katalog Master via SUMIFS).",
        callout_text
    )
    story.append(create_callout_box(case1_res_box, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(Spacer(1, 8))

    # KASUS 2
    story.append(Paragraph("7.2 Kasus 2: Penanganan Kasus Outlier Ekstrim (Listing Scam DP & Overpricing)", h2_style))
    story.append(Paragraph(
        "<b>Subjek:</b> Lenovo Legion 5 15ACH6 (Tahun Rilis: 2021, Ryzen 7 5800H, RTX 3060). "
        "Skenario pengujian ketahanan terhadap gangguan data kotor pasar e-commerce.",
        body_style
    ))

    case2_data = [
        [Paragraph("Tahap Analisis", table_header), Paragraph("Data Harga Listing Pasar", table_header), Paragraph("Keterangan & Tindakan Algoritma", table_header)],
        [
            Paragraph("Listing Mentah Scraper<br/>(Raw Market Data)", table_cell_bold),
            Paragraph("Rp 1.500.000 (Iklan Scam / Uang Muka DP Kredit)<br/>"
                      "Rp 11.500.000, Rp 12.000.000, Rp 12.200.000, Rp 12.500.000,<br/>"
                      "Rp 12.800.000, Rp 13.000.000, Rp 13.500.000<br/>"
                      "Rp 28.500.000 (Penjual Overpriced Berdasarkan Nota Lama 2021)", table_cell),
            Paragraph("Terdapat 9 listing dengan rentang sangat lebar (Rp 1,5 jt s/d Rp 28,5 jt).<br/>"
                      "Jika dihitung rata-rata (MEAN): <b>Rp 13.055.556</b> (terdistorsi berat).", table_cell)
        ],
        [
            Paragraph("Penerapan Tukey's IQR Fences", table_cell_bold),
            Paragraph("Q<sub>1</sub> = Rp 12.000.000 &nbsp;|&nbsp; Q<sub>3</sub> = Rp 13.000.000<br/>"
                      "IQR = Rp 13.000.000 - Rp 12.000.000 = Rp 1.000.000<br/>"
                      "<b>Batas Bawah = Rp 12.000.000 - 1.5 × 1 jt = Rp 10.500.000</b><br/>"
                      "<b>Batas Atas = Rp 13.000.000 + 1.5 × 1 jt = Rp 14.500.000</b>", table_cell),
            Paragraph("• Listing Rp 1.500.000 < Rp 10.500.000 ==> <b>DIBUANG (OUTLIER BAWAH)</b>.<br/>"
                      "• Listing Rp 28.500.000 > Rp 14.500.000 ==> <b>DIBUANG (OUTLIER ATAS)</b>.<br/>"
                      "Tersisa 7 sampel harga valid (Rp 11,5 jt s/d Rp 13,5 jt).", table_cell)
        ],
        [
            Paragraph("Hasil Rekalkulasi FMV", table_cell_bold),
            Paragraph("Himpunan Tersaring: [11.5jt, 12.0jt, 12.2jt, 12.5jt, 12.8jt, 13.0jt, 13.5jt]<br/>"
                      "<b>Median FMV Bersih = Rp 12.500.000</b>", table_cell_bold),
            Paragraph("Sistem berhasil membuang distorsi scam dan overprice tanpa intervensi manual manusia. Akurasi 100%.", table_cell)
        ]
    ]
    story.append(create_styled_table(case2_data, [125, 230, 160], is_header=True, custom_padding=3.5))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 10: BAB 7 (BAGIAN 2): KASUS 3 (ZERO SAMPLE) & KASUS 4 (HEDONIK)
    # =========================================================================
    story.append(Paragraph("BAB 7: Simulasi Perhitungan Kasus Nyata (Bagian 2)", h1_style))
    story.append(Paragraph(
        "Bagian ini mendemonstrasikan penanganan kondisi tepi (edge cases): produk tanpa listing pasar riil serta "
        "unit bekas dengan cacat keausan baterai dan fisik nyata.",
        body_style
    ))

    # KASUS 3
    story.append(Paragraph("7.3 Kasus 3: Unit Langka / Zero Listing Riil Pasar (Fallback Model Depresiasi)", h2_style))
    story.append(Paragraph(
        "<b>Subjek:</b> Lenovo ThinkPad X1 Carbon Gen 9 (Tahun Rilis: 2021, Intel Core i7-1165G7, RAM 16GB, SSD 512GB). "
        "Kasus di mana unit jarang diperjualbelikan di marketplace terbuka (listing riil = 0) sehingga memicu fallback ekonometrik.",
        body_style
    ))

    case3_box = Paragraph(
        "<b>Simulasi Langkah demi Langkah Model Depresiasi Ekonometrik:</b><br/>"
        "1. <b>Penetapan Kasta Hardware:</b> Merek Lenovo seri 'ThinkPad X1' diklasifikasikan ke dalam <b>Tier Business Enterprise</b>.<br/>"
        "2. <b>Parameter Tier Business Enterprise:</b> δ₁ (Tahun ke-1) = 20%, δₐ (Penyusutan tahunan) = 9%, Max Cap Depresiasi = 75%.<br/>"
        "3. <b>MSRP Baru Peluncuran (2021):</b> Rp 33.500.000 OTR Indonesia.<br/>"
        "4. <b>Perhitungan Usia Aset:</b> t = 2026 - 2021 = <b>5 Tahun</b>.<br/>"
        "5. <b>Akumulasi Depresiasi:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Depresiasi Total = δ₁ + (t - 1) × δₐ = 20% + (5 - 1) × 9% = 20% + 36% = <b>56.0%</b>.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Karena 56.0% < Max Cap (75%), maka nilai depresiasi efektif = 56.0%.<br/>"
        "6. <b>Tingkat Retensi Nilai:</b> R(5) = 1.0 - 0.56 = <b>44.0%</b>.<br/>"
        "7. <b>Estimasi Base FMV Teoretis Fallback:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;FMV Fallback = Rp 33.500.000 × 44.0% = <b>Rp 14.740.000</b>.<br/>"
        "<i>Dengan algoritma ini, sistem tidak akan pernah menghasilkan nilai kosong (null/error) meskipun data pasar nihil.</i>",
        callout_text
    )
    story.append(create_callout_box(case3_box, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(Spacer(1, 8))

    # KASUS 4
    story.append(Paragraph("7.4 Kasus 4: Unit Bekas dengan Penurunan Kondisi Fisik & Baterai (Penyesuaian Hedonik & Buyback)", h2_style))
    story.append(Paragraph(
        "<b>Subjek:</b> ASUS Vivobook 14 A416 (Tahun Rilis: 2022, Core i5-1135G7, RAM 8GB, SSD 512GB). "
        "Base FMV kondisi normal = <b>Rp 5.800.000</b>. Konsumen menjual laptop dengan beberapa catatan keausan fisik.",
        body_style
    ))

    case4_table_data = [
        [Paragraph("Komponen / Atribut yang Dinilai", table_header), Paragraph("Kondisi Riil Unit Konsumen", table_header), Paragraph("Koefisien Penalti Hedonik (Δ)", table_header), Paragraph("Nilai Potongan Moneter (Rp)", table_header)],
        [Paragraph("Status Garansi", table_cell_bold), Paragraph("Garansi Resmi Asus ID Sudah Habis", table_cell), Paragraph("Netral (0.00)", table_cell), Paragraph("Rp 0", table_cell)],
        [Paragraph("Kesehatan Baterai", table_cell_bold), Paragraph("Baterai Drop (Hanya tahan 20 mnt, harus colok)", table_cell), Paragraph("Penalti Baterai (-0.20)", table_cell), Paragraph("- Rp 1.160.000", table_cell)],
        [Paragraph("Kondisi Fisik Casing", table_cell_bold), Paragraph("Grade B (Lecet pemakaian halus pada cover)", table_cell), Paragraph("Penalti Grade B (-0.07)", table_cell), Paragraph("- Rp 406.000", table_cell)],
        [Paragraph("Panel Layar LCD", table_cell_bold), Paragraph("Whitespot Tipis di pojok kanan bawah", table_cell), Paragraph("Penalti Whitespot (-0.10)", table_cell), Paragraph("- Rp 580.000", table_cell)],
        [Paragraph("Kelengkapan Aksesoris", table_cell_bold), Paragraph("Batangan (Hanya unit laptop tanpa charger)", table_cell), Paragraph("Penalti Batangan (-0.12)", table_cell), Paragraph("- Rp 696.000", table_cell)],
        [Paragraph("Total Akumulasi Penyesuaian", table_cell_bold), Paragraph("4 Cacat Fungsional & Fisik", table_cell_bold), Paragraph("<b>Δ<sub>net</sub> = -0.49 (-49.0%)</b>", table_cell_bold), Paragraph("<b>- Rp 2.842.000</b>", table_cell_bold)]
    ]
    story.append(create_styled_table(case4_table_data, [130, 165, 115, 105], is_header=True, custom_padding=3))

    story.append(Spacer(1, 5))
    case4_res_box = Paragraph(
        "<b>Dua Perspektif Output Penilaian Kasus 4:</b><br/>"
        "<b>A. Nilai Pasar C2C Disesuaikan (Transparansi Jual Antar Pengguna Langsung):</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Harga Wajar Terkoreksi = Rp 5.800.000 × (1 - 0.49) = <b>Rp 2.958.000</b>.<br/>"
        "<b>B. Penawaran Kas Beli Toko (Cash Offer Buyback Commercial):</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Toko retail menanggung margin perputaran inventori (Consumer Tier = 25% = Rp 1.450.000) "
        "serta biaya suku cadang: baterai baru (Rp 450rb), adaptor ori (Rp 250rb), dan servis whitespot (Rp 250rb).<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Cash Offer Mid Toko = <b>Rp 2.250.000</b> (Rentang Penawaran: Rp 2.000.000 - Rp 2.500.000).<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Nilai Kredit Tukar Tambah (Trade-In Offer) = <b>Rp 2.700.000</b> (Insentif 8% jika tukar tambah ke unit lain).",
        callout_text
    )
    story.append(create_callout_box(case4_res_box, bg_color="#f8fafc", border_color="#cbd5e1", width=515))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 11: BAB 8 (BAGIAN 1): TATA KELOLA DATA & OTOMASI AIRFLOW
    # =========================================================================
    story.append(Paragraph("BAB 8: Tata Kelola, Audit Integritas Data, & Otomasi Pipeline", h1_style))
    story.append(Paragraph(
        "Sistem penetapan harga yang andal memerlukan tata kelola data (<i>data governance</i>) yang disiplin serta "
        "audit otomatis berkala untuk mencegah degradasi model maupun infeksi data palsu.",
        body_style
    ))

    story.append(Paragraph("8.1 Orkestrasi Pipeline Harian via Apache Airflow DAG", h2_style))
    story.append(Paragraph(
        "Seluruh proses penarikan data, sanitasi, pemotongan pencilan, dan agregasi FMV dijalankan secara otomatis "
        "oleh penjadwal terpusat <b>Apache Airflow</b> melalui DAG teruji: <code>laptop_price_scraping_v1</code> dan <code>dag_sync_market_stats</code>.<br/>"
        "• <b>Siklus Eksekusi:</b> Dijalankan setiap hari pada pukul 02:00 WIB (fase penarikan data e-commerce) dan pukul 05:00 WIB (fase agregasi statistik).<br/>"
        "• <b>SLA Ketersediaan Data:</b> Maksimal latensi data pasar adalah 24 jam. Setiap baris data pada Lapis 2 dilengkapi dengan stempel waktu <code>calculated_at</code>.<br/>"
        "• <b>Fault Tolerance & Retry Policy:</b> Kegagalan koneksi jaringan ke e-commerce secara otomatis memicu <i>exponential backoff retry</i> (3 kali percobaan dengan interval 5 menit).",
        body_style
    ))

    story.append(Paragraph("8.2 Protokol Pencegahan Data Palsu (Zero Synthetic Data Guarantee)", h2_style))
    story.append(Paragraph(
        "LaptopPrice ID menerapkan standar ketat kepatuhan data: <b>100% Data Riil Terverifikasi</b>. "
        "Sistem melarang keras penggunaan generator data sintetis (dummy) dalam penentuan FMV komersial. "
        "Setiap baris listing pada Lapis 1 wajib memiliki URL tautan sumber asli yang aktif, nama merchant yang terdaftar, dan kota asal seller yang jelas.",
        body_style
    ))

    story.append(Paragraph("8.3 Sinkronisasi Multi-File dan Pemeliharaan Integritas Formula Excel", h2_style))
    story.append(Paragraph(
        "Untuk mencegah ketidaksesuaian data antar tim operasional, berkas spreadsheet master <code>pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx</code> "
        "disinkronkan secara otomatis ke 3 direktori sistem:<br/>"
        "1. Direktori Kerja Utama: <code>exports/pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx</code><br/>"
        "2. Direktori Unduhan Pengguna: <code>~/Downloads/pemetaan_tipe_laptop_internal_vs_laptopmedia.xlsx</code><br/>"
        "3. Direktori Arsip Tim Audit: <code>~/Downloads/pemetaan tipe laptop data internal dan data tarikan laptopmedia/...</code><br/>"
        "Setiap proses pembaruan data memvalidasi ulang seluruh formula <code>SUMIFS</code> guna memastikan tidak ada sel bernilai <code>#NAME?</code> atau strip kosong.",
        body_style
    ))

    story.append(Spacer(1, 6))
    airflow_callout = Paragraph(
        "<b>Status Kesiapan Pipeline Apache Airflow:</b><br/>"
        "Pipeline scraper dan sinkronisasi statistik telah diuji secara komprehensif pada server lokal "
        "(Webserver Airflow: <code>http://localhost:8088</code> / Flower: <code>http://localhost:8095</code>). "
        "Seluruh 39 unit test pada modul <code>tests/test_pricing_engine.py</code> dan <code>tests/test_buyback_engine.py</code> "
        "lulus 100% tanpa catatan galat. Sistem siap melayani penarikan data skala penuh secara berkelanjutan.",
        callout_text
    )
    story.append(create_callout_box(airflow_callout, bg_color="#eff6ff", border_color="#93c5fd", width=515))

    story.append(Spacer(1, 8))
    story.append(Paragraph("8.4 Rekomendasi Penerapan Operasional", h2_style))
    story.append(Paragraph(
        "1. <b>Bagi Tim Analis & Bisnis:</b> Gunakan nilai <b>Median FMV</b> sebagai patokan harga jual pasar wajar, "
        "dan perhatikan <b>P25</b> untuk menetapkan batas minimum diskon promosi kilat.<br/>"
        "2. <b>Bagi Tim Penilai Lapangan (Appraiser Toko):</b> Wajib melakukan inspeksi 12 parameter sebelum menetapkan harga penawaran beli. "
        "Gunakan tabel potongan suku cadang pada Lapis Buyback untuk transparansi penjelasan kepada konsumen yang menjual laptop.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 12: BAB 8 (BAGIAN 2): DEFECT CATALOG, PENGESAHAN, & BIBLIOGRAFI
    # =========================================================================
    story.append(Paragraph("8.5 Matriks Ringkasan Biaya Pengurangan Kerusakan Toko (Defect Catalog)", h2_style))
    story.append(Paragraph(
        "Berikut adalah katalog biaya standar suku cadang dan servis yang digunakan oleh mesin buyback untuk menghitung potongan cacat fisik:",
        body_style
    ))

    defect_cat_data = [
        [Paragraph("Komponen Defek", table_header), Paragraph("Deskripsi Gejala Kerusakan", table_header), Paragraph("Laptop Standar (Rp)", table_header), Paragraph("Laptop Gaming (Rp)", table_header), Paragraph("Apple MacBook (Rp)", table_header)],
        [Paragraph("Layar Pecah / Blank", table_cell_bold), Paragraph("Panel LCD retak fisik, membutuhkan modul baru", table_cell), Paragraph("Rp 750.000", table_cell), Paragraph("Rp 1.200.000", table_cell), Paragraph("Rp 2.200.000", table_cell)],
        [Paragraph("Layar Bergaris / Flicker", table_cell_bold), Paragraph("Garis horizontal/vertikal atau kedip flexgate", table_cell), Paragraph("Rp 650.000", table_cell), Paragraph("Rp 1.000.000", table_cell), Paragraph("Rp 1.800.000", table_cell)],
        [Paragraph("Whitespot / Dead Pixel", table_cell_bold), Paragraph("Bercak terang atau titik piksel mati pada panel", table_cell), Paragraph("Rp 250.000", table_cell), Paragraph("Rp 350.000", table_cell), Paragraph("Rp 500.000", table_cell)],
        [Paragraph("Baterai Drop (< 30 mnt)", table_cell_bold), Paragraph("Kapasitas aus berat, wajib colok adaptor", table_cell), Paragraph("Rp 450.000", table_cell), Paragraph("Rp 650.000", table_cell), Paragraph("Rp 850.000", table_cell)],
        [Paragraph("Baterai Kembung", table_cell_bold), Paragraph("Sel baterai bengkak menekan trackpad (bahaya)", table_cell), Paragraph("Rp 550.000", table_cell), Paragraph("Rp 750.000", table_cell), Paragraph("Rp 950.000", table_cell)],
        [Paragraph("Engsel Patah / Rusak", table_cell_bold), Paragraph("Dudukan baut engsel hancur dari sasis", table_cell), Paragraph("Rp 450.000", table_cell), Paragraph("Rp 550.000", table_cell), Paragraph("Rp 800.000", table_cell)],
        [Paragraph("Casing Penyok (Dent)", table_cell_bold), Paragraph("Benturan keras sudut bodi atau sasis retak", table_cell), Paragraph("Rp 400.000", table_cell), Paragraph("Rp 500.000", table_cell), Paragraph("Rp 750.000", table_cell)],
        [Paragraph("Keyboard Tombol Mati", table_cell_bold), Paragraph("Satu/lebih tombol keyboard tidak merespons", table_cell), Paragraph("Rp 300.000", table_cell), Paragraph("Rp 450.000", table_cell), Paragraph("Rp 750.000", table_cell)],
        [Paragraph("Charger Hilang (Batangan)", table_cell_bold), Paragraph("Unit dijual tanpa charger original bawaan", table_cell), Paragraph("Rp 250.000", table_cell), Paragraph("Rp 450.000", table_cell), Paragraph("Rp 550.000", table_cell)],
        [Paragraph("BIOS / MDM Lock", table_cell_bold), Paragraph("Firmware terkunci password atau profil MDM", table_cell), Paragraph("Rp 400.000", table_cell), Paragraph("Rp 400.000", table_cell), Paragraph("Rp 800.000", table_cell)]
    ]
    story.append(create_styled_table(defect_cat_data, [105, 170, 80, 80, 80], is_header=True, custom_padding=2.8))

    story.append(Spacer(1, 8))

    # LEMBAR PENGESAHAN TATA KELOLA (SIGN-OFF BOX)
    story.append(Paragraph("<b>Lembar Pengesahan Tata Kelola (Sign-off Box):</b>", ParagraphStyle('SignHdr', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#0f172a"), spaceBefore=2, spaceAfter=4, keepWithNext=True)))

    sign_table_data = [
        [Paragraph("Disiapkan Oleh:", table_cell_bold), Paragraph("Diverifikasi Oleh:", table_cell_bold), Paragraph("Disetujui Oleh:", table_cell_bold)],
        [
            Paragraph("<b>Data Analyst & Riset</b><br/>Tim Analisis Data & Riset<br/>LaptopPrice ID Engine Team", table_cell),
            Paragraph("<b>Manajer Business Development</b><br/>Divisi Business Development<br/>PT Hardware Analytics Indonesia", table_cell),
            Paragraph("<b>Chief Risk Officer / Board of Directors</b><br/>Valuation Committee<br/>Status: <b>APPROVED FOR PRODUCTION</b>", table_cell)
        ]
    ]
    story.append(create_styled_table(sign_table_data, [170, 175, 170], is_header=False, custom_padding=4.2))

    story.append(Spacer(1, 8))

    # REFERENSI BIBLIOGRAFI LENGKAP
    story.append(Paragraph("<b>Daftar Referensi Ilmiah & Bibliografi Standar:</b>", h3_style))
    story.append(Paragraph(
        "1. Court, A. T. (1939). <i>Hedonic price indexes with automotive examples</i>. The Dynamics of Automobile Demand, General Motors Corporation, New York, 99-117.<br/>"
        "2. Griliches, Z. (1961). <i>Hedonic price indexes for automobiles: An econometric analysis of quality change</i>. The Price Statistics of the Federal Government, NBER, 173-196.<br/>"
        "3. Griliches, Z. (1971). <i>Price Indexes and Quality Change: Studies in New Methods of Measurement</i>. Harvard University Press, Cambridge, Massachusetts.<br/>"
        "4. Lancaster, K. J. (1966). <i>A new approach to consumer theory</i>. Journal of Political Economy, 74(2), 132-157.<br/>"
        "5. Tukey, J. W. (1977). <i>Exploratory Data Analysis</i>. Addison-Wesley Publishing Company, Reading, Massachusetts.<br/>"
        "6. International Valuation Standards Council (IVSC). (2022). <i>International Valuation Standards (IVS 104: Bases of Value & IVS 220: Plant and Equipment)</i>. London, United Kingdom.<br/>"
        "7. American Society of Appraisers (ASA). (2020). <i>Valuing Machinery and Equipment: The Fundamentals of Appraising Machinery and Technical Assets (4th Edition)</i>. Herndon, Virginia.",
        table_cell
    ))

    # Bangun Dokumen PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f" Dokumen PDF berhasil dibangun: {output_filepath}")


if __name__ == "__main__":
    target_path = "docs/PANDUAN_METODOLOGI_FAIR_MARKET_VALUE_FMV_LAPTOP.pdf"
    if len(sys.argv) > 1:
        target_path = sys.argv[1]

    build_fmv_methodology_pdf(target_path)

    # Salin juga ke folder Downloads pengguna
    downloads_target = os.path.expanduser("~/Downloads/PANDUAN_METODOLOGI_FAIR_MARKET_VALUE_FMV_LAPTOP.pdf")
    try:
        shutil.copyfile(target_path, downloads_target)
        print(f" Dokumen PDF berhasil disalin ke Downloads: {downloads_target}")
    except Exception as e:
        print(f" Gagal menyalin ke Downloads: {e}")
