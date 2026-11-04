---
name: copymove-lab
description: Create reproducible scientific copy-move image examples with CopyMove Lab, compare five classical blending methods, inspect source/target regions and export images, masks and parameters. Use for copy-move demonstrations and method comparisons, not ordinary illustration generation.
---

# CopyMove Lab

Locate the repository containing `pyproject.toml` and `copymove_lab/`; after installing this skill elsewhere, use the user's checkout rather than assuming a home-directory path. Read the repository's `docs/METHODS.md` when selecting or explaining a method, and `NOTICE.md` before redistributing the bundled image.

## Prepare a meaningful event

The bundled CC0 example is immediately reusable. For another image, record its source and redistribution terms. Actually view the native original and exact source crop: select a complete cell or other meaningful object, retain background around it, and avoid annotations, cut objects or incompatible target regions.

Coordinates are native pixels, with a half-open source box and a target top-left. Both regions must be in bounds and non-overlapping, at least 16 × 16 pixels. CLI converts to RGB uint8 without EXIF rotation; normalize orientation before choosing coordinates if needed.

## Generate and inspect

From the repository root:

```sh
python -m pip install -e .
python -m copymove_lab --image examples/cell/original.png --source 315 265 535 485 --target 40 65 --output runs/cell
```

Use a new output directory for each changed experiment. Five methods share exactly the same event: hard, feather, tone_feather, multiband, poisson. No network service is called. Never label these outputs as AI-generated methods.

Inspect the source crop, target before/after and full native results. A valid pixel mask is not visual approval. Preserve the intended object, look for rectangular brightness seams and meaningful changes, and describe visible limitations honestly. Direct-copy seams are expected in an instructional comparison.

## Explain the output accurately

The manifest records effective parameters, coordinates, versions and hashes. Planned source/target masks differ from actual change masks. Hard copy preserves the whole donor exactly; feather preserves the center; other methods may change content intensity. Poisson includes feather restoration; multiband includes boundary gating.

Every full output keeps original dimensions and pixels outside the target. One original with five versions remains one example, not five independent benchmark samples. Label edited images as synthetic research demonstrations.

## Present

Open `docs/index.html` for the bundled offline explorer. To update its bundled sample after regenerating the same image/event, run `python scripts/update_demo.py --from runs/cell`. A different public source also requires updating the license notice, provenance and page copy; the update script deliberately rejects that substitution.

For custom experiments, deliver the CLI output directory and source attribution. Keep local paths, keys and private logs out of public repositories. Repository publication follows the user's chosen destination; this skill does not authorize an external push.
