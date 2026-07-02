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

export type LungifyHealth = {
  status: string;
  device: string;
  model_status: string;
  loaded_models: Record<string, unknown>;
  warnings: string[];
  backend_mode: "demo" | "proxy";
};

export type LungifyModelInfo = {
  name: string;
  status: string;
  architecture: Record<string, unknown>;
  metrics: Record<string, unknown>;
  classes: Record<string, string[]>;
  limitations: string[];
  warnings: string[];
  backend_mode: "demo" | "proxy";
};
