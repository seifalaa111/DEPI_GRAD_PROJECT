"use client";

import { useMemo, useState } from "react";
import { AlertCircle, FileArchive, FileText, Image as ImageIcon, Loader2, Play, RefreshCcw, ScanLine, UploadCloud } from "lucide-react";
import { analyzeScan, getSampleReport, imageSrc, type LungifyPrediction } from "@/src/lib/api";

const tabs = ["Original", "Mask", "Overlay", "Report"] as const;
type Tab = (typeof tabs)[number];

export function DemoClient() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<LungifyPrediction | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("Report");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const statusLabel = useMemo(() => {
    if (!result) return "Awaiting scan";
    if (result.model_status === "real") return "Real model";
    if (result.model_status === "sample") return "Sample mode";
    return "Preview mode";
  }, [result]);

  async function runAnalysis() {
    if (!file) {
      setError("Choose a DICOM series ZIP or preview file first.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const next = await analyzeScan(file);
      setResult(next);
      setActiveTab(next.segmentation.available ? "Overlay" : "Report");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  async function loadSample() {
    setLoading(true);
    setError(null);
    try {
      const next = await getSampleReport();
      setResult(next);
      setActiveTab("Report");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load sample report.");
    } finally {
      setLoading(false);
    }
  }

  const original = imageSrc(result?.segmentation.original_image_base64);
  const mask = imageSrc(result?.segmentation.mask_image_base64);
  const overlay = imageSrc(result?.segmentation.overlay_image_base64);

  return (
    <section className="demo-shell">
      <div className="upload-panel">
        <div>
          <p className="eyebrow">Lungify Demo</p>
          <h1>AI Report Workspace</h1>
        </div>
        <label className="drop-zone">
          <UploadCloud size={28} />
          <span>{file ? file.name : "Recommended upload: DICOM series as .zip"}</span>
          <small>Single .dcm, .png, or .jpg is preview mode only.</small>
          <input
            type="file"
            accept=".zip,.dcm,.png,.jpg,.jpeg"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setError(null);
            }}
          />
        </label>
        <div className="button-row">
          <button className="primary-button" onClick={runAnalysis} disabled={loading}>
            {loading ? <Loader2 className="spin" size={18} /> : <Play size={18} />}
            <span>Analyze</span>
          </button>
          <button className="ghost-button" onClick={loadSample} disabled={loading}>
            <RefreshCcw size={18} />
            <span>Sample</span>
          </button>
        </div>
        <div className="status-strip">
          <span>AI Backend: {loading ? "Processing" : "Online"}</span>
          <span>Model Mode: {statusLabel}</span>
        </div>
        {error && (
          <div className="error-box">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
      </div>

      <div className="result-workspace">
        <div className="tabs" role="tablist" aria-label="Result views">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={activeTab === tab ? "active" : ""}
              onClick={() => setActiveTab(tab)}
              type="button"
            >
              {tab === "Original" && <ImageIcon size={16} />}
              {tab === "Mask" && <FileArchive size={16} />}
              {tab === "Overlay" && <ScanLine size={16} />}
              {tab === "Report" && <FileText size={16} />}
              <span>{tab}</span>
            </button>
          ))}
        </div>
        <div className="viewer">
          {activeTab === "Original" && <ImagePane src={original} label="Original CT slice" />}
          {activeTab === "Mask" && <ImagePane src={mask} label="Predicted tumor mask" />}
          {activeTab === "Overlay" && <ImagePane src={overlay} label="CT overlay" />}
          {activeTab === "Report" && <ReportPane result={result} />}
        </div>
      </div>
    </section>
  );
}

function ImagePane({ src, label }: { src: string | null; label: string }) {
  if (!src) {
    return (
      <div className="empty-view">
        <ImageIcon size={36} />
        <span>No image available</span>
      </div>
    );
  }
  return <img className="scan-preview" src={src} alt={label} />;
}

function ReportPane({ result }: { result: LungifyPrediction | null }) {
  if (!result) {
    return (
      <div className="empty-view">
        <AlertCircle size={36} />
        <span>No report yet</span>
      </div>
    );
  }
  const confidence = Math.round(result.final_assessment.confidence * 100);
  return (
    <div className="report-pane">
      <div className="assessment-line">
        <span>{result.final_assessment.label}</span>
        <strong>{confidence}%</strong>
      </div>
      <div className="report-grid">
        <div>
          <small>Risk</small>
          <b>{result.final_assessment.risk_level}</b>
        </div>
        <div>
          <small>Subtype</small>
          <b>{result.subtype_suggestion.label}</b>
        </div>
        <div>
          <small>Localization</small>
          <b>{result.segmentation.available ? "Available" : "Unavailable"}</b>
        </div>
      </div>
      <p>{result.report.summary}</p>
      <p className="recommendation">{result.report.recommendation}</p>
      {result.warnings.length > 0 && (
        <ul className="warning-list">
          {result.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}
      <small className="disclaimer">{result.report.disclaimer}</small>
    </div>
  );
}
