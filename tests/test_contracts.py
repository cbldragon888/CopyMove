"""Test observable image contracts, independent of blending implementation."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from copymove_lab import METHODS, Event, render
from copymove_lab.__main__ import export

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def fixture_image():
    # Odd patch dimensions catch OpenCV placement and pyramid rounding errors.
    y, x = np.mgrid[:128, :160]
    image = np.stack(((x * 3 + y) % 256, (y * 5) % 256, (x + y * 2) % 256), axis=2).astype(np.uint8)
    image[13:30, 17:32] = [230, 40, 90]
    return image


@pytest.mark.parametrize("method", METHODS)
def test_unchanged_source_and_outside_target(fixture_image, method):
    original = fixture_image.copy()
    result, _ = render(fixture_image, Event((8, 8, 49, 53), (90, 65)), method)
    np.testing.assert_array_equal(fixture_image, original)
    allowed = np.zeros(original.shape[:2], dtype=bool)
    allowed[65:110, 90:131] = True
    np.testing.assert_array_equal(result[~allowed], original[~allowed])
    np.testing.assert_array_equal(result[8:53, 8:49], original[8:53, 8:49])
    assert np.any(result[allowed] != original[allowed])
    assert result.dtype == np.uint8 and result.shape == original.shape


def test_hard_copy_exact_coordinate_mapping(fixture_image):
    result, _ = render(fixture_image, Event((8, 8, 49, 53), (90, 65)), "hard")
    np.testing.assert_array_equal(result[65:110, 90:131], fixture_image[8:53, 8:49])


@pytest.mark.parametrize("method", METHODS[1:])
def test_blended_outer_border_unchanged(fixture_image, method):
    result, _ = render(fixture_image, Event((8, 8, 49, 53), (90, 65)), method)
    for ys, xs in ((65, slice(90, 131)), (109, slice(90, 131)), (slice(65, 110), 90), (slice(65, 110), 130)):
        np.testing.assert_array_equal(result[ys, xs], fixture_image[ys, xs])


@pytest.mark.parametrize(
    "event",
    [
        Event((0, 0, 40, 40), (20, 20)),
        Event((-1, 0, 40, 40), (80, 60)),
        Event((0, 0, 40, 40), (150, 100)),
        Event((0, 0, 10, 10), (80, 60)),
        Event((0, 0, 40, 40), (80.5, 60)),
    ],
)
def test_bad_geometry_rejected(fixture_image, event):
    with pytest.raises(ValueError):
        render(fixture_image, event, "hard")


def test_noop_rejected():
    with pytest.raises(ValueError, match="no changed pixels"):
        render(np.zeros((80, 80, 3), dtype=np.uint8), Event((0, 0, 20, 20), (40, 40)), "hard")


def test_export_masks_and_hashes(tmp_path, fixture_image):
    source = tmp_path / "source.png"
    Image.fromarray(fixture_image).save(source)
    target = tmp_path / "output"
    manifest = export(source, target, Event((8, 8, 49, 53), (90, 65)), list(METHODS))
    assert manifest == json.loads((target / "manifest.json").read_text())
    for item in manifest["methods"]:
        result = np.array(Image.open(target / item["image"]))
        mask = np.array(Image.open(target / item["change_mask"])) > 0
        np.testing.assert_array_equal(mask, np.any(result != fixture_image, axis=2))
        assert int(mask.sum()) == item["changed_pixels"]
    for name, digest in manifest["files_sha256"].items():
        assert hashlib.sha256((target / name).read_bytes()).hexdigest() == digest
    with pytest.raises(ValueError, match="new or empty"):
        export(source, target, Event((8, 8, 49, 53), (90, 65)), ["hard"])


def test_cc0_source_matches_published_registry():
    source = ROOT / "examples/cell/original.png"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == (
        "8d23a7fb81f7cc877cd09f330357fc7f595651306e84e17252f6e0a1b3f61515"
    )
