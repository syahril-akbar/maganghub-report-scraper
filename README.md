# MagangHub Monthly Report Scraper

Tool Python interaktif untuk mengambil laporan harian MagangHub Monev dalam rentang tanggal tertentu, lalu menyusunnya menjadi satu file Markdown.

Target laporan per hari:

- Uraian Aktivitas
- Pembelajaran yang Diperoleh
- Kendala yang Dialami

## Fitur

- Input tanggal mulai dan akhir secara interaktif.
- Membuka browser Chromium nyata untuk autentikasi manual.
- Menyimpan session browser lokal agar login berikutnya biasanya tidak perlu diulang.
- Mengakses laporan berdasarkan parameter URL `date=YYYY-MM-DD`.
- Mengabaikan Sabtu dan Minggu.
- Retry navigasi ketika SSO MagangHub masih mengalihkan halaman.
- Tidak menimpa Markdown sebelumnya apabila tidak ada laporan berhasil diambil.
- Menulis laporan menjadi Markdown siap diedit atau dikonversi menjadi dokumen resmi.

## Arsitektur

```text
Terminal PowerShell
        |
        v
scrape_maganghub.py
        |
        +-- Playwright Chromium persistent profile
        |        |
        |        +-- Login SSO MagangHub manual
        |
        +-- URL riwayat per tanggal
        |        |
        |        +-- Ekstraksi teks laporan harian
        |
        +-- Laporan-Bulanan-Magang-*.md
```

## Struktur Folder

```text
Agustus/
├── scrape_maganghub.py
├── README.md
├── Laporan-Bulanan-Magang-2026-08-10-sd-2026-09-04.md
└── maganghub-browser-profile/   # Dibuat otomatis; session/cookie browser lokal
```

> `maganghub-browser-profile/` berisi cookie dan session autentikasi. Jangan unggah, kirim, commit, atau bagikan folder ini.

## Persyaratan

| Komponen | Versi minimum | Keterangan |
|---|---:|---|
| Windows | 10/11 | Diuji pada Windows 11 |
| Python | 3.11+ | Periksa dengan `python --version` |
| Playwright | 1.x | Automasi browser |
| Chromium Playwright | Sesuai Playwright | Browser otomatis yang dibuka script |
| Koneksi internet | Aktif | Akses SSO dan MagangHub Monev |
| Akun MagangHub aktif | Wajib | Login dilakukan sendiri di browser |

## Instalasi

Buka PowerShell pada folder proyek:

```powershell
cd "H:\My Drive\Bapekom PU Wilayah VIII\LAPORAN BULANAN MAGANG\Agustus"
```

Periksa Python:

```powershell
python --version
```

Instal dependency bila belum tersedia:

```powershell
python -m pip install playwright
python -m playwright install chromium
```

Verifikasi syntax script:

```powershell
python -m py_compile .\scrape_maganghub.py
```

Tidak ada output berarti verifikasi berhasil.

## Menjalankan

```powershell
python .\scrape_maganghub.py
```

Script meminta rentang tanggal:

```text
Tanggal mulai [YYYY-MM-DD] (Enter = 2026-08-10):
Tanggal akhir [YYYY-MM-DD] (Enter = 2026-09-04):
```

Contoh mengambil 11–14 Agustus 2026:

```text
Tanggal mulai [YYYY-MM-DD] (Enter = 2026-08-10): 2026-08-11
Tanggal akhir [YYYY-MM-DD] (Enter = 2026-09-04): 2026-08-14
```

## Alur Login

1. Script membuka Chromium Playwright.
2. Jika diarahkan ke halaman SSO, login sendiri pada browser tersebut.
3. Selesaikan seluruh proses SSO hingga kembali ke halaman `Riwayat` MagangHub.
4. Pastikan laporan halaman riwayat tampil.
5. Kembali ke PowerShell.
6. Tekan Enter ketika prompt berikut muncul:

```text
Login manual bila perlu. Setelah kembali ke halaman Riwayat, tekan Enter...
```

Jangan memasukkan password ke terminal, source code, file konfigurasi, atau Git.

## Output

Output default:

```text
Laporan-Bulanan-Magang-2026-08-10-sd-2026-09-04.md
```

Isi output per hari:

```markdown
## 10 August 2026

**Status:** Disetujui
**Kehadiran:** Hadir

### Uraian Aktivitas
...

### Pembelajaran yang Diperoleh
...

### Kendala yang Dialami
...
```

Script hanya menulis file output jika setidaknya satu laporan berhasil diekstrak. Ini mencegah hasil yang valid tertimpa file kosong saat login/session gagal.

## Log Sukses

Contoh:

```text
2026-08-10: OK
2026-08-11: OK
Saved 18 reports: H:\...\Laporan-Bulanan-Magang-2026-08-10-sd-2026-09-04.md
```

`OK` berarti tiga bagian laporan berhasil diproses untuk tanggal tersebut.

## Hari Tidak Memiliki Laporan

Hari berikut dapat tampil `no report` dan bukan kegagalan teknis:

- Sabtu dan Minggu, karena dilewati script.
- Hari libur nasional.
- Tanggal tanpa laporan harian pada akun MagangHub.

Contoh periode ini:

- 17 Agustus 2026: Proklamasi Kemerdekaan.
- 25 Agustus 2026: Maulid Nabi Muhammad S.A.W.

## Troubleshooting

### `can't open file 'H:\My'`

Penyebab: path absolut mengandung spasi dan tidak diberi tanda kutip.

Gunakan relative path saat sudah berada di folder proyek:

```powershell
python .\scrape_maganghub.py
```

Atau quote path absolut:

```powershell
python "H:\My Drive\Bapekom PU Wilayah VIII\LAPORAN BULANAN MAGANG\Agustus\scrape_maganghub.py"
```

### `Page.goto: Timeout ...`

Penyebab umum: koneksi lambat, halaman sedang memuat, WAF, atau redirect SSO.

Tindakan:

1. Jalankan ulang script.
2. Tunggu browser benar-benar selesai login.
3. Pastikan URL browser sudah kembali ke `https://monev.maganghub.kemnaker.go.id/dashboard/riwayat`.
4. Baru tekan Enter di terminal.

### `Navigation ... is interrupted by another navigation`

Penyebab: script mulai mengganti tanggal ketika callback SSO masih mengalihkan halaman.

Tindakan:

1. Tutup Chromium yang dibuka script.
2. Jalankan script ulang.
3. Login manual sampai halaman Riwayat selesai tampil.
4. Tekan Enter hanya setelah proses redirect selesai.

### `laporan tidak muncul` atau `bagian laporan tidak terbaca`

Kemungkinan penyebab:

- Hari libur atau tidak ada laporan.
- Session habis dan kembali ke SSO.
- Struktur halaman MagangHub berubah.

Periksa URL akhir yang dicetak script. Jika kembali ke halaman SSO, login ulang. Jika halaman riwayat sudah benar tetapi tetap gagal, simpan output terminal dan periksa perubahan struktur halaman sebelum mengubah selector.

### `ModuleNotFoundError: No module named 'playwright'`

```powershell
python -m pip install playwright
python -m playwright install chromium
```

### Browser tidak terbuka

Pasang browser Playwright kembali:

```powershell
python -m playwright install chromium
```

## Keamanan Data

- Login dilakukan manual; script tidak menyimpan email atau password.
- Session autentikasi tersimpan lokal di `%LOCALAPPDATA%\MagangHubScraper\profile`, di luar folder Google Drive dan Git.
- Jangan salin folder profile ke cloud publik, Git, USB bersama, atau chat.
- Logout dari MagangHub bila perangkat dipakai orang lain.
- Untuk mereset session, tutup browser lalu hapus folder `%LOCALAPPDATA%\MagangHubScraper\profile`. Tindakan ini mengharuskan login ulang pada run berikutnya.
- Log di `logs/` tidak menyimpan query URL SSO, cookie, atau password.

## Kesiapan Operasional

Script ini **interactive-only**. Jangan jalankan melalui cron atau tanpa pengawasan karena SSO membutuhkan login manual dan UI situs dapat berubah.

Proteksi bawaan:

- Output ditulis atomik melalui file sementara; file laporan lama tidak rusak saat proses berhenti.
- Output lama tidak ditimpa bila tidak ada laporan yang berhasil diekstrak.
- Browser context selalu ditutup melalui `finally`, termasuk saat error.
- Tiga bagian laporan wajib terisi sebelum suatu tanggal disimpan.
- URL pada log disanitasi; parameter SSO tidak ditulis.

Sebelum penggunaan rutin:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
playwright install chromium
python .\test_scrape_maganghub.py
```

Tes parser harus mengembalikan `parser checks: OK`.

File pendukung:

| File | Fungsi |
|---|---|
| `requirements.txt` | Versi dependency Python yang diperlukan |
| `test_scrape_maganghub.py` | Regression check parser tanpa login atau akses situs |
| `.gitignore` | Mengecualikan session, log, virtual environment, output sensitif |
| `logs/run-*.log` | Catatan proses aman untuk troubleshooting |

## Batasan

- Script mengambil teks yang telah disetujui/tersedia pada Riwayat MagangHub; tidak mengubah laporan di server.
- Hari Sabtu/Minggu dilewati otomatis.
- Hari libur nasional dapat tampil sebagai `no report`.
- Heading output memakai nama bulan Indonesia, tidak bergantung locale Windows.
- Perubahan UI/DOM MagangHub dapat memerlukan penyesuaian parser di `scrape_maganghub.py`.

## Pengembangan

Area yang relevan:

| Komponen | Tanggung jawab |
|---|---|
| `BASE_URL` | Template URL riwayat berdasarkan tanggal |
| `extract_report()` | Navigasi, validasi tanggal, ekstraksi tiga bagian laporan |
| `render()` | Penyusunan output Markdown |
| `ask_date()` | Validasi input tanggal interaktif |
| `PROFILE_DIR` | Lokasi persistent browser profile |

Prinsip perubahan:

1. Jangan memasukkan kredensial ke script.
2. Pertahankan proteksi agar file output valid tidak tertimpa saat 0 laporan.
3. Uji pada rentang kecil, misalnya 1–2 hari, sebelum menjalankan satu periode penuh.
4. Simpan output terminal jika terjadi error navigasi/SSO.

## Lisensi dan Penggunaan

Tool ini dibuat untuk penggunaan internal dalam penyusunan laporan magang. Data MagangHub tetap milik pemilik akun dan tunduk pada kebijakan Kementerian Ketenagakerjaan serta instansi terkait.
