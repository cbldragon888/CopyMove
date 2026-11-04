"""Refresh the shipped static demo only from a verified export of the CC0 event."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def refresh(source: Path, root: Path) -> None:
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    provenance = json.loads((root / "examples/cell/provenance.json").read_text(encoding="utf-8"))
    if manifest["input_file_sha256"] != provenance["source_sha256"]:
        raise ValueError("This page is licensed and described for the bundled CC0 image only")
    if manifest["source_xyxy"] != [315, 265, 535, 485] or manifest["target_xyxy"] != [40, 65, 260, 285]:
        raise ValueError("The page's region labels require the documented demo coordinates")
    if [m["id"] for m in manifest["methods"]] != ["hard", "feather", "tone_feather", "multiband", "poisson"]:
        raise ValueError("The demo requires all five methods in the documented order")
    if (manifest["width"], manifest["height"]) != (550, 660):
        raise ValueError("Unexpected image size")
    files = manifest["files_sha256"]
    required = {manifest["original"], manifest["source_mask"], manifest["target_mask"]}
    for item in manifest["methods"]:
        required.update((item["image"], item["change_mask"]))
    if set(files) != required:
        raise ValueError("Image hashes and manifest references do not match")
    for name, digest in files.items():
        if Path(name).name != name or not name.endswith(".png"):
            raise ValueError("Asset names must be plain PNG filenames")
        actual = hashlib.sha256((source / name).read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"Hash mismatch: {name}")
    destination = root / "docs/assets/demo"
    if source.resolve() != destination.resolve():
        destination.mkdir(parents=True, exist_ok=True)
        for name in [*files, "manifest.json"]:
            shutil.copyfile(source / name, destination / name)
    data = "window.COPYMOVE_DEMO = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n"
    (root / "docs/assets/demo-data.js").write_text(data, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="source", type=Path, required=True)
    args = parser.parse_args()
    refresh(args.source, Path(__file__).resolve().parents[1])
    print("Static demo assets and data updated.")
