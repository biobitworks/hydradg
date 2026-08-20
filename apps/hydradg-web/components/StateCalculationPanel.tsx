import Link from "next/link";

import KnowledgeTermLink from "@/components/KnowledgeTermLink";

export type StateCalculation = {
  t: number;
  label: string;
  distribution: readonly number[];
  shannon_entropy: number;
  normalized_entropy: number;
  g_star: number;
  delta_g_star: number;
  mutation_distance: number;
  restoration_gain: number;
  burden: number;
  cloud_drift_0_100: number;
};

export type AnticubeConsideration = {
  status: string;
  receiptId?: string;
  classifierState?: string;
  claimCeiling?: string;
  note: string;
};

export const STATE_VISUALS: Record<number, { name: string; color: string; hue: number; meaning: string }> = {
  0: { name: "Reference / normal", color: "#b69cff", hue: 265, meaning: "Frozen comparison state" },
  1: { name: "Poison / mutation", color: "#ff8a3d", hue: 18, meaning: "Controlled perturbation" },
  2: { name: "Antidote / restoration", color: "#5aa9ff", hue: 215, meaning: "Recovery with history retained" },
};

function metricBox(color: string) {
  return {
    border: `1px solid ${color}88`,
    background: `${color}16`,
    borderRadius: 9,
    padding: "9px 10px",
  } as const;
}

function signed(value: number, digits = 6) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(digits)}`;
}

export function AnticubePanel({ anticube }: { anticube: AnticubeConsideration }) {
  const anticubeHasReceipt = Boolean(anticube.receiptId);
  return (
    <div style={{ marginTop: 10, border: anticubeHasReceipt ? "1px solid rgba(246,200,95,0.65)" : "1px solid rgba(216,224,232,0.28)", background: anticubeHasReceipt ? "rgba(246,200,95,0.08)" : "rgba(216,224,232,0.04)", borderRadius: 9, padding: "10px 12px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
        <strong><KnowledgeTermLink slug="anticube">Anticube consideration</KnowledgeTermLink></strong>
        <span className={anticubeHasReceipt ? "pill pillWarn" : "pill pillMuted"}>{anticube.status}</span>
      </div>
      <p className="small muted">{anticube.note}</p>
      {anticube.receiptId ? <p className="mono small compact">receipt={anticube.receiptId}</p> : null}
      {anticube.classifierState ? <p className="mono small compact">classifier_state={anticube.classifierState}</p> : null}
      {anticube.claimCeiling ? <p className="mono small compact">claim_ceiling={anticube.claimCeiling}</p> : null}
      {anticube.receiptId ? <Link className="secondary" href={`/fco/${encodeURIComponent(anticube.receiptId)}`}>Open ClassificationReceipt</Link> : <Link className="secondary" href="/knowledge#anticube">Why UNKNOWN is retained</Link>}
    </div>
  );
}

export default function StateCalculationPanel({
  state,
  scope,
  anticube,
}: {
  state: StateCalculation;
  scope: "OBJECT_STATE_SNAPSHOT" | "STATE_INHERITED";
  anticube: AnticubeConsideration;
}) {
  const visual = STATE_VISUALS[state.t] || { name: state.label, color: "#d8e0e8", hue: 0, meaning: "Declared state" };

  return (
    <section aria-label="Selected node state calculations" style={{ marginTop: 14 }}>
      <div style={{ borderLeft: `4px solid ${visual.color}`, background: `${visual.color}10`, borderRadius: 10, padding: "10px 12px", marginBottom: 12 }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <strong style={{ color: visual.color }}>t{state.t} · {visual.name}</strong>
          <span className="pill pillMuted">{scope}</span>
        </div>
        <p className="small muted" style={{ marginBottom: 0 }}>{visual.meaning}. These values describe the selected node's declared/inherited synthetic fixture state; they are not an accuracy verdict.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,minmax(0,1fr))", gap: 8 }}>
        <div style={metricBox(visual.color)}><span className="metricLabel">Distribution</span><strong className="mono small">[{state.distribution.map((v) => v.toFixed(2)).join(", ")}]</strong></div>
        <div style={metricBox(visual.color)}><span className="metricLabel"><KnowledgeTermLink slug="shannon-h">Shannon H</KnowledgeTermLink></span><strong>{state.shannon_entropy.toFixed(6)}</strong></div>
        <div style={metricBox(visual.color)}><span className="metricLabel">Hnorm</span><strong>{state.normalized_entropy.toFixed(6)}</strong></div>
        <div style={metricBox(visual.color)}><span className="metricLabel"><KnowledgeTermLink slug="u-star-burden">U* burden</KnowledgeTermLink></span><strong>{state.burden.toFixed(4)}</strong></div>
        <div style={metricBox(visual.color)}><span className="metricLabel"><KnowledgeTermLink slug="g-star">G*</KnowledgeTermLink></span><strong>{state.g_star.toFixed(6)}</strong></div>
        <div style={metricBox(visual.color)}><span className="metricLabel"><KnowledgeTermLink slug="delta-g-star">ΔG*</KnowledgeTermLink></span><strong>{signed(state.delta_g_star)}</strong></div>
        <div style={metricBox(visual.color)}><span className="metricLabel"><KnowledgeTermLink slug="cloud-drift">Cloud Drift</KnowledgeTermLink></span><strong>{state.cloud_drift_0_100.toFixed(4)}</strong></div>
        <div style={metricBox(visual.color)}><span className="metricLabel"><KnowledgeTermLink slug="mutation-distance">TV mutation</KnowledgeTermLink></span><strong>{state.mutation_distance.toFixed(6)}</strong></div>
        <div style={metricBox(visual.color)}><span className="metricLabel"><KnowledgeTermLink slug="restoration-gain">Restoration gain</KnowledgeTermLink></span><strong>{state.restoration_gain.toFixed(6)}</strong></div>
      </div>

      <AnticubePanel anticube={anticube} />
    </section>
  );
}
