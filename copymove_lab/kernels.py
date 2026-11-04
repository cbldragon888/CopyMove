"""Local blending kernels, isolated from the original research workflow.

Multiband fusion gates the reconstructed difference against the recipient;
this avoids the inner seam created by restoring only the outermost ring.
"""

from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np


def _smoothstep(value: np.ndarray) -> np.ndarray:
    t = np.clip(value, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _feather_alpha(height: int, width: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Smoothstep alpha, exactly zero on the outermost pixel and one in the core."""
    transition = int(np.clip(round(min(height, width) * 0.15), 3, 18))
    yy, xx = np.mgrid[0:height, 0:width]
    depth = np.minimum.reduce((xx, width - 1 - xx, yy, height - 1 - yy)).astype(np.int32)
    alpha = _smoothstep(depth.astype(np.float32) / transition)
    alpha[depth == 0] = 0.0
    alpha[depth >= transition] = 1.0
    return np.rint(alpha * 255.0).astype(np.uint8), depth, transition


def _blend(recipient: np.ndarray, donor: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    weight = alpha.astype(np.float32)[..., None] / 255.0
    mixed = weight * donor.astype(np.float32) + (1.0 - weight) * recipient.astype(np.float32)
    return np.clip(np.rint(mixed), 0, 255).astype(np.uint8)


def _tone_donor(donor: np.ndarray, recipient: np.ndarray, depth: np.ndarray) -> tuple[np.ndarray, list[int]]:
    ring = depth < max(2, round(min(depth.shape) * 0.20))
    delta = np.median(recipient.astype(np.float32)[ring] - donor.astype(np.float32)[ring], axis=0)
    delta = np.clip(np.rint(delta), -20, 20)
    adjusted = np.clip(donor.astype(np.float32) + delta, 0, 255)
    return np.rint(adjusted).astype(np.uint8), [int(v) for v in delta]


def _multiband(
    donor: np.ndarray, recipient: np.ndarray, alpha8: np.ndarray, depth: np.ndarray, levels: int = 3
) -> tuple[np.ndarray, dict[str, Any]]:
    """Laplacian/Gaussian-alpha fusion on a reflected local patch."""
    height, width = alpha8.shape
    multiple = 2**levels
    pad_h = int(math.ceil(height / multiple) * multiple)
    pad_w = int(math.ceil(width / multiple) * multiple)
    pad = ((0, pad_h - height), (0, pad_w - width), (0, 0))

    donor_p = cv2.copyMakeBorder(donor, *pad[0], *pad[1], cv2.BORDER_REFLECT_101)
    recipient_p = cv2.copyMakeBorder(recipient, *pad[0], *pad[1], cv2.BORDER_REFLECT_101)
    alpha_p = cv2.copyMakeBorder(
        alpha8.astype(np.float32) / 255.0,
        pad[0][0],
        pad[0][1],
        pad[1][0],
        pad[1][1],
        cv2.BORDER_CONSTANT,
        value=0.0,
    )
    blur = cv2.GaussianBlur(alpha_p, (0, 0), 1.0)
    transition = int(np.clip(round(min(height, width) * 0.15), 3, 18))
    ramp = _smoothstep(depth.astype(np.float32) / transition)
    ramp = cv2.copyMakeBorder(
        ramp, pad[0][0], pad[0][1], pad[1][0], pad[1][1], cv2.BORDER_CONSTANT, value=0.0
    )
    smooth_alpha = np.clip(blur * ramp, 0.0, 1.0)

    gd: list[np.ndarray] = [donor_p.astype(np.float32)]
    gr: list[np.ndarray] = [recipient_p.astype(np.float32)]
    ga: list[np.ndarray] = [smooth_alpha]
    for _ in range(levels):
        gd.append(cv2.pyrDown(gd[-1]))
        gr.append(cv2.pyrDown(gr[-1]))
        ga.append(cv2.resize(ga[-1], (gd[-1].shape[1], gd[-1].shape[0]), interpolation=cv2.INTER_AREA))

    lap_d, lap_r = [], []
    for level in range(levels):
        size = (gd[level].shape[1], gd[level].shape[0])
        lap_d.append(gd[level] - cv2.pyrUp(gd[level + 1], dstsize=size))
        lap_r.append(gr[level] - cv2.pyrUp(gr[level + 1], dstsize=size))
    fused = [ga[i][..., None] * lap_d[i] + (1.0 - ga[i][..., None]) * lap_r[i] for i in range(levels)]
    base = ga[levels][..., None] * gd[levels] + (1.0 - ga[levels][..., None]) * gr[levels]
    reconstructed = base
    for level in range(levels - 1, -1, -1):
        reconstructed = (
            cv2.pyrUp(reconstructed, dstsize=(fused[level].shape[1], fused[level].shape[0])) + fused[level]
        )
    # The pyramid carries low-frequency donor content inward. Restoring only
    # depth==0 therefore creates a hard inner step. Gate the reconstructed
    # difference against the clean recipient with the same smooth alpha, then
    # still enforce the exact alpha-zero ring.
    clean = recipient.astype(np.float32)
    gate = smooth_alpha[:height, :width][..., None]
    gated = clean + gate * (reconstructed[:height, :width] - clean)
    patch = np.clip(np.rint(gated), 0, 255).astype(np.uint8)
    patch[depth == 0] = recipient[depth == 0]
    return patch, {
        "levels": levels,
        "gaussian_sigma": 1.0,
        "padded_size_wh": [pad_w, pad_h],
        "alpha_edge_zero": True,
        "alpha_core_max": round(float(smooth_alpha.max()), 6),
        "boundary_gate": "recipient+smooth_alpha*(reconstructed-recipient)",
        "boundary_gate_zero_at_depth0": True,
    }


def _poisson(
    original: np.ndarray, donor: np.ndarray, dst: tuple[int, int, int, int], alpha8: np.ndarray
) -> tuple[np.ndarray, dict[str, Any]]:
    x0, y0, x1, y1 = dst
    height, width = donor.shape[:2]
    mask = np.full((height, width), 255, dtype=np.uint8)
    center = (x0 + width // 2, y0 + height // 2)
    cloned = cv2.seamlessClone(donor, original.copy(), mask, center, cv2.NORMAL_CLONE)
    changed = np.any(cloned != original, axis=2)
    outside = changed.copy()
    outside[y0:y1, x0:x1] = False
    if bool(outside.any()):
        raise RuntimeError(f"Poisson placement exceeded target bbox: {int(outside.sum())} pixels")
    if not bool(changed.any()):
        raise RuntimeError("Poisson produced no changed pixels")
    clone_patch = cloned[y0:y1, x0:x1]
    patch = _blend(original[y0:y1, x0:x1], clone_patch, alpha8)
    return patch, {
        "opencv_version": cv2.__version__,
        "flags": "NORMAL_CLONE",
        "center_xy": [int(center[0]), int(center[1])],
        "bbox_xyxy": [int(x0), int(y0), int(x1), int(y1)],
        "placement_formula": "p=(x0+w//2, y0+h//2)",
        "changed_bbox_source": "seamlessClone output",
        "smooth_alpha_restoration": True,
    }
