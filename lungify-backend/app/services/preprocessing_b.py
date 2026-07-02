from __future__ import annotations

from typing import Any

import numpy as np

from app.services.preprocessing_common import clip_norm, crop_pad, resample


PATCH_SHAPE = (32, 64, 64)


def prepare_volume_b(volume: np.ndarray, spacing: tuple[float, float, float], bundle: dict[str, Any]) -> np.ndarray:
    target_spacing = tuple(float(v) for v in bundle["target_spacing"])
    target_shape = tuple(int(v) for v in bundle["target_shape"])
    vol = resample(volume, spacing, target_spacing)
    vol = crop_pad(vol, target_shape)
    ch0 = clip_norm(vol, float(bundle["hu_min"]), float(bundle["hu_max"]))
    ch1 = clip_norm(vol, float(bundle["hu_lung_min"]), float(bundle["hu_lung_max"]))
    return np.stack([ch0, ch1], axis=0).astype(np.float32)


def center_patch(img: np.ndarray, patch_shape: tuple[int, int, int] = PATCH_SHAPE) -> tuple[np.ndarray, tuple[slice, slice, slice]]:
    _, z, y, x = img.shape
    pz, py, px = patch_shape
    z0 = max((z - pz) // 2, 0)
    y0 = max((y - py) // 2, 0)
    x0 = max((x - px) // 2, 0)
    patch = img[:, z0 : z0 + pz, y0 : y0 + py, x0 : x0 + px]
    if patch.shape[1:] == patch_shape:
        return patch.astype(np.float32), (slice(z0, z0 + pz), slice(y0, y0 + py), slice(x0, x0 + px))

    out = np.zeros((img.shape[0], *patch_shape), dtype=np.float32)
    dz, dy, dx = patch.shape[1:]
    out[:, :dz, :dy, :dx] = patch
    return out, (slice(z0, z0 + dz), slice(y0, y0 + dy), slice(x0, x0 + dx))


def place_patch_mask(mask_patch: np.ndarray, target_shape: tuple[int, int, int], region: tuple[slice, slice, slice]) -> np.ndarray:
    mask = np.zeros(target_shape, dtype=np.float32)
    z_sl, y_sl, x_sl = region
    dz = z_sl.stop - z_sl.start
    dy = y_sl.stop - y_sl.start
    dx = x_sl.stop - x_sl.start
    mask[z_sl, y_sl, x_sl] = mask_patch[:dz, :dy, :dx]
    return mask

