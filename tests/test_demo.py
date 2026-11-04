"""Verify that the committed website and reproducible export agree."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from copymove_lab import METHODS, Event, render

ROOT = Path(__file__).resolve().parents[1]


def test_committed_assets_and_browser_data():
    demo = ROOT / "docs/assets/demo"
    data = json.loads((demo / "manifest.json").read_text(encoding="utf-8"))
    wrapper = (ROOT / "docs/assets/demo-data.js").read_text(encoding="utf-8")
    assert json.loads(wrapper.removeprefix("window.COPYMOVE_DEMO = ").removesuffix(";\n")) == data
    assert [method["id"] for method in data["methods"]] == list(METHODS)
    for name, digest in data["files_sha256"].items():
        assert Path(name).name == name
        assert hashlib.sha256((demo / name).read_bytes()).hexdigest() == digest
    source = np.array(Image.open(ROOT / "examples/cell/original.png").convert("RGB"))
    np.testing.assert_array_equal(np.array(Image.open(demo / data["original"])), source)
    allowed = np.zeros(source.shape[:2], bool)
    allowed[65:285, 40:260] = True
    for item in data["methods"]:
        image = np.array(Image.open(demo / item["image"]))
        np.testing.assert_array_equal(image[~allowed], source[~allowed])
        change = np.any(image != source, axis=2)
        np.testing.assert_array_equal(np.array(Image.open(demo / item["change_mask"])) > 0, change)
        assert item["changed_pixels"] == int(change.sum()) > 0


def test_real_demo_hard_result_reproduces_exactly():
    image = np.array(Image.open(ROOT / "examples/cell/original.png").convert("RGB"))
    actual, _ = render(image, Event((315, 265, 535, 485), (40, 65)), "hard")
    np.testing.assert_array_equal(actual, np.array(Image.open(ROOT / "docs/assets/demo/hard.png")))
