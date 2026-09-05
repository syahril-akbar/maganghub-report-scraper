# Scraper Laporan MagangHub

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.62%2B-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)](https://www.microsoft.com/windows)

Tool Python interaktif untuk mengekspor laporan harian MagangHub Monev menjadi laporan bulanan berformat Markdown.

> Login tetap manual. Kredensial, cookie, token SSO, profile browser, log, serta laporan hasil scrape tidak disimpan di Git.

## Data yang Diekspor

Untuk setiap hari kerja yang memiliki laporan dalam rentang tanggal pilihan:

- Uraian Aktivitas
- Pembelajaran yang Diperoleh
- Kendala yang Dialami
- Status persetujuan dan kehadiran

## Fitur

- Input tanggal mulai dan akhir secara interaktif.
- Login SSO manual melalui Chromium Playwright nyata.
- Session browser disimpan lokal di `%LOCALAPPDATA%\MagangHubScraper\profile`.
- Akses laporan langsung melalui parameter `date=YYYY-MM-DD`.
- Sabtu dan Minggu dilewati otomatis.
- Retry ketika navigasi atau redirect SSO belum stabil.
- Laporan diterima hanya bila tiga bagian inti lengkap.
- Penulisan Markdown atomik; laporan lama tidak diganti file kosong.
- URL log disanitasi; query SSO, token, dan cookie tidak dicatat.
- Tes regresi parser dan penutupan browser tersedia tanpa login.

## Mulai Cepat

```powershell
# 1. Clone repository
git clone https://github.com/syahril-akbar/maganghub-report-scraper.git
cd maganghub-report-scraper

# 2. Buat environment terisolasi
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Pasang dependency dan browser
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium

# 4. Verifikasi instalasi
python .\test_scrape_maganghub.py
python .\test_context_cleanup.py

# 5. Jalankan scraper
python .\scrape_maganghub.py
```

Output verifikasi yang diharapkan:

```text
parser checks: OK
playwright context cleanup: OK
```

## Penggunaan

```powershell
python .\scrape_maganghub.py
```

Contoh rentang tanggal:

```text
Tanggal mulai [YYYY-MM-DD] (Enter = 2026-08-10): 2026-08-10
Tanggal akhir [YYYY-MM-DD] (Enter = 2026-09-04): 2026-09-04
```

Saat browser terbuka:

1. Selesaikan SSO MagangHub sendiri.
2. Tunggu halaman kembali ke `Riwayat`.
3. Pastikan detail laporan telah tampil.
4. Kembali ke PowerShell, lalu tekan Enter.

Jangan masukkan password pada terminal, source code, konfigurasi Git, atau issue tracker.

## Output

Run berhasil menghasilkan file Markdown sesuai rentang:

```text
Laporan-Bulanan-Magang-2026-08-10_sd_2026-09-04.md
```

Contoh isi:

```markdown
## 10 Agustus 2026

**Status:** Disetujui  
**Kehadiran:** Hadir

### Uraian Aktivitas
...

### Pembelajaran yang Diperoleh
...

### Kendala yang Dialami
...
```

`OK` berarti tiga bagian laporan ditemukan dan tervalidasi. `no report` wajar pada hari libur nasional atau tanggal tanpa laporan harian.

## Arsitektur

```text
PowerShell
  │
  ├─ scrape_maganghub.py
  │    ├─ Chromium Playwright
  │    │    └─ SSO MagangHub manual
  │    ├─ URL laporan per tanggal
  │    ├─ Parser teks aman
  │    └─ Penulis Markdown atomik
  │
  ├─ %LOCALAPPDATA%\MagangHubScraper\profile
  │    └─ Session browser lokal
  │
  └─ Laporan-Bulanan-Magang-*.md
```

## Struktur Proyek

```text
maganghub-report-scraper/
├── scrape_maganghub.py          # Scraper interaktif
├── test_scrape_maganghub.py     # Tes regresi parser offline
├── test_context_cleanup.py       # Tes regresi penutupan Playwright
├── requirements.txt              # Dependency Python terpin
├── .gitignore                    # Proteksi artefak session/runtime
├── logs/                         # Log runtime; diabaikan Git
└── Laporan-Bulanan-Magang-*.md   # Laporan privat; diabaikan Git
```

## Persyaratan

| Komponen | Kebutuhan |
|---|---|
| OS | Windows 10/11 |
| Python | 3.11+ |
| Internet | Koneksi aktif ke MagangHub Monev/SSO |
| Akun | Akun MagangHub aktif |
| Browser | Chromium Playwright, dipasang via CLI |

## Operasi Aman

- Hanya untuk penggunaan interaktif. Jangan gunakan cron atau proses tanpa pengawasan; SSO memerlukan konfirmasi manusia dan UI situs dapat berubah.
- Session browser berada di luar folder proyek sehingga tidak tersinkron cloud atau ter-commit ke Git.
- Browser context ditutup sebelum Playwright berhenti, menghindari error `Event loop is closed`.
- Log ditulis pada `logs/run-*.log` dengan detail diagnostik aman.
- Output hanya dibuat bila setidaknya satu laporan berhasil diekstrak.

Reset session login: tutup browser scraper, lalu hapus folder berikut.

```text
%LOCALAPPDATA%\MagangHubScraper\profile
```

Run berikutnya memerlukan login ulang.

## Troubleshooting

### `ModuleNotFoundError: No module named 'playwright'`

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### `Page.goto: Timeout` atau navigasi terinterupsi

SSO masih melakukan redirect atau koneksi lambat.

1. Tutup browser yang dibuka script.
2. Jalankan script ulang.
3. Selesaikan SSO.
4. Tunggu halaman `Riwayat` stabil.
5. Baru tekan Enter pada PowerShell.

### `laporan atau tanggal tidak muncul`

Kemungkinan tidak ada laporan, session habis, atau halaman belum selesai dimuat. Login kembali lalu uji rentang satu hari.

### `tiga bagian laporan tidak lengkap`

Umumnya hari libur atau tanggal tanpa laporan. Bila terjadi pada hari yang pasti memiliki laporan, simpan log aman lalu periksa struktur halaman MagangHub sebelum mengubah parser.

### `can't open file 'D:\MyProgram\...'`

Jalankan dari folder proyek:

```powershell
cd D:\MyProgram\maganghub-report-scraper
python .\scrape_maganghub.py
```

## Pengembangan

Jalankan pemeriksaan setelah mengubah parser atau lifecycle browser:

```powershell
python .\test_scrape_maganghub.py
python .\test_context_cleanup.py
python -m py_compile .\scrape_maganghub.py .\test_scrape_maganghub.py .\test_context_cleanup.py
```

| Komponen | Tanggung jawab |
|---|---|
| `extract_report()` | Navigasi, validasi, ekstraksi laporan |
| `report_sections()` | Parser tiga bagian laporan |
| `atomic_write()` | Penggantian output secara aman |
| `safe_url()` | Menghapus query URL sensitif dari log |
| `PROFILE_DIR` | Lokasi persistent browser session lokal |

## Ruang Lingkup

Project ini hanya membaca laporan yang tersedia untuk akun terautentikasi. Project tidak membuat, mengubah, menyetujui, atau mengirim laporan pada MagangHub.

Gunakan secara bertanggung jawab. Data MagangHub tetap tunduk pada kebijakan platform dan instansi terkait.

## Lisensi

Lisensi belum ditetapkan. Seluruh hak cipta dilindungi sampai pemilik repository menambahkan file lisensi.
