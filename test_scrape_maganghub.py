"""Offline regression checks for MagangHub report parsing."""
from datetime import date

from scrape_maganghub import format_date_id, report_sections, safe_url


BODY = """
Riwayat Periode 1 LAPORAN HARIAN 10 Agustus 2026 DISETUJUI
Uraian Aktivitas Membuat laporan harian dan memeriksa data.
Pembelajaran yang Diperoleh Memahami alur verifikasi data.
Kendala yang Dialami Tidak ada kendala teknis.
Waktu Server 10:00 WITA Beranda
"""


def main() -> None:
    assert report_sections(BODY) == (
        "Membuat laporan harian dan memeriksa data.",
        "Memahami alur verifikasi data.",
        "Tidak ada kendala teknis.",
    )
    assert report_sections("LAPORAN HARIAN Uraian Aktivitas kosong") is None
    assert format_date_id(date(2026, 8, 10)) == "10 Agustus 2026"
    assert safe_url("https://example.test/sso/callback?code=secret&state=private") == "https://example.test/sso/callback"
    print("parser checks: OK")


if __name__ == "__main__":
    main()
