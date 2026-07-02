from __future__ import annotations

from pathlib import Path

import numpy as np
import pydicom
from scipy.ndimage import zoom as _zoom


def discover_dicom_files(dicom_dir: Path) -> list[Path]:
    files = [p for p in dicom_dir.rglob("*") if p.is_file()]
    readable: list[Path] = []
    for fp in files:
        try:
            ds = pydicom.dcmread(str(fp), force=True, stop_before_pixels=True)
            if hasattr(ds, "SOPInstanceUID") or fp.suffix.lower() == ".dcm":
                readable.append(fp)
        except Exception:
            continue
    return readable


def load_dicom_series(dicom_dir: Path) -> tuple[np.ndarray, tuple[float, float, float]]:
    files = discover_dicom_files(dicom_dir)
    slices = []
    for fp in files:
        try:
            ds = pydicom.dcmread(str(fp), force=True)
            if hasattr(ds, "PixelData"):
                slices.append(ds)
        except Exception:
            continue
    if not slices:
        raise ValueError(f"No readable DICOM slices found in {dicom_dir}")

    def sort_key(ds) -> float:
        try:
            return float(ds.ImagePositionPatient[2])
        except Exception:
            try:
                return float(ds.InstanceNumber)
            except Exception:
                return 0.0

    slices.sort(key=sort_key)

    # ← التعديل هنا: 512×512 ثابت
    vol = np.empty((len(slices), 512, 512), dtype=np.float32)

    for idx, ds in enumerate(slices):
        raw = ds.pixel_array.astype(np.float32)
        slope = float(getattr(ds, "RescaleSlope", 1.0))
        intercept = float(getattr(ds, "RescaleIntercept", 0.0))
        raw_hu = raw * slope + intercept

        # ← التعديل هنا: resize لو مش 512×512
        if raw_hu.shape != (512, 512):
            zy = 512 / raw_hu.shape[0]
            zx = 512 / raw_hu.shape[1]
            raw_hu = _zoom(raw_hu, (zy, zx), order=1)

        vol[idx] = raw_hu

    try:
        zs = [float(ds.ImagePositionPatient[2]) for ds in slices]
        z_spacing = abs(zs[1] - zs[0]) if len(zs) > 1 else float(getattr(slices[0], "SliceThickness", 1.0))
        z_spacing = z_spacing or float(getattr(slices[0], "SliceThickness", 1.0))
    except Exception:
        z_spacing = float(getattr(slices[0], "SliceThickness", 1.0))

    pixel_spacing = getattr(slices[0], "PixelSpacing", [1.0, 1.0])
    spacing = (z_spacing, float(pixel_spacing[0]), float(pixel_spacing[1]))
    return vol, spacing