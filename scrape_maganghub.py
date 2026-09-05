"""Scrape laporan harian MagangHub Monev ke Markdown.

Login remains manual. Browser session is stored outside this project to prevent
cloud-sync or source-control exposure.
"""
from __future__ import annotations

import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

BASE_URL = "https://monev.maganghub.kemnaker.go.id/dashboard/riwayat?date={date}&view=detail"
START = date(2026, 8, 10)
END = date(2026, 9, 4)
PROJECT_DIR = Path(__file__).resolve().parent
LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
PROFILE_DIR = LOCAL_APP_DATA / "MagangHubScraper" / "profile"
LOG_DIR = PROJECT_DIR / "logs"
HEADINGS = ("Uraian Aktivitas", "Pembelajaran yang Diperoleh", "Kendala yang Dialami")
MONTH_ID = (
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
)


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def safe_url(url: str) -> str:
    """Return only origin and path. SSO query values can be credentials."""
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def log_line(log_file: Path, message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.parent.mkdir(exist_ok=True)
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(f"{stamp} {message}\n")


def report_sections(body: str) -> tuple[str, str, str] | None:
    """Extract the three report fields from normalized report-detail text."""
    detail_start = body.rfind("LAPORAN HARIAN")
    detail = body[detail_start:] if detail_start >= 0 else body
    activity = re.search(
        rf"{re.escape(HEADINGS[0])}\s+(.*?)(?=\s+{re.escape(HEADINGS[1])})",
        detail,
        re.DOTALL,
    )
    learning = re.search(
        rf"{re.escape(HEADINGS[1])}\s+(.*?)(?=\s+{re.escape(HEADINGS[2])})",
        detail,
        re.DOTALL,
    )
    obstacle = re.search(
        rf"{re.escape(HEADINGS[2])}\s+(.*?)(?=\s+(?:Waktu Server|Beranda)|$)",
        detail,
        re.DOTALL,
    )
    values = tuple(clean(item.group(1)) if item else "" for item in (activity, learning, obstacle))
    return values if all(values) else None


def wait_for_report(page, day: date) -> str | None:
    expected = f"{day.day} {MONTH_ID[day.month - 1]} {day.year}"
    for _ in range(30):
        body = clean(page.locator("body").inner_text())
        if "LAPORAN HARIAN" in body and expected in body:
            return body
        page.wait_for_timeout(1_000)
    return None


def extract_report(page, day: date, log_file: Path) -> dict | None:
    url = BASE_URL.format(date=day.isoformat())
    for attempt in range(3):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=120_000)
            break
        except Exception as error:
            if attempt == 2:
                log_line(log_file, f"{day} navigation failed: {type(error).__name__}")
                raise
            print(f"{day}: navigasi belum stabil, ulang {attempt + 1}/2")
            page.wait_for_timeout(5_000)

    body = wait_for_report(page, day)
    if body is None:
        message = f"{day}: laporan atau tanggal tidak muncul ({safe_url(page.url)})"
        print(message, file=sys.stderr)
        log_line(log_file, message)
        return None

    sections = report_sections(body)
    if sections is None:
        message = f"{day}: tiga bagian laporan tidak lengkap ({safe_url(page.url)})"
        print(message, file=sys.stderr)
        log_line(log_file, message)
        return None

    activity, learning, obstacle = sections
    return {
        "date": day,
        "status": "Disetujui" if "DISETUJUI" in body else "-",
        "attendance": "Hadir" if re.search(r"Kehadiran\s+Hadir", body) else "-",
        "activity": activity,
        "learning": learning,
        "obstacle": obstacle,
    }


def format_date_id(day: date) -> str:
    return f"{day.day:02d} {MONTH_ID[day.month - 1]} {day.year}"


def output_path(from_date: date, to_date: date) -> Path:
    return PROJECT_DIR / f"Laporan-Bulanan-Magang-{from_date.isoformat()}_sd_{to_date.isoformat()}.md"


def render(reports: list[dict], skipped: list[date], from_date: date, to_date: date) -> str:
    lines = [
        "# Laporan Bulanan Magang",
        "",
        "**Periode pelaporan:** 10 Agustus 2026–9 September 2026  ",
        f"**Cakupan data:** {format_date_id(from_date)}–{format_date_id(to_date)}  ",
        "**Sumber:** Riwayat MagangHub Monev, Periode 1",
        "",
    ]
    for report in reports:
        lines += [
            f"## {format_date_id(report['date'])}", "",
            f"**Status:** {report['status']}  ",
            f"**Kehadiran:** {report['attendance']}", "",
            "### Uraian Aktivitas", report["activity"], "",
            "### Pembelajaran yang Diperoleh", report["learning"], "",
            "### Kendala yang Dialami", report["obstacle"], "", "---", "",
        ]
    if skipped:
        lines += ["## Tidak Diekstrak", ""]
        lines += [f"- {format_date_id(item)}" for item in skipped]
        lines += [""]
    return "\n".join(lines)


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def ask_date(label: str, default: date) -> date:
    while True:
        raw = input(f"{label} [YYYY-MM-DD] (Enter = {default.isoformat()}): ").strip()
        try:
            return date.fromisoformat(raw) if raw else default
        except ValueError:
            print("Format salah. Contoh: 2026-08-10")


def main() -> int:
    print("=== Scraper Laporan MagangHub ===")
    from_date = ask_date("Tanggal mulai", START)
    to_date = ask_date("Tanggal akhir", END)
    while to_date < from_date:
        print("Tanggal akhir harus sama atau setelah tanggal mulai.")
        to_date = ask_date("Tanggal akhir", END)

    log_file = LOG_DIR / f"run-{datetime.now():%Y%m%d-%H%M%S}.log"
    log_line(log_file, f"run started: {from_date} through {to_date}")
    # The Playwright context manager closes the browser before its event loop stops.
    with sync_playwright() as playwright:
        PROFILE_DIR.parent.mkdir(parents=True, exist_ok=True)
        with playwright.chromium.launch_persistent_context(
            str(PROFILE_DIR), headless=False, viewport={"width": 1440, "height": 1000}
        ) as context:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(BASE_URL.format(date=from_date.isoformat()), wait_until="commit", timeout=120_000)
            input("Login manual bila perlu. Setelah kembali ke halaman Riwayat, tekan Enter... ")
            try:
                page.wait_for_url("**/dashboard/riwayat**", timeout=120_000)
                page.wait_for_timeout(3_000)
            except PlaywrightTimeoutError:
                print("Login belum kembali ke halaman Riwayat. Tutup browser, lalu jalankan ulang.")
                log_line(log_file, "run stopped: SSO did not return to riwayat")
                return 1

            reports, skipped = [], []
            current = from_date
            while current <= to_date:
                if current.weekday() < 5:
                    try:
                        report = extract_report(page, current, log_file)
                        (reports if report else skipped).append(report or current)
                        print(f"{current}: {'OK' if report else 'no report'}")
                    except Exception as error:
                        skipped.append(current)
                        print(f"{current}: ERROR {type(error).__name__}", file=sys.stderr)
                        log_line(log_file, f"{current}: extraction error {type(error).__name__}")
                current += timedelta(days=1)

            if not reports:
                print("Tidak ada laporan berhasil diambil. File Markdown lama tidak ditimpa.")
                log_line(log_file, "run completed: 0 reports; output preserved")
                return 1
            destination = output_path(from_date, to_date)
            atomic_write(destination, render(reports, skipped, from_date, to_date))
            print(f"Saved {len(reports)} reports: {destination}")
            log_line(log_file, f"run completed: {len(reports)} reports; output={destination.name}")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
