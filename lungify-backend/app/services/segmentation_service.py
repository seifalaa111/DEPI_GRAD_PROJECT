from __future__ import annotations

import numpy as np

from app.utils.image_export import make_mask_png, make_original_png, make_overlay_png


def export_segmentation_images(image: np.ndarray, mask: np.ndarray) -> dict[str, str | int]:
    image_channel = image[0]
    per_slice = mask.reshape(mask.shape[0], -1).sum(axis=1)
    slice_idx = int(per_slice.argmax()) if float(per_slice.max()) > 0 else int(mask.shape[0] // 2)
    return {
        "slice_index": slice_idx,
        "original_image_base64": make_original_png(image_channel[slice_idx]),
        "mask_image_base64": make_mask_png(mask[slice_idx]),
        "overlay_image_base64": make_overlay_png(image_channel[slice_idx], mask[slice_idx]),
    }

