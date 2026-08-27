"use client";

import { useEffect, useState } from "react";

type ProbeRow = { id: string; outcome: string };

type CortexSuccessorSummary = {
  lane?: string;
  ui_demo_eligible?: boolean;
  probes?: ProbeRow[];
  CORTEX_AUTH_CURRENT?: string;
  CORTEX_REMEMBER?: string;
  CORTEX_RECALL?: string;
  boundary?: string;
};

const STEP_IDS = [
  "A_MEMORY_WRITE",
  "B_MEMORY_READ",
  "D_POISON_CONFLICT",
  "E_CURRENT_STATE_QUERY",
  "F_HYDRADG_CUSTODY_CHECK",
  "G_ANTIDOTE_CORRECTION",
  "H_RESTORATION_QUERY",
] as const;

const STEP_LABELS: Record<string, string> = {
  A_MEMORY_WRITE: "REFERENCE → Cortex remember",
  B_MEMORY_READ: "Cortex direct recall",
  D_POISON_CONFLICT: "POISON candidate",
  E_CURRENT_STATE_QUERY: "Contradiction probe",
  F_HYDRADG_CUSTODY_CHECK: "HydraDG receipt verify",
  G_ANTIDOTE_CORRECTION: "ANTIDOTE correction",
  H_RESTORATION_QUERY: "Restoration read",
};

export default function CortexSuccessorStrip() {
  const [data, setData] = useState<CortexSuccessorSummary | null>(null);

  useEffect(() => {
    fetch("/demo/cortex-successor-summary.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => setData(j))
      .catch(() => setData(null));
  }, []);

  if (!data?.ui_demo_eligible) return null;

  const probes = data.probes ?? [];

  return (
    <section className="hlCortexSuccessor" aria-label="Sponsor integration Cortex live lane">
      <header>
        <strong>SPONSOR INTEGRATION · MITOSIS CORTEX (LIVE)</strong>
        <span className="hlHint">Outside frozen 46-event judge strip</span>
      </header>
      <p className="hlCortexBoundary">
        <span className="hlCortexTag">CORTEX MEMORY</span> external recall ·{" "}
        <span className="hlHydraTag">HYDRADG CUSTODY</span> canonical provenance
      </p>
      <div className="hlCortexGates">
        <span>auth {data.CORTEX_AUTH_CURRENT}</span>
        <span>remember {data.CORTEX_REMEMBER}</span>
        <span>recall {data.CORTEX_RECALL}</span>
      </div>
      <ol className="hlCortexSteps">
        {STEP_IDS.map((id) => {
          const probe = probes.find((p) => p.id === id);
          const outcome = probe?.outcome ?? "—";
          return (
            <li key={id}>
              <span>{STEP_LABELS[id]}</span>
              <span className={`hlCortexOutcome hlCortexOutcome--${outcome}`}>{outcome}</span>
            </li>
          );
        })}
      </ol>
      <p className="hlHint">{data.boundary}</p>
    </section>
  );
}
