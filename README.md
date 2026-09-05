# MagangHub Report Scraper

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.62%2B-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)](https://www.microsoft.com/windows)

Interactive Python tool for exporting MagangHub Monev daily internship reports into a clean Markdown monthly report.

> Login stays manual. Credentials, cookies, SSO tokens, browser profiles, logs, and generated reports are excluded from Git.

## What It Exports

For every available weekday in a selected date range:

- Uraian Aktivitas
- Pembelajaran yang Diperoleh
- Kendala yang Dialami
- Status approval and attendance

## Features

- Interactive start/end date input.
- Manual SSO authentication in a real Playwright Chromium browser.
- Reuses a local-only browser session at `%LOCALAPPDATA%\MagangHubScraper\profile`.
- Navigates reports directly using `date=YYYY-MM-DD`.
- Skips weekends automatically.
- Retries unstable SSO/navigation redirects.
- Requires all three report sections before accepting an entry.
- Writes Markdown atomically; valid prior output is never replaced with an empty file.
- Sanitizes SSO URL logs; query strings, tokens, and cookies are not logged.
- Includes offline parser and browser-cleanup regression checks.

## Quick Start

```powershell
# 1. Clone
 git clone https://github.com/syahril-akbar/maganghub-report-scraper.git
 cd maganghub-report-scraper

# 2. Create isolated environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install Python dependency and browser
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium

# 4. Verify installation
python .\test_scrape_maganghub.py
python .\test_context_cleanup.py

# 5. Run
python .\scrape_maganghub.py
```

Expected verification output:

```text
parser checks: OK
playwright context cleanup: OK
```

## Usage

```powershell
python .\scrape_maganghub.py
```

Example range:

```text
Tanggal mulai [YYYY-MM-DD] (Enter = 2026-08-10): 2026-08-10
Tanggal akhir [YYYY-MM-DD] (Enter = 2026-09-04): 2026-09-04
```

When the browser opens:

1. Complete MagangHub SSO yourself.
2. Wait until the page returns to `Riwayat`.
3. Confirm the report detail is visible.
4. Return to PowerShell and press Enter.

Never enter a password in the terminal, code, Git config, or issue tracker.

## Output

A successful run creates a date-specific Markdown file:

```text
Laporan-Bulanan-Magang-2026-08-10_sd_2026-09-04.md
```

Example:

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

`OK` means the scraper found and validated all three report sections. `no report` is expected on national holidays or dates without a daily report.

## Architecture

```text
PowerShell
  │
  ├─ scrape_maganghub.py
  │    ├─ Playwright Chromium
  │    │    └─ Manual MagangHub SSO
  │    ├─ Direct report URL per date
  │    ├─ Safe text parser
  │    └─ Atomic Markdown writer
  │
  ├─ %LOCALAPPDATA%\MagangHubScraper\profile
  │    └─ Local-only authenticated browser session
  │
  └─ Laporan-Bulanan-Magang-*.md
```

## Project Layout

```text
maganghub-report-scraper/
├── scrape_maganghub.py          # Interactive scraper
├── test_scrape_maganghub.py     # Offline parser regression check
├── test_context_cleanup.py       # Playwright shutdown regression check
├── requirements.txt              # Pinned Python dependency
├── .gitignore                    # Protects session/runtime artifacts
├── logs/                         # Runtime logs; ignored
└── Laporan-Bulanan-Magang-*.md   # Generated private reports; ignored
```

## Requirements

| Component | Requirement |
|---|---|
| OS | Windows 10/11 |
| Python | 3.11+ |
| Internet | Active connection to MagangHub Monev/SSO |
| Account | Active MagangHub account |
| Browser | Playwright Chromium, installed via CLI |

## Safe Operation

- Interactive only. Do not run via cron or unattended automation; SSO needs human confirmation and the website UI can change.
- Browser session lives outside the project, preventing accidental cloud sync or Git commits.
- Browser context closes before Playwright stops, avoiding `Event loop is closed` shutdown errors.
- Logs are written to `logs/run-*.log` and only contain safe diagnostic details.
- Report output is generated only if at least one report succeeds.

To reset the login session, close any scraper browser then remove:

```text
%LOCALAPPDATA%\MagangHubScraper\profile
```

The next run will require a fresh login.

## Troubleshooting

### `ModuleNotFoundError: No module named 'playwright'`

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### `Page.goto: Timeout` or navigation interrupted

SSO is still redirecting or the connection is slow.

1. Close the browser opened by the script.
2. Run the script again.
3. Finish SSO.
4. Wait for the `Riwayat` page to settle.
5. Only then press Enter in PowerShell.

### `laporan atau tanggal tidak muncul`

Likely no report exists, the session expired, or the page did not finish loading. Login again and test a one-day range first.

### `tiga bagian laporan tidak lengkap`

Commonly a holiday or date with no daily report. If it occurs on a known report day, retain the safe log and inspect the current MagangHub page structure before changing the parser.

### `can't open file 'D:\MyProgram\...'`

Quote absolute paths containing spaces, or run from the project directory:

```powershell
cd D:\MyProgram\maganghub-report-scraper
python .\scrape_maganghub.py
```

## Development

Run checks after parser or browser lifecycle changes:

```powershell
python .\test_scrape_maganghub.py
python .\test_context_cleanup.py
python -m py_compile .\scrape_maganghub.py .\test_scrape_maganghub.py .\test_context_cleanup.py
```

Key implementation points:

| Component | Responsibility |
|---|---|
| `extract_report()` | Navigation, report validation, extraction |
| `report_sections()` | Three-section parser |
| `atomic_write()` | Safe output replacement |
| `safe_url()` | Removes sensitive URL query strings from logs |
| `PROFILE_DIR` | Local-only persistent browser session |

## Scope

This project reads reports available to the authenticated user. It does not create, edit, approve, or submit reports on MagangHub.

Use responsibly. MagangHub data remains subject to the applicable platform and institutional policies.

## License

No license is currently declared. All rights reserved unless the repository owner adds a license file.
