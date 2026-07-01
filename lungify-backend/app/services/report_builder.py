from __future__ import annotations

from typing import Any


DISCLAIMER = (
    "Lungify is a research prototype and clinical decision-support concept. It is not a replacement "
    "for radiologists, medical diagnosis, or professional clinical judgment."
)


def risk_level(label: str, confidence: float) -> str:
    if label == "Benign/Unknown":
        return "Low"
    if confidence >= 0.85:
        return "High"
    if confidence >= 0.65:
        return "Moderate"
    return "Low confidence / needs review"


def build_report(
    pipeline_a: dict[str, Any],
    pipeline_b: dict[str, Any] | None,
    *,
    input_mode: str,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    warnings = warnings or []
    label = pipeline_a["label"]
    confidence = float(pipeline_a["confidence"])
    risk = risk_level(label, confidence)

    if label == "Malignant" and pipeline_b is not None:
        subtype = {
            "label": pipeline_b["label"],
            "confidence": pipeline_b["confidence"],
            "probabilities": pipeline_b["probabilities"],
            "source": pipeline_b["source"],
        }
        segmentation = pipeline_b["segmentation"]
        summary = (
            f"The uploaded CT scan shows a {risk.lower()} malignant prediction with suspected tumor "
            "localization available for review."
        )
        recommendation = "Radiologist review is recommended."
    elif label == "Malignant":
        subtype = {
            "label": "Unavailable",
            "confidence": None,
            "probabilities": {},
            "source": "Multiclass Extension Engine",
        }
        segmentation = {
            "available": False,
            "mask_image_base64": None,
            "overlay_image_base64": None,
            "original_image_base64": None,
            "localization_scope": None,
            "source": "3D U-Net Tumor Segmentation",
        }
        summary = "The uploaded CT scan shows a malignant prediction. Advanced localization was unavailable."
        recommendation = "Radiologist review is recommended."
    else:
        subtype = {
            "label": "Not applicable",
            "confidence": None,
            "probabilities": {},
            "source": "Multiclass Extension Engine",
        }
        segmentation = {
            "available": False,
            "mask_image_base64": None,
            "overlay_image_base64": None,
            "original_image_base64": None,
            "localization_scope": None,
            "source": "3D U-Net Tumor Segmentation",
        }
        summary = "The uploaded CT scan is not classified as malignant by the cancer screening engine."
        recommendation = "Routine clinical review is recommended if symptoms, history, or radiology findings warrant it."

    return {
        "model_status": "real" if input_mode == "real" else "preview",
        "final_assessment": {
            "label": label,
            "risk_level": risk,
            "confidence": round(confidence, 4),
            "source": pipeline_a["source"],
        },
        "subtype_suggestion": subtype,
        "segmentation": segmentation,
        "report": {
            "summary": summary,
            "recommendation": recommendation,
            "disclaimer": DISCLAIMER,
        },
        "warnings": warnings,
    }


def preview_report(reason: str) -> dict[str, Any]:
    warnings = [reason, "Upload a DICOM series as .zip for real 3D model inference."]
    return {
        "model_status": "preview",
        "final_assessment": {
            "label": "Preview only",
            "risk_level": "Unavailable",
            "confidence": 0.0,
            "source": "Binary Cancer Screening Engine",
        },
        "subtype_suggestion": {
            "label": "Not available in preview mode",
            "confidence": None,
            "probabilities": {},
            "source": "Multiclass Extension Engine",
        },
        "segmentation": {
            "available": False,
            "mask_image_base64": None,
            "overlay_image_base64": None,
            "original_image_base64": None,
            "localization_scope": None,
            "source": "3D U-Net Tumor Segmentation",
        },
        "report": {
            "summary": "This upload was accepted for interface preview only; no 3D CT model inference was run.",
            "recommendation": "Upload a de-identified DICOM series ZIP to generate a real Lungify AI report.",
            "disclaimer": DISCLAIMER,
        },
        "warnings": warnings,
    }


def sample_report() -> dict[str, Any]:
    return {
        "model_status": "sample",
        "final_assessment": {
            "label": "Malignant",
            "risk_level": "High",
            "confidence": 0.87,
            "source": "Binary Cancer Screening Engine",
        },
        "subtype_suggestion": {
            "label": "Primary Lung Cancer",
            "confidence": 0.72,
            "probabilities": {
                "Benign/Unknown": 0.08,
                "Primary Lung Ca": 0.72,
                "Metastatic": 0.2,
            },
            "source": "Multiclass Extension Engine",
        },
        "segmentation": {
            "available": True,
            "mask_image_base64": None,
            "overlay_image_base64": None,
            "original_image_base64": None,
            "localization_scope": "sample response",
            "source": "3D U-Net Tumor Segmentation",
        },
        "report": {
            "summary": "The uploaded CT scan shows a high-risk malignant prediction with suspected tumor region highlighted.",
            "recommendation": "Radiologist review is recommended.",
            "disclaimer": DISCLAIMER,
        },
        "warnings": ["Sample response only; no patient data was processed."],
    }

