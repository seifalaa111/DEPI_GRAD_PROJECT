from __future__ import annotations

from typing import Any

import numpy as np

from app.services.preprocessing_common import clip_norm, crop_pad, resample


def prepare_volume_a(volume: np.ndarray, spacing: tuple[float, float, float], bundle: dict[str, Any]) -> np.ndarray:
    target_spacing = tuple(float(v) for v in bundle["target_spacing"])
    target_shape = tuple(int(v) for v in bundle["target_shape"])
    vol = resample(volume, spacing, target_spacing)
    vol = clip_norm(vol, float(bundle["hu_min"]), float(bundle["hu_max"]))
    vol = crop_pad(vol, target_shape)
    return vol[None, None, ...].astype(np.float32)


def prepare_tabular_a(metadata: dict[str, Any] | None, bundle: dict[str, Any]) -> np.ndarray:
    scaler = bundle["scaler"]
    feature_cols = list(bundle["feature_cols"])
    raw_defaults = np.asarray(scaler.mean_, dtype=np.float32)
    raw_values = []
    metadata = metadata or {}
    for idx, col in enumerate(feature_cols):
        value = metadata.get(col, metadata.get(f"feature_{idx + 1}", raw_defaults[idx]))
        try:
            raw_values.append(float(value))
        except (TypeError, ValueError):
            raw_values.append(float(raw_defaults[idx]))
    raw = np.asarray(raw_values, dtype=np.float32).reshape(1, -1)
    return scaler.transform(raw).astype(np.float32)

