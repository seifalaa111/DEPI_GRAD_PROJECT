export type LungifyPrediction = {
  request_id: string;
  model_status: string;
  input_mode: string;
  final_assessment: {
    label: string;
    risk_level: string;
    confidence: number;
    source: string;
  };
  subtype_suggestion: {
    label: string;
    confidence: number | null;
    probabilities: Record<string, number>;
    source: string;
  };
  segmentation: {
    available: boolean;
    mask_image_base64: string | null;
    overlay_image_base64: string | null;
    original_image_base64: string | null;
    localization_scope: string | null;
    source: string;
  };
  report: {
    summary: string;
    recommendation: string;
    disclaimer: string;
  };
  warnings: string[];
  processing_time_ms: number | null;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeScan(file: File, metadata?: Record<string, unknown>): Promise<LungifyPrediction> {
  const form = new FormData();
  form.append("scan", file);
  if (metadata && Object.keys(metadata).length > 0) {
    form.append("metadata", JSON.stringify(metadata));
  }

  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    body: form
  });
  return parsePredictionResponse(response);
}

export async function getSampleReport(): Promise<LungifyPrediction> {
  const response = await fetch(`${API_URL}/predict/sample`, { method: "POST" });
  return parsePredictionResponse(response);
}

export function imageSrc(base64: string | null | undefined): string | null {
  return base64 ? `data:image/png;base64,${base64}` : null;
}

async function parsePredictionResponse(response: Response): Promise<LungifyPrediction> {
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.detail?.message || data?.message || "Lungify backend request failed.";
    throw new Error(message);
  }
  return data as LungifyPrediction;
}

