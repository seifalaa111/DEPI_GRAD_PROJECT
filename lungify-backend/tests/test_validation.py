from __future__ import annotations

import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.utils.exceptions import ValidationError
from app.utils.validation import safe_extract_zip


def test_safe_extract_zip_rejects_path_traversal(tmp_path: Path):
    zip_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("../escape.dcm", b"bad")

    with pytest.raises(ValidationError, match="unsafe file paths"):
        safe_extract_zip(zip_path, tmp_path / "out")


def test_safe_extract_zip_rejects_excessive_file_count(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.utils.validation.settings",
        SimpleNamespace(max_dicom_files=1, max_extracted_mb=1024),
    )
    zip_path = tmp_path / "too_many.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("a.dcm", b"a")
        archive.writestr("b.dcm", b"b")

    with pytest.raises(ValidationError, match="too many files"):
        safe_extract_zip(zip_path, tmp_path / "out")
