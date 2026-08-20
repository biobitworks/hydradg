"use client";

import { useEffect, useMemo, useState } from "react";

import type { PresentationState } from "@/lib/presentationLineage";

type TimelineState = {
  t: number;
  label: string;
  delta_g_star: number;
  cloud_drift_0_100: number;
  delta_hit_at_k?: number | null;
  delta_recall_at_k?: number | null;
};

type IcebergPayload = {
  source_state?: string;
  timeline?: TimelineState[];
  claim_ceiling?: string;
  error?: string;
};

function signed(value: number | null | undefined, digits = 3) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "PENDING";
  if (Math.abs(value) < 10 ** -(digits + 1)) return (0).toFixed(digits);
  return `${value > 0 ? "+" : ""}${value.toFixed(digits)}`;
}

function pct(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "PENDING";
  return `${value > 0 ? "+" : ""}${(value * 100).toFixed(1)}%`;
}

export default function PresentationEvolution({ history }: { history: readonly PresentationState[] }) {
  const [iceberg, setIceberg] = useState<IcebergPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    fetch("/api/iceberg", { cache: "no-store" })
      .then(async (response) => {
        const payload = (await response.json()) as IcebergPayload;
        if (!response.ok || payload.error) throw new Error(payload.error || `iceberg state failed (${response.status})`);
        if (active) setIceberg(payload);
      })
      .catch((caught) => {
        if (active) setError(caught instanceof Error ? caught.message : String(caught));
      });
    return () => {
      active = false;
    };
  }, []);

  const timeline = useMemo(() => [...(iceberg?.timeline || [])].sort((a, b) => a.t - b.t), [iceberg]);

  return (
    <div className="stack" style={{ gap: 24 }}>
      <section className="panel evolutionPanel">
        <div className="panelHead">
          <div>
            <p className="eyebrow">Current context-state measurements</p>
            <h2>Numbers move with state, not with design fashion.</h2>
          </div>
          <span className={error ? "pill pillWarn" : "pill pillMuted"}>{iceberg?.source_state?.replaceAll("_", " ") || (error ? "READ BLOCKED" : "LOADING")}</span>
        </div>
        <p className="muted">
          ΔG* is the project&apos;s dimensionless information-state diagnostic; Cloud Drift is 100×Jensen-Shannon divergence from the frozen reference distribution. Hit/recall remain separate empirical outcomes. A presentation update may coincide with these changes, but supersession alone is not evidence of causation.
        </p>
        {timeline.length ? (
          <div className="evolutionMetrics" role="table" aria-label="Context metric history">
            {timeline.map((state) => (
              <div className="evolutionMetricRow" role="row" key={`${state.t}-${state.label}`}>
                <div><span className="metricLabel">State</span><strong>t{state.t} · {state.label}</strong></div>
                <div><span className="metricLabel">ΔG*</span><strong>{signed(state.delta_g_star)}</strong></div>
                <div><span className="metricLabel">Cloud Drift</span><strong>{state.cloud_drift_0_100.toFixed(1)}</strong></div>
                <div><span className="metricLabel">Hit Δ</span><strong>{pct(state.delta_hit_at_k)}</strong></div>
                <div><span className="metricLabel">Recall Δ</span><strong>{pct(state.delta_recall_at_k)}</strong></div>
              </div>
            ))}
          </div>
        ) : (
          <p className="small muted">{error ? `Metric readback unavailable: ${error}` : "Loading context-state measurements…"}</p>
        )}
      </section>

      <section className="panel evolutionPanel">
        <p className="eyebrow">Presentation lineage</p>
        <h2>New views supersede; old views remain evidence.</h2>
        <p className="muted">
          Historical versions lose default presentation priority as the product evolves, but their Git commits remain addressable. Older states are not rewritten to make the current interface look inevitable.
        </p>
        <div className="presentationTimeline">
          {history.map((version, index) => (
            <article className={`presentationState ${version.state === "CURRENT" ? "current" : "historical"}`} key={version.id}>
              <div className="presentationStateIndex">{String(index + 1).padStart(2, "0")}</div>
              <div>
                <div className="presentationStateTitle">
                  <strong>{version.label}</strong>
                  <span className={version.state === "CURRENT" ? "pill pillGood" : "pill pillMuted"}>{version.presentation_priority}</span>
                </div>
                <p className="small muted mono compact">{version.commit}</p>
                <p>{version.reason}</p>
                <p className="small muted">Context metrics: {version.measured_context_metrics.replaceAll("_", " ").toLowerCase()}.</p>
                <div className="actions">
                  <a className="secondary" href={version.github_url} target="_blank" rel="noreferrer">Open GitHub state</a>
                  {version.deployment_url ? <a className="secondary" href={version.deployment_url} target="_blank" rel="noreferrer">Open historical deployment</a> : null}
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
