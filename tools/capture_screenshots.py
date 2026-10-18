"""Capture real screenshots of the live client sites and switch the portfolio to use them.

Run this on any computer with internet access:

    pip install playwright pillow
    playwright install chromium
    python3 tools/capture_screenshots.py

Use it to refresh the client-site screenshots. It overwrites
assets/images/projects/site-<name>-1600.webp and -800.webp (desktop, top of the
homepage, ~2.08:1 like the current images). The HTML already points at these files.
"""
import asyncio
from pathlib import Path
from io import BytesIO
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'images' / 'projects'
SITES = {
    'quickjumpstart': 'https://quickjumpstart.ae/',
    'glanpawspets': 'https://glanpawspets.com/',
    'batteryonline': 'https://batteryonline.ae/',
}


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=2)
        for name, url in SITES.items():
            print('capturing', url)
            await page.goto(url, wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(2500)  # let hero images and fonts settle
            png = await page.screenshot(clip={'x': 0, 'y': 0, 'width': 1440, 'height': 692})
            im = Image.open(BytesIO(png)).convert('RGB')
            for w in (1600, 800):
                dest = OUT / f'site-{name}-{w}.webp'
                im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(dest, quality=84, method=6)
                print('  saved', dest.relative_to(ROOT))
        await browser.close()

asyncio.run(main())
