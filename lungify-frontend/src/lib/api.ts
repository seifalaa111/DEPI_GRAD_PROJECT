import type { LungifyHealth, LungifyModelInfo, LungifyPrediction } from "@/src/lib/lungify";

const API_URL = "/api";

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
  return parseJsonResponse<LungifyPrediction>(response, "Lungify prediction request failed.");
}

export async function getSampleReport(): Promise<LungifyPrediction> {
  const response = await fetch(`${API_URL}/predict/sample`, { method: "POST" });
  return parseJsonResponse<LungifyPrediction>(response, "Could not load the Lungify sample report.");
}

export async function getBackendHealth(): Promise<LungifyHealth> {
  const response = await fetch(`${API_URL}/health`, {
    cache: "no-store",
  });
  return parseJsonResponse<LungifyHealth>(response, "Could not load backend health.");
}

export async function getModelInfo(): Promise<LungifyModelInfo> {
  const response = await fetch(`${API_URL}/model-info`, {
    cache: "no-store",
  });
  return parseJsonResponse<LungifyModelInfo>(response, "Could not load model information.");
}

export function imageSrc(value: string | null | undefined): string | null {
  if (!value) {
    return null;
  }
  if (
    value.startsWith("data:") ||
    value.startsWith("http://") ||
    value.startsWith("https://") ||
    value.startsWith("/")
  ) {
    return value;
  }
  return `data:image/png;base64,${value}`;
}

async function parseJsonResponse<T>(response: Response, fallbackMessage: string): Promise<T> {
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.detail?.message || data?.message || fallbackMessage;
    throw new Error(message);
  }
  return data as T;
}
