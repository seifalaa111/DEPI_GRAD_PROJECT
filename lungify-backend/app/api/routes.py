from __future__ import annotations

import json
import logging
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from app.config import settings
from app.schemas import HealthResponse, ModelInfoResponse, PredictionResponse, StatusResponse
from app.services.report_builder import build_report, preview_report, sample_report
from app.utils.exceptions import LungifyError, ModelUnavailableError, ValidationError
from app.utils.validation import classify_upload, safe_extract_zip

logger = logging.getLogger("lungify")

router = APIRouter()


@router.get("/", response_model=StatusResponse)
def root() -> StatusResponse:
    return StatusResponse(
        service=settings.app_name,
        status="online",
        version=settings.app_version,
        message="Lungify AI backend is running.",
    )


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    registry = request.app.state.models
    loaded_models = registry.health()
    warnings = []
    if loaded_models.get("errors"):
        warnings.append("One or more model artifacts could not be loaded.")
    return HealthResponse(
        status="ok" if not warnings else "degraded",
        device=str(registry.device),
        model_status=settings.model_status,
        loaded_models=loaded_models,
        warnings=warnings,
    )


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info(request: Request) -> ModelInfoResponse:
    info = request.app.state.models.model_info()
    pipeline_a = info.get("pipeline_a", {})
    pipeline_b = info.get("pipeline_b", {})
    cv_summary = info.get("cv_summary", {})
    return ModelInfoResponse(
        name="Lungify CT cancer screening and tumor localization prototype",
        status=settings.model_status,
        architecture={
            "binary_screening": pipeline_a.get("model", {}),
            "subtype_and_segmentation": pipeline_b.get("model", {}),
        },
        metrics={
            "binary_metrics_note": "Binary CSV and confusion-matrix image may represent different evaluation sets.",
            "multiclass_cv": cv_summary,
            "pipeline_b_per_fold": pipeline_b.get("per_fold_val_metrics", {}),
        },
        classes={
            "binary": pipeline_a.get("inference", {}).get("class_names", ["Benign/Unknown", "Malignant"]),
            "multiclass": pipeline_b.get("inference", {}).get(
                "class_names", ["Benign/Unknown", "Primary Lung Ca", "Metastatic"]
            ),
        },
        limitations=[
            "Research prototype only; not for clinical diagnosis.",
            "Real inference requires a de-identified DICOM CT series ZIP.",
            "Segmentation is center-patch prototype localization for uploaded studies without XML nodule annotations.",
            "Subtype probabilities are support information and do not override the binary screening assessment.",
        ],
    )


@router.post("/predict/sample", response_model=PredictionResponse)
def predict_sample() -> PredictionResponse:
    body = sample_report()
    return PredictionResponse(
        request_id=_request_id(),
        input_mode="sample",
        processing_time_ms=0,
        **body,
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: Request,
    scan: UploadFile = File(...),
    metadata: str | None = Form(default=None),
) -> PredictionResponse:
    started = time.perf_counter()
    request_id = _request_id()
    try:
        parsed_metadata = _parse_metadata(metadata)
        input_mode, suffix = classify_upload(scan.filename, scan.size)
        with tempfile.TemporaryDirectory(prefix="lungify_") as tmp:
            tmp_path = Path(tmp)
            upload_path = tmp_path / f"upload{suffix}"
            with upload_path.open("wb") as handle:
                shutil.copyfileobj(scan.file, handle)

            if input_mode == "preview":
                body = preview_report(f"{suffix} uploads are preview-only because the real model expects a 3D DICOM series.")
                return PredictionResponse(
                    request_id=request_id,
                    input_mode="preview",
                    processing_time_ms=_elapsed_ms(started),
                    **body,
                )

            dicom_dir = safe_extract_zip(upload_path, tmp_path / "dicom_series")
            registry = request.app.state.models
            if not registry.pipeline_a.loaded:
                raise ModelUnavailableError("Binary cancer screening model is not loaded.")

            a_result = registry.pipeline_a.predict(dicom_dir, parsed_metadata)
            b_result = None
            warnings: list[str] = []
            if a_result["label"] == "Malignant":
                if registry.pipeline_b.loaded:
                    b_result = registry.pipeline_b.predict(dicom_dir)
                else:
                    warnings.append("Advanced subtype and segmentation model is not loaded.")
            body = build_report(a_result, b_result, input_mode="real", warnings=warnings)
            return PredictionResponse(
                request_id=request_id,
                input_mode="real",
                processing_time_ms=_elapsed_ms(started),
                **body,
            )
    except LungifyError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc
    except Exception as exc:
        logger.exception("Unexpected inference error (request_id=%s)", request_id)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "inference_error",
                "message": "Internal error while processing the scan. Please try again or contact support.",
            },
        ) from exc


def _parse_metadata(metadata: str | None) -> dict[str, Any] | None:
    if not metadata:
        return None
    try:
        parsed = json.loads(metadata)
    except json.JSONDecodeError as exc:
        raise ValidationError("metadata must be valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValidationError("metadata must be a JSON object.")
    return parsed


def _request_id() -> str:
    return f"LNG-{uuid.uuid4().hex[:10].upper()}"


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)

