from __future__ import annotations

import zipfile
from pathlib import Path

from app.config import settings
from app.utils.exceptions import ValidationError


REAL_EXTENSIONS = {".zip"}
PREVIEW_EXTENSIONS = {".dcm", ".png", ".jpg", ".jpeg"}
ALLOWED_EXTENSIONS = REAL_EXTENSIONS | PREVIEW_EXTENSIONS


def classify_upload(filename: str | None, size_bytes: int | None = None) -> tuple[str, str]:
    if not filename:
        raise ValidationError("Uploaded scan must include a filename.")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Unsupported file type. Upload a DICOM series as .zip, or use .dcm/.png/.jpg for preview mode."
        )
    if size_bytes is not None and size_bytes > settings.max_upload_mb * 1024 * 1024:
        raise ValidationError(f"Upload is larger than the {settings.max_upload_mb} MB limit.")
    return ("real", suffix) if suffix in REAL_EXTENSIONS else ("preview", suffix)


def safe_extract_zip(zip_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    try:
        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                target = (destination / member.filename).resolve()
                if root not in target.parents and target != root:
                    raise ValidationError("ZIP contains unsafe file paths.")
            archive.extractall(destination)
    except zipfile.BadZipFile as exc:
        raise ValidationError("Uploaded ZIP is not a valid archive.") from exc
    return destination

