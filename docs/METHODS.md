# Method contracts

All five methods receive one immutable RGB uint8 original and the same `Event`. Coordinates are integers, source/target boxes are half-open, and source/target cannot overlap. The entire final image is created from an original copy; only the target rectangle is assigned new pixels.

## Direct copy (`hard`)

Assign the source patch directly to the target. All source patch pixels are preserved exactly. Background mismatch and rectangular boundaries are intentionally visible as a baseline.

## Feather (`feather`)

For each patch pixel, calculate its minimum distance `d` to the rectangular boundary. The transition width is `clip(round(0.15 * min(height, width)), 3, 18)`. Apply smoothstep `t²(3−2t)` to the clipped ratio `t=d/transition`, quantize alpha to 8-bit, then mix donor and recipient. The outermost ring is unchanged recipient; the full-alpha core equals donor exactly.

## Tone + feather (`tone_feather`)

Estimate the median recipient-minus-donor RGB difference in an outer ring 20% of the smaller patch dimension, round and clamp each channel to ±20, apply it to the donor, then feather. The copied center is no longer guaranteed to match original source pixels. The effective offset is saved in the manifest.

## Multiband (`multiband`)

Reflect-pad donor and recipient to multiples of eight. Construct three Gaussian reductions and Laplacian detail levels. Smooth and gate the alpha map, blend each level and reconstruct. Finally gate the reconstructed difference against the clean recipient using smooth alpha, retaining an exactly unchanged outer ring. This avoids the hard inner step caused by restoring only an outer border after unconstrained pyramid reconstruction. It is a boundary-constrained multiband variant, not an unmodified textbook baseline.

## Poisson (`poisson`)

Apply `cv2.seamlessClone` with `NORMAL_CLONE`, a full patch mask, and the target center. Verify its changes do not extend outside the target rectangle. Feather the resulting patch against the original recipient. The result may change the copied cell's intensity and contrast. It is explicitly **Poisson + feather restoration**, not a pure Poisson-only comparison. Save OpenCV version, mode, target box and center in effective parameters.

## Mask semantics

- Source mask: planned donor rectangle in original coordinates.
- Target mask: allowed target rectangle in original coordinates.
- Change mask: pixels where at least one RGB channel actually differs from original.

A planned mask is not a claim that every enclosed pixel changed. Counts indicate modification size, not perceptual quality. The sample intentionally includes an obvious direct-copy seam to illustrate algorithm differences; no method is auto-approved for image integrity or visual realism.

## Demo provenance and geometry

Original: CC0 `cell.png` from scikit-image 0.25.2, 550 × 660 pixels. Source `[315, 265, 535, 485]`; destination `[40, 65, 260, 285]`. No scale, rotation, denoising, recoloring or cropping is applied to full-size outputs beyond the stated method. Web close-ups include 20 pixels of surrounding context. Region outlines are browser overlays and are not burned into saved results.

Licenses and scientific reference: [NOTICE](../NOTICE.md). Source and output SHA256 values: [manifest](assets/demo/manifest.json).
