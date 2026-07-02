"use client";

import { useEffect, useState } from "react";
import { Activity, BrainCircuit, Layers3, ShieldAlert, ShieldCheck, Siren } from "lucide-react";

import { getBackendHealth, getModelInfo } from "@/src/lib/api";
import type { LungifyHealth, LungifyModelInfo } from "@/src/lib/lungify";

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function formatMetric(value: unknown): string {
  return typeof value === "number" ? value.toFixed(3) : "N/A";
}

export function ModelInsights() {
  const [health, setHealth] = useState<LungifyHealth | null>(null);
  const [modelInfo, setModelInfo] = useState<LungifyModelInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const [nextHealth, nextModelInfo] = await Promise.all([getBackendHealth(), getModelInfo()]);
        if (!active) return;
        setHealth(nextHealth);
        setModelInfo(nextModelInfo);
        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Could not load runtime model details.");
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, []);

  const metrics = asRecord(modelInfo?.metrics);
  const multiclassCv = asRecord(metrics?.multiclass_cv);
  const cvMeans = asRecord(multiclassCv?.cv_means);
  const warnings = [...(health?.warnings ?? []), ...(modelInfo?.warnings ?? [])];
  const uniqueWarnings = Array.from(new Set(warnings));

  return (
    <section className="runtime-panel">
      <div className="runtime-header">
        <div>
          <p className="eyebrow">Runtime Status</p>
          <h2>Live model and backend snapshot</h2>
        </div>
        <div className={`runtime-pill ${health?.backend_mode === "proxy" ? "live" : "demo"}`}>
          {health?.backend_mode === "proxy" ? <ShieldCheck size={16} /> : <ShieldAlert size={16} />}
          <span>{health?.backend_mode === "proxy" ? "Real backend linked" : "Built-in fallback mode"}</span>
        </div>
      </div>

      <div className="runtime-grid">
        <article>
          <div className="icon-badge">
            <Activity size={18} />
          </div>
          <small>Backend Health</small>
          <strong>{health?.status ?? "Loading"}</strong>
          <p>Device: {health?.device ?? "Checking"}.</p>
        </article>
        <article>
          <div className="icon-badge">
            <BrainCircuit size={18} />
          </div>
          <small>Model Status</small>
          <strong>{health?.model_status ?? modelInfo?.status ?? "Loading"}</strong>
          <p>Binary and multiclass pipelines are loaded together for ZIP inference.</p>
        </article>
        <article>
          <div className="icon-badge">
            <Layers3 size={18} />
          </div>
          <small>Binary Classes</small>
          <strong>{modelInfo?.classes.binary?.join(" / ") ?? "Loading"}</strong>
          <p>The first-stage screen decides whether subtype and segmentation should run.</p>
        </article>
        <article>
          <div className="icon-badge">
            <Siren size={18} />
          </div>
          <small>Multiclass AUC</small>
          <strong>{formatMetric(cvMeans?.auc)}</strong>
          <p>Cross-validation mean taken from the bundled model summary.</p>
        </article>
      </div>

      <div className="runtime-detail-grid">
        <article className="runtime-detail">
          <h3>Classes</h3>
          <p><strong>Binary:</strong> {modelInfo?.classes.binary?.join(", ") ?? "Loading..."}</p>
          <p><strong>Multiclass:</strong> {modelInfo?.classes.multiclass?.join(", ") ?? "Loading..."}</p>
        </article>
        <article className="runtime-detail">
          <h3>Current Limitations</h3>
          <ul className="warning-list">
            {(modelInfo?.limitations ?? ["Loading model limitations..."]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </div>

      {(uniqueWarnings.length > 0 || error) && (
        <div className="runtime-warning">
          <strong>Deployment notes</strong>
          <ul className="warning-list">
            {uniqueWarnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
            {error && <li>{error}</li>}
          </ul>
        </div>
      )}
    </section>
  );
}
