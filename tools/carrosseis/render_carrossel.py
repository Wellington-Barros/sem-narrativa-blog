import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

html = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
    page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
    page.goto(html.as_uri())
    page.wait_for_timeout(800)
    slides = page.query_selector_all("section.s")
    for i, s in enumerate(slides, 1):
        over = s.evaluate("el => [...el.querySelectorAll('*')].filter(c => { const r = c.getBoundingClientRect(), b = el.getBoundingClientRect(); return r.bottom > b.bottom - 95 && !c.closest('.foot') && !c.classList.contains('wave') && !c.classList.contains('foot'); }).length")
        name = out / f"slide{i:02d}.png"
        s.screenshot(path=str(name))
        print(name.name, "possivel sobreposicao" if over else "ok")
    browser.close()
