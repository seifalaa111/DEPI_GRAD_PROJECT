import { randomUUID } from "crypto";

import type { LungifyHealth, LungifyModelInfo, LungifyPrediction } from "@/src/lib/lungify";

const DISCLAIMER =
  "Lungify is a research prototype and clinical decision-support concept. It is not a replacement for radiologists, medical diagnosis, or professional clinical judgment.";

function requestId(): string {
  return `LNG-${randomUUID().replace(/-/g, "").slice(0, 10).toUpperCase()}`;
}

function normalizeBaseUrl(value: string | undefined): string | null {
  if (!value) {
    return null;
  }
  return value.trim().replace(/\/+$/, "") || null;
}

export function resolveBackendUrl(): string | null {
  return normalizeBaseUrl(process.env.LUNGIFY_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL);
}

export function isZipUpload(filename: string | null | undefined): boolean {
  return Boolean(filename?.toLowerCase().endsWith(".zip"));
}

type BackendRequestResult =
  | { kind: "missing" }
  | { kind: "ok"; response: Response }
  | { kind: "unreachable"; backendUrl: string };

export async function requestBackend(path: string, init?: RequestInit): Promise<BackendRequestResult> {
  const backendUrl = resolveBackendUrl();
  if (!backendUrl) {
    return { kind: "missing" };
  }

  try {
    const response = await fetch(`${backendUrl}${path}`, {
      ...init,
      cache: "no-store",
    });
    return { kind: "ok", response };
  } catch {
    return { kind: "unreachable", backendUrl };
  }
}

export function createDemoHealth(extraWarnings: string[] = []): LungifyHealth {
  return {
    status: "demo",
    device: "demo-mode",
    model_status: "sample",
    loaded_models: {
      pipeline_a: { loaded: false, artifact: "Not configured in this deployment." },
      pipeline_b: { loaded: false, artifacts: 0 },
      errors: {},
    },
    warnings: [
      "Built-in preview and sample mode is active.",
      "Set LUNGIFY_BACKEND_URL in Vercel to enable real DICOM ZIP inference through the FastAPI backend.",
      ...extraWarnings,
    ],
    backend_mode: "demo",
  };
}

export function createProxyDegradedHealth(extraWarnings: string[] = []): LungifyHealth {
  return {
    status: "degraded",
    device: "backend-unreachable",
    model_status: "unknown",
    loaded_models: {},
    warnings: [
      "A backend URL is configured, but the deployed inference service is currently unavailable.",
      ...extraWarnings,
    ],
    backend_mode: "proxy",
  };
}

export function createSamplePrediction(extraWarnings: string[] = []): LungifyPrediction {
  return {
    request_id: requestId(),
    model_status: "sample",
    input_mode: "sample",
    final_assessment: {
      label: "Malignant",
      risk_level: "High",
      confidence: 0.87,
      source: "Binary Cancer Screening Engine",
    },
    subtype_suggestion: {
      label: "Primary Lung Cancer",
      confidence: 0.72,
      probabilities: {
        "Benign/Unknown": 0.08,
        "Primary Lung Ca": 0.72,
        Metastatic: 0.2,
      },
      source: "Multiclass Extension Engine",
    },
    segmentation: {
      available: true,
      original_image_base64: "/assets/seg_vis_LIDC-IDRI-0939.png",
      mask_image_base64: null,
      overlay_image_base64: "/assets/seg_vis_LIDC-IDRI-0939.png",
      localization_scope: "sample response",
      source: "3D U-Net Tumor Segmentation",
    },
    report: {
      summary: "The uploaded CT scan shows a high-risk malignant prediction with suspected tumor region highlighted.",
      recommendation: "Radiologist review is recommended.",
      disclaimer: DISCLAIMER,
    },
    warnings: ["Sample response only; no patient data was processed.", ...extraWarnings],
    processing_time_ms: 0,
  };
}

export function createDemoModelInfo(extraWarnings: string[] = []): LungifyModelInfo {
  return {
    name: "Lungify CT cancer screening and tumor localization prototype",
    status: "sample",
    architecture: {
      binary_screening: "3D ResNet-SE image encoder + tabular MLP fusion head",
      subtype_and_segmentation: "5-fold multiclass ensemble with 3D U-Net localization",
    },
    metrics: {
      binary_metrics_note: "Charts on this page are bundled with the frontend for engineering review.",
      multiclass_cv: {
        cv_means: {
          acc: 0.548,
          f1_mac: 0.537,
          f1_wt: 0.538,
          auc: 0.666,
        },
      },
    },
    classes: {
      binary: ["Benign/Unknown", "Malignant"],
      multiclass: ["Benign/Unknown", "Primary Lung Ca", "Metastatic"],
    },
    limitations: [
      "Research prototype only; not for clinical diagnosis.",
      "Real inference requires a de-identified DICOM CT series ZIP.",
      "Segmentation is center-patch prototype localization for uploaded studies without XML nodule annotations.",
      "Subtype probabilities are support information and do not override the binary screening assessment.",
    ],
    warnings: [
      "Built-in model summary is active because no backend is configured for this deployment.",
      ...extraWarnings,
    ],
    backend_mode: "demo",
  };
}

export function createProxyDegradedModelInfo(extraWarnings: string[] = []): LungifyModelInfo {
  return {
    ...createDemoModelInfo(),
    status: "degraded",
    warnings: [
      "A backend URL is configured, but the deployed inference service is currently unavailable.",
      ...extraWarnings,
    ],
    backend_mode: "proxy",
  };
}

export function createPreviewPrediction(reason: string): LungifyPrediction {
  return {
    request_id: requestId(),
    model_status: "preview",
    input_mode: "preview",
    final_assessment: {
      label: "Preview only",
      risk_level: "Unavailable",
      confidence: 0,
      source: "Binary Cancer Screening Engine",
    },
    subtype_suggestion: {
      label: "Not available in preview mode",
      confidence: null,
      probabilities: {},
      source: "Multiclass Extension Engine",
    },
    segmentation: {
      available: false,
      original_image_base64: null,
      mask_image_base64: null,
      overlay_image_base64: null,
      localization_scope: null,
      source: "3D U-Net Tumor Segmentation",
    },
    report: {
      summary: "This upload was accepted for interface preview only; no 3D CT model inference was run.",
      recommendation: "Connect the FastAPI backend to enable real ZIP inference, or use Sample mode to preview the report flow.",
      disclaimer: DISCLAIMER,
    },
    warnings: [reason],
    processing_time_ms: 0,
  };
}
