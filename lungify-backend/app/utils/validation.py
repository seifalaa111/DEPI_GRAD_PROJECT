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
    extracted_files = 0
    extracted_bytes = 0
    try:
        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                target = (destination / member.filename).resolve()
                if root not in target.parents and target != root:
                    raise ValidationError("ZIP contains unsafe file paths.")
                if member.is_dir():
                    continue
                extracted_files += 1
                extracted_bytes += int(member.file_size)
                if extracted_files > settings.max_dicom_files:
                    raise ValidationError(
                        f"ZIP contains too many files. Limit is {settings.max_dicom_files} extracted files."
                    )
                if extracted_bytes > settings.max_extracted_mb * 1024 * 1024:
                    raise ValidationError(
                        f"Extracted ZIP content exceeds the {settings.max_extracted_mb} MB safety limit."
                    )
            archive.extractall(destination)
    except zipfile.BadZipFile as exc:
        raise ValidationError("Uploaded ZIP is not a valid archive.") from exc
    return destination
