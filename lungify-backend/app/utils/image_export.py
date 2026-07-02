from __future__ import annotations

import base64
from io import BytesIO

import numpy as np
from PIL import Image


def png_base64(arr: np.ndarray) -> str:
    image = Image.fromarray(arr.astype(np.uint8))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def slice_to_uint8(slice_2d: np.ndarray) -> np.ndarray:
    arr = np.clip(slice_2d, 0, 1)
    return (arr * 255).astype(np.uint8)


def make_mask_png(mask_slice: np.ndarray) -> str:
    mask = (mask_slice > 0.5).astype(np.uint8) * 255
    rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
    rgba[..., 0] = 233
    rgba[..., 1] = 75
    rgba[..., 2] = 95
    rgba[..., 3] = mask
    return png_base64(rgba)


def make_overlay_png(image_slice: np.ndarray, mask_slice: np.ndarray) -> str:
    gray = slice_to_uint8(image_slice)
    rgb = np.stack([gray, gray, gray], axis=-1)
    active = mask_slice > 0.5
    overlay = rgb.copy()
    overlay[active, 0] = 233
    overlay[active, 1] = 75
    overlay[active, 2] = 95
    blended = (0.65 * rgb + 0.35 * overlay).astype(np.uint8)
    return png_base64(blended)


def make_original_png(image_slice: np.ndarray) -> str:
    return png_base64(slice_to_uint8(image_slice))

