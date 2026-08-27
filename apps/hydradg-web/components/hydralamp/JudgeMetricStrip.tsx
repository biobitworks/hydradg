"use client";

import { useState } from "react";

type JudgeMetric = {
  rank: number;
  NAME: string;
  display: string;
  status: string;
};

type JudgeSurface = {
  FROZEN_46_EVENT_SHA256?: string;
  FROZEN_EVENT_COUNT?: number;
  metrics?: JudgeMetric[];
  engineering_tier?: Record<string, unknown>;
  governance?: Record<string, string>;
  preferred_claim?: string;
};

const DEFAULT: JudgeSurface = {
  FROZEN_EVENT_COUNT: 46,
  FROZEN_46_EVENT_SHA256: "44e9d3dc7014b9b2c410a9e1e2c9b35a72cd269e4e561eba40414081ca81690d",
  metrics: [
    { rank: 1, NAME: "PRIVATE_LEAK_COUNT", display: "0", status: "PASS" },
    { rank: 2, NAME: "UNAUTHORIZED_WRITE_COUNT", display: "0", status: "PASS" },
    { rank: 3, NAME: "REPLAY_ACCEPTED_COUNT", display: "0 (5 rejected)", status: "PASS" },
    { rank: 4, NAME: "POISON_CANONICALIZED_COUNT", display: "0", status: "PASS" },
    { rank: 5, NAME: "RESTORATION_PASS", display: "PASS", status: "PASS" },
    { rank: 6, NAME: "QUARANTINE_RESOLVED", display: "PASS", status: "PASS" },
    { rank: 7, NAME: "fcg_root_after", display: "a1ec5db1…846b1", status: "INFORMATIONAL" },
    { rank: 8, NAME: "BROWSER_VERIFY_PASS", display: "PASS", status: "PASS" },
  ],
  engineering_tier: {
    FCG_ROOT_CHANGE_COUNT: 6,
    gateway_msm_entropy_proxy_0_100: 75.3349,
    canonical_cloud_drift_jsd: "NOT_COMPUTED",
    restoration_gain_tvd: "NOT_COMPUTED",
    PASS_AT_3_46_EVENT_LANE: "NOT_ESTABLISHED",
  },
  governance: {
    SIGNATURE_STATE: "NOT_SIGNED",
    MERKLE_MMR_STATE: "NOT_COMMITTED_BY_THIS_REVIEW",
  },
  preferred_claim:
    "HydraLamp does not ask a model whether the system is safe. Deterministic custody decides.",
};

export default function JudgeMetricStrip({ data }: { data?: JudgeSurface | null }) {
  const [open, setOpen] = useState(false);
  const surface = data ?? DEFAULT;
  const sha = surface.FROZEN_46_EVENT_SHA256 ?? DEFAULT.FROZEN_46_EVENT_SHA256!;
  const metrics = surface.metrics ?? DEFAULT.metrics!;

  return (
    <section className="hlJudgeStrip" aria-label="Frozen judge metrics">
      <header>
        <strong>REVIEW B · FROZEN JUDGE STRIP</strong>
        <span className="hlHint">
          {surface.FROZEN_EVENT_COUNT ?? 46} events · {sha.slice(0, 8)}…{sha.slice(-5)}
        </span>
      </header>
      <ul className="hlJudgeMetrics">
        {metrics.map((m) => (
          <li key={m.NAME} className={m.status === "PASS" ? "pass" : m.status === "INFORMATIONAL" ? "info" : ""}>
            <span className="name">{m.NAME.replace(/_/g, " ")}</span>
            <span className="val">{m.display}</span>
            <span className="st">{m.status}</span>
          </li>
        ))}
      </ul>
      <p className="hlJudgeClaim">{surface.preferred_claim ?? DEFAULT.preferred_claim}</p>
      <p className="hlHint">
        FCG root changes (6) = custody/topology only · Zero counts = gate outcomes, not statistical superiority
      </p>
      <button type="button" className="hlDiagToggle" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        {open ? "Hide" : "Show"} engineering diagnostics
      </button>
      {open && (
        <div className="hlDiagPanel mono small">
          <p>ΔG* — ENGINEERING TIER ONLY (not judge strip; not physical Gibbs energy)</p>
          <p>Gateway drift proxy — 75.3349 (MSM entropy proxy, not canonical JSD CloudDrift)</p>
          <p>Canonical CloudDrift JSD — NOT_COMPUTED on frozen lane</p>
          <p>restoration_gain (TVD) — NOT_COMPUTED on frozen 46-event lane</p>
          <p>PASS@3 / PASS^3 (46-event lane) — NOT_ESTABLISHED (BLOCKED_CASE_VECTORS)</p>
          <p>SIGNATURE — {surface.governance?.SIGNATURE_STATE ?? "NOT_SIGNED"}</p>
          <p>MERKLE/MMR — {surface.governance?.MERKLE_MMR_STATE ?? "NOT_COMMITTED"}</p>
          <a href="/demo/judge-metric-surface.json">Source JSON</a>
        </div>
      )}
    </section>
  );
}
