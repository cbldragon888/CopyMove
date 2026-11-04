"""Geometry and pixel-preservation contracts shared by all methods."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .kernels import _blend, _feather_alpha, _multiband, _poisson, _tone_donor

METHODS = ("hard", "feather", "tone_feather", "multiband", "poisson")


@dataclass(frozen=True)
class Event:
    """Integer, half-open source rectangle and target top-left, in native pixels."""

    source: tuple[int, int, int, int]
    target: tuple[int, int]

    @property
    def destination(self) -> tuple[int, int, int, int]:
        x0, y0, x1, y1 = self.source
        x, y = self.target
        return x, y, x + x1 - x0, y + y1 - y0

    def validate(self, shape: tuple[int, ...]) -> None:
        if len(self.source) != 4 or len(self.target) != 2:
            raise ValueError("Expected source x0 y0 x1 y1 and target x y")
        if any(type(v) is not int for v in (*self.source, *self.target)):
            raise ValueError("Coordinates must be integers")
        height, width = shape[:2]
        for name, (x0, y0, x1, y1) in (("Source", self.source), ("Target", self.destination)):
            if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
                raise ValueError(f"{name} rectangle lies outside the image or is empty")
            if min(x1 - x0, y1 - y0) < 16:
                raise ValueError("Patch must be at least 16 x 16 pixels")
        a, b = self.source, self.destination
        if max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3]):
            raise ValueError("Source and target must not overlap")


def rectangle_mask(shape: tuple[int, ...], box: tuple[int, int, int, int]) -> np.ndarray:
    mask = np.zeros(shape[:2], dtype=np.uint8)
    x0, y0, x1, y1 = box
    mask[y0:y1, x0:x1] = 255
    return mask


def render(image: np.ndarray, event: Event, method: str) -> tuple[np.ndarray, dict]:
    """Return a new RGB uint8 image and effective parameters; never mutate input."""
    if image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8:
        raise ValueError("Expected an RGB uint8 image")
    if method not in METHODS:
        raise ValueError(f"Unknown method: {method}")
    event.validate(image.shape)
    sx, sy, ex, ey = event.source
    x, y, right, bottom = event.destination
    donor = image[sy:ey, sx:ex].copy()
    recipient = image[y:bottom, x:right]
    alpha, depth, transition = _feather_alpha(*donor.shape[:2])
    parameters: dict = {"method": method}
    if method == "hard":
        patch = donor
    elif method == "feather":
        patch = _blend(recipient, donor, alpha)
        parameters["transition_px"] = transition
    elif method == "tone_feather":
        adjusted, shift = _tone_donor(donor, recipient, depth)
        patch = _blend(recipient, adjusted, alpha)
        parameters.update(transition_px=transition, rgb_offset=shift)
    elif method == "multiband":
        patch, settings = _multiband(donor, recipient, alpha, depth)
        parameters.update(settings)
    else:
        patch, settings = _poisson(image, donor, event.destination, alpha)
        parameters.update(settings)
    output = image.copy()
    output[y:bottom, x:right] = patch
    if np.array_equal(output, image):
        raise ValueError(f"{method} produced no changed pixels; choose a meaningful event")
    return output, parameters
