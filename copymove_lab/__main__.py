"""Command line export of native images, masks and comparison metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from PIL import __version__ as pillow_version

from . import __version__
from .core import METHODS, Event, rectangle_mask, render


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(image_path: Path, output_dir: Path, event: Event, methods: list[str]) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Output directory must be new or empty; existing results are preserved")
    with Image.open(image_path) as source:
        image = np.asarray(source.convert("RGB"))
    event.validate(image.shape)
    if not methods or len(set(methods)) != len(methods):
        raise ValueError("Select at least one method, without duplicates")
    # Validate and calculate first, so invalid geometry leaves no partial export.
    outputs = [(method, *render(image, event, method)) for method in methods]
    output_dir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(output_dir / "original.png")
    for name, box in (("source-mask", event.source), ("target-mask", event.destination)):
        Image.fromarray(rectangle_mask(image.shape, box)).save(output_dir / f"{name}.png")
    items = []
    for method, result, parameters in outputs:
        filename = f"{method}.png"
        Image.fromarray(result).save(output_dir / filename)
        changed = np.any(result != image, axis=2)
        change_file = f"{method}-changes.png"
        Image.fromarray(changed.astype(np.uint8) * 255).save(output_dir / change_file)
        outside = changed & (rectangle_mask(image.shape, event.destination) == 0)
        if outside.any():
            raise RuntimeError("Pixel-preservation contract failed")
        items.append(
            {
                "id": method,
                "image": filename,
                "change_mask": change_file,
                "sha256": sha256(output_dir / filename),
                "changed_pixels": int(changed.sum()),
                "parameters": parameters,
            }
        )
    manifest = {
        "schema_version": 1,
        "tool_version": __version__,
        "purpose": "Synthetic copy-move demonstration; not an experimental observation or benchmark.",
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
        "coordinate_convention": "integer half-open xyxy, native pixels, no EXIF rotation",
        "source_xyxy": list(event.source),
        "target_xyxy": list(event.destination),
        "input_file_sha256": sha256(image_path),
        "original": "original.png",
        "original_sha256": sha256(output_dir / "original.png"),
        "source_mask": "source-mask.png",
        "target_mask": "target-mask.png",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "opencv": cv2.__version__,
            "pillow": pillow_version,
        },
        "methods": items,
    }
    # Includes every image hash, not just the result images.
    manifest["files_sha256"] = {p.name: sha256(p) for p in sorted(output_dir.glob("*.png"))}
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate reproducible copy-move method comparisons")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--source", nargs=4, type=int, required=True, metavar=("X0", "Y0", "X1", "Y1"))
    parser.add_argument("--target", nargs=2, type=int, required=True, metavar=("X", "Y"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=list(METHODS))
    args = parser.parse_args()
    try:
        result = export(args.image, args.output, Event(tuple(args.source), tuple(args.target)), args.methods)
    except (ValueError, OSError, cv2.error) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"Generated {len(result['methods'])} methods at {args.output}")


if __name__ == "__main__":
    main()
