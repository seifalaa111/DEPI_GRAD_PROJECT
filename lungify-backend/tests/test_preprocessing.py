from __future__ import annotations

import numpy as np

from app.services.preprocessing_b import center_patch, place_patch_mask
from app.services.preprocessing_common import clip_norm, crop_pad


def test_crop_pad_shape():
    vol = np.ones((10, 20, 30), dtype=np.float32)
    out = crop_pad(vol, (12, 16, 28))
    assert out.shape == (12, 16, 28)


def test_clip_norm_bounds():
    vol = np.array([-1200, -1000, -300, 400, 900], dtype=np.float32)
    out = clip_norm(vol, -1000, 400)
    assert float(out.min()) >= 0.0
    assert float(out.max()) <= 1.0


def test_center_patch_and_reinsert_shape():
    img = np.zeros((2, 64, 128, 128), dtype=np.float32)
    patch, region = center_patch(img)
    assert patch.shape == (2, 32, 64, 64)
    mask = place_patch_mask(np.ones((32, 64, 64), dtype=np.float32), (64, 128, 128), region)
    assert mask.shape == (64, 128, 128)
    assert mask.sum() == 32 * 64 * 64

