from __future__ import annotations

import numpy as np
from scipy.ndimage import zoom


def clip_norm(vol: np.ndarray, hu_min: float, hu_max: float) -> np.ndarray:
    return ((np.clip(vol, hu_min, hu_max) - hu_min) / (hu_max - hu_min + 1e-8)).astype(np.float32)


def resample(vol: np.ndarray, spacing: tuple[float, float, float], target_spacing: tuple[float, float, float]) -> np.ndarray:
    factors = tuple(float(spacing[i]) / float(target_spacing[i]) for i in range(3))
    return zoom(vol, factors, order=1).astype(np.float32)


def crop_pad(vol: np.ndarray, shape: tuple[int, int, int]) -> np.ndarray:
    if vol.shape != shape:
        factors = tuple(shape[i] / vol.shape[i] for i in range(3))
        vol = zoom(vol, factors, order=1).astype(vol.dtype)
        return vol  
    
    return vol
    tz, ty, tx = shape
    z, y, x = vol.shape
    out = np.zeros(shape, dtype=vol.dtype)
    z0s = max((z - tz) // 2, 0)
    y0s = max((y - ty) // 2, 0)
    x0s = max((x - tx) // 2, 0)
    z1s = min(z0s + tz, z)
    y1s = min(y0s + ty, y)
    x1s = min(x0s + tx, x)
    cz, cy, cx = z1s - z0s, y1s - y0s, x1s - x0s
    z0d = max((tz - cz) // 2, 0)
    y0d = max((ty - cy) // 2, 0)
    x0d = max((tx - cx) // 2, 0)
    out[z0d : z0d + cz, y0d : y0d + cy, x0d : x0d + cx] = vol[z0s:z1s, y0s:y1s, x0s:x1s]
    return out

