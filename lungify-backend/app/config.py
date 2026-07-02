from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Lungify AI Backend"
    app_version: str = "1.0.0"
    environment: str = os.getenv("LUNGIFY_ENV", "local")
    model_status: str = "real"
    device: str = os.getenv("LUNGIFY_DEVICE", "auto")
    skip_model_load: bool = os.getenv("LUNGIFY_SKIP_MODEL_LOAD", "0") == "1"
    max_upload_mb: int = int(os.getenv("LUNGIFY_MAX_UPLOAD_MB", "512"))
    max_extracted_mb: int = int(os.getenv("LUNGIFY_MAX_EXTRACTED_MB", "1024"))
    max_dicom_files: int = int(os.getenv("LUNGIFY_MAX_DICOM_FILES", "5000"))
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "LUNGIFY_CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    )
    allow_all_cors_origins: bool = cors_origins == ("*",)
    configs_dir: Path = ROOT_DIR / "configs"
    weights_dir: Path = ROOT_DIR / "weights"
    pipeline_a_weight: Path = ROOT_DIR / "weights" / "pipeline_a_model.pkl"
    pipeline_b_weights_dir: Path = ROOT_DIR / "weights" / "pipeline_b_models"
    pipeline_a_params: Path = ROOT_DIR / "configs" / "pipeline_a_params.json"
    pipeline_b_params: Path = ROOT_DIR / "configs" / "pipeline_b_params.json"
    cv_summary: Path = ROOT_DIR / "configs" / "cv_summary.json"


settings = Settings()
