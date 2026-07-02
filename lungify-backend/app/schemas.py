from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    service: str
    status: str
    version: str
    message: str


class HealthResponse(BaseModel):
    status: str
    device: str
    model_status: str
    loaded_models: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)


class FinalAssessment(BaseModel):
    label: str
    risk_level: str
    confidence: float
    source: str


class SubtypeSuggestion(BaseModel):
    label: str
    confidence: float | None = None
    probabilities: dict[str, float] = Field(default_factory=dict)
    source: str


class SegmentationResult(BaseModel):
    available: bool
    mask_image_base64: str | None = None
    overlay_image_base64: str | None = None
    original_image_base64: str | None = None
    localization_scope: str | None = None
    source: str


class ReportBody(BaseModel):
    summary: str
    recommendation: str
    disclaimer: str


class PredictionResponse(BaseModel):
    request_id: str
    model_status: str
    input_mode: str
    final_assessment: FinalAssessment
    subtype_suggestion: SubtypeSuggestion
    segmentation: SegmentationResult
    report: ReportBody
    warnings: list[str] = Field(default_factory=list)
    processing_time_ms: int | None = None


class ModelInfoResponse(BaseModel):
    name: str
    status: str
    architecture: dict[str, Any]
    metrics: dict[str, Any]
    classes: dict[str, list[str]]
    limitations: list[str]

