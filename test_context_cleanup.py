"""Regression check: browser context closes before Playwright stops."""
from pathlib import Path
from tempfile import TemporaryDirectory

from playwright.sync_api import sync_playwright


with TemporaryDirectory() as folder:
    with sync_playwright() as playwright:
        with playwright.chromium.launch_persistent_context(
            str(Path(folder) / "profile"), headless=True
        ) as context:
            assert context.pages

print("playwright context cleanup: OK")
