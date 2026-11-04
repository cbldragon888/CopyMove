"""Optional real-browser smoke check: pip install playwright; playwright install chromium."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def check() -> None:
    output = ROOT / "runs/browser"
    output.mkdir(parents=True, exist_ok=True)
    demo_url = (ROOT / "docs/index.html").as_uri()
    report = {"errors": [], "checks": []}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 1120}, device_scale_factor=1)
            page.on("pageerror", lambda error: report["errors"].append(str(error)))
            page.on(
                "response",
                lambda response: (
                    report["errors"].append(f"HTTP {response.status}: {response.url}")
                    if response.status >= 400
                    else None
                ),
            )
            page.goto(demo_url, wait_until="load")
            page.wait_for_function("document.querySelector('#crop-after').width === 260")
            assert page.locator(".method-button").count() == 5
            for method in ("hard", "tone_feather", "multiband", "poisson", "feather"):
                page.locator(f'[data-method="{method}"]').click()
                page.wait_for_function(
                    "() => Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)"
                )
                assert page.locator("#download").get_attribute("href") == f"assets/demo/{method}.png"
                assert page.locator(f'[data-method="{method}"]').get_attribute("aria-pressed") == "true"
            report["checks"].append("All five methods load and update downloads")
            stage = page.locator("#image-stage").bounding_box()
            y = stage["y"] + stage["height"] * 0.5
            page.mouse.move(stage["x"] + stage["width"] * 0.25, y)
            page.mouse.down()
            page.mouse.move(stage["x"] + stage["width"] * 0.75, y, steps=10)
            page.mouse.up()
            assert 73 <= int(page.locator("#wipe").input_value()) <= 77
            page.locator("#wipe").focus()
            page.keyboard.press("Home")
            assert page.locator("#wipe").input_value() == "0"
            page.keyboard.press("End")
            assert page.locator("#wipe").input_value() == "100"
            report["checks"].append("Pointer drag and keyboard wipe endpoints")
            page.locator('[data-view="mask"]').click()
            assert page.locator("#mask").is_visible()
            assert page.locator("#wipe").is_hidden()
            assert page.locator("#annotations").is_hidden()
            page.locator('[data-view="result"]').click()
            assert page.locator("#mask").is_hidden()
            page.locator("#show-regions").uncheck()
            assert page.locator("#annotations").is_hidden()
            page.locator("#show-regions").check()
            assert page.locator("#annotations").is_visible()
            report["checks"].append("Result/mask views and region overlays")
            page.locator('[data-view="compare"]').click()
            page.locator("#wipe").fill("58")
            page.locator("#wipe").dispatch_event("input")
            page.locator("#copy-command").click()
            page.wait_for_function("document.querySelector('#copy-status').textContent.length > 0")
            assert page.locator("#copy-status").inner_text()
            page.evaluate("document.activeElement.blur(); window.scrollTo(0,0)")
            page.screenshot(path=str(output / "desktop.png"), full_page=True)
            page.screenshot(path=str(output / "hero.png"))
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            report["checks"].append("Desktop layout and copy-command feedback")
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(demo_url, wait_until="load")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.locator('[data-method="poisson"]').click()
            page.locator('[data-view="mask"]').click()
            assert page.locator("#mask").is_visible()
            page.screenshot(path=str(output / "mobile.png"), full_page=True)
            report["checks"].append("390px mobile layout and controls")
            page.goto((ROOT / "docs/index.html").as_uri(), wait_until="load")
            page.locator('[data-method="multiband"]').click()
            page.wait_for_function(
                "() => Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)"
            )
            assert page.locator("#download").get_attribute("href").endswith("multiband.png")
            report["checks"].append("Direct file:// opening without a web server")
            browser.close()
        if report["errors"]:
            raise AssertionError(report["errors"])
    finally:
        (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    check()
