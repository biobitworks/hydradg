"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";
import SiteNav from "@/components/SiteNav";
import "./hydralamp.css";

const CustodyGraph = dynamic(() => import("@/components/hydralamp/CustodyGraph"), {
  ssr: false,
  loading: () => <div className="hlCyto hlCytoPlaceholder">Loading graph…</div>,
});

type ModelSlot = {
  tag: string;
  params_b: number;
  digest_abbrev: string;
  status: string;
  diameter_px: number;
};

type Transition = {
  seq: number;
  phase: string;
  action: string;
  actor: string;
  tool_provider: string | null;
  model: ModelSlot | null;
  input_fco: string | null;
  output_fco: string | null;
  fcg_root_before: string;
  fcg_root_after: string;
  evidence_class: string;
  claim_ceiling: string;
  status: string;
  summary: string;
};

type GoldenRun = {
  run_id: string;
  session_id: string;
  phase: string;
  paused: boolean;
  follow_current: boolean;
  focus_target: string;
  task_prompt: string;
  transitions: Transition[];
  fcg_root_initial: string;
  fcg_root_current: string;
  fco_lineage: { A?: string; B?: string; C?: string; auth?: string };
  earliest_divergence: string | null;
  model_ladder: ModelSlot[];
  active_model_index: number;
  escalation_reason: string | null;
  providers: Record<string, string>;
  result_panel: Record<string, unknown> | null;
  claim_ceiling: string;
  signature_state: string;
  merkle_mmr_state: string;
  hydradb_state: string;
  done: boolean;
  judge_label?: string;
  phase_rail?: string[];
};

const PREFILL =
  "Load a governed customer-support memory. Poison one trusted fact so the account state becomes wrong. Give the agent the task 'resolve the customer’s request using the current evidence.' Start with the smallest admitted model and increase model size only if the evidence is insufficient. Trace every tool call and handoff. Detect the earliest poisoned dependency, reject unsupported state, apply the verified antidote, restore the last supported state, and show the exact FCO/FCG path from reference → poison → agent decision → contradiction → antidote → restoration. Preserve every failed, null, abstaining, and superseded result.";

const RAIL = ["UNLOCK", "REFERENCE", "POISON", "AGENT", "VERIFY", "ANTIDOTE", "RESTORATION", "RECEIPT"];

async function postGolden(body: Record<string, unknown>) {
  const res = await fetch("/api/hydralamp/golden", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  return { ok: res.ok, status: res.status, data };
}

function short(h?: string | null) {
  if (!h) return "—";
  return `${h.slice(0, 8)}…${h.slice(-4)}`;
}

export default function HydraLampLivePage() {
  const [judgeKey, setJudgeKey] = useState("");
  const [task, setTask] = useState(PREFILL);
  const [run, setRun] = useState<GoldenRun | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [drawer, setDrawer] = useState(false);
  const [evidenceTab, setEvidenceTab] = useState<"historical" | "demo" | "dev" | "future">("demo");

  const applyRun = useCallback((r: GoldenRun) => setRun(r), []);

  const unlock = async () => {
    setBusy(true);
    setErr(null);
    const { ok, data } = await postGolden({ action: "unlock", judge_key: judgeKey, task_prompt: task });
    setBusy(false);
    if (!ok) {
      setErr(data.error || data.code || "Unlock failed");
      return;
    }
    applyRun(data.run);
  };

  const act = async (action: string, extra: Record<string, unknown> = {}) => {
    if (!run && action !== "reset") return;
    setBusy(true);
    setErr(null);
    const { ok, data } = await postGolden({
      action,
      run_id: run?.run_id,
      judge_key: judgeKey,
      task_prompt: task,
      ...extra,
    });
    setBusy(false);
    if (!ok) {
      setErr(data.error || "Action failed");
      return;
    }
    if (data.run) applyRun(data.run);
  };

  const graphNodes = useMemo(() => {
    if (!run) return [];
    const nodes: Array<{ id: string; label: string; visual_class: string; size?: number }> = [];
    const L = run.fco_lineage;
    if (L.auth) nodes.push({ id: L.auth, label: "JudgeAuth", visual_class: "reference" });
    if (L.A) nodes.push({ id: L.A, label: "A accepted", visual_class: "canonical" });
    if (L.B) nodes.push({ id: L.B, label: "B poison", visual_class: "quarantined" });
    if (L.C) nodes.push({ id: L.C, label: "C restored", visual_class: "repaired" });
    const m = run.model_ladder[run.active_model_index];
    if (m && (run.phase === "AGENT" || run.transitions.some((t) => t.phase === "AGENT"))) {
      nodes.push({
        id: `model:${m.tag}`,
        label: `${m.tag} ${m.params_b}B`,
        visual_class: "probabilistic_proposal",
        size: m.diameter_px,
      });
    }
    return nodes;
  }, [run]);

  const graphEdges = useMemo(() => {
    if (!run) return [];
    const L = run.fco_lineage;
    const edges: Array<{ id: string; source: string; target: string; label: string }> = [];
    if (L.A && L.auth) edges.push({ id: "e1", source: L.A, target: L.auth, label: "AUTHORIZED_DEMO" });
    if (L.B && L.A) edges.push({ id: "e2", source: L.B, target: L.A, label: "CONTRADICTS" });
    if (L.C && L.A) edges.push({ id: "e3", source: L.C, target: L.A, label: "SUPERSEDES" });
    if (L.C && L.B) edges.push({ id: "e4", source: L.B, target: L.C, label: "QUARANTINED_NOT_ERASED" });
    return edges;
  }, [run]);

  const focusId = useMemo(() => {
    if (!run) return null;
    switch (run.focus_target) {
      case "poison":
        return run.fco_lineage.B || null;
      case "divergence":
        return run.earliest_divergence;
      case "restoration":
        return run.fco_lineage.C || null;
      default:
        return run.fco_lineage.C || run.fco_lineage.B || run.fco_lineage.A || run.fco_lineage.auth || null;
    }
  }, [run]);

  const last = run?.transitions[run.transitions.length - 1];

  return (
    <main className="hlPage">
      <SiteNav />
      <div className="hlInner hlMicroscope">
        <header className="hlHero">
          <p className="hlEyebrow">HydraLamp · Judge-operated golden path</p>
          <h1>Models propose. Custody decides.</h1>
          <p className="hlLead">
            Unlock a demo session, poison a governed memory, let an agent act, verify earliest divergence, restore —
            with a visible FCG root change at every step. Demo session ≠ canonical science.
          </p>
          {run && (
            <p className="hlBanner">{run.judge_label || "JUDGE SESSION — AUTHORIZED"} · not cryptographically signed</p>
          )}
        </header>

        {!run && (
          <section className="hlUnlock">
            <label>
              ENTER JUDGE KEY
              <input
                value={judgeKey}
                onChange={(e) => setJudgeKey(e.target.value)}
                placeholder="JUDGE-HYDRA-2026"
                autoComplete="off"
              />
            </label>
            <p className="hlMuted">Demo capability only — not a project private key, author signing key, or Merkle key.</p>
            <button className="hlPrimary" disabled={busy || !judgeKey.trim()} onClick={() => void unlock()}>
              {busy ? "…" : "AUTHORIZE SESSION"}
            </button>
          </section>
        )}

        <section className="hlTask">
          <label>
            Task
            <textarea value={task} onChange={(e) => setTask(e.target.value)} rows={5} />
          </label>
        </section>

        <section className="hlRail" aria-label="Phase rail">
          {RAIL.map((p) => (
            <span
              key={p}
              className={`hlRailStep ${run?.phase === p ? "active" : ""} ${
                run && RAIL.indexOf(run.phase) >= RAIL.indexOf(p) ? "reached" : ""
              }`}
            >
              {p}
            </span>
          ))}
        </section>

        <section className="hlControls">
          <button className="hlPrimary" disabled={busy || !run || run.done} onClick={() => void act("run")}>
            RUN
          </button>
          <button className="hlSecondary" disabled={busy || !run} onClick={() => void act("pause")}>
            PAUSE
          </button>
          <button className="hlSecondary" disabled={busy || !run || run.done} onClick={() => void act("step")}>
            STEP
          </button>
          <button
            className="hlSecondary"
            disabled={busy || !judgeKey.trim()}
            onClick={() => void act("reset")}
          >
            RESET
          </button>
          <button
            className="hlSecondary"
            disabled={!run}
            onClick={() => void act("focus", { focus: "current" })}
          >
            CENTER
          </button>
          <label className="hlFollow">
            <input
              type="checkbox"
              checked={run?.follow_current ?? true}
              disabled={!run}
              onChange={(e) => void act("follow", { follow: e.target.checked })}
            />
            FOLLOW CURRENT
          </label>
        </section>

        <section className="hlCenterBar">
          {(
            [
              ["current", "CENTER CURRENT"],
              ["poison", "CENTER POISON"],
              ["divergence", "CENTER DIVERGENCE"],
              ["restoration", "CENTER RESTORATION"],
              ["centroid", "FIT GRAPH"],
            ] as const
          ).map(([focus, label]) => (
            <button
              key={focus}
              className="hlSecondary"
              disabled={!run}
              onClick={() => void act("focus", { focus })}
            >
              {label}
            </button>
          ))}
        </section>

        {err && <p className="hlBanner">{err}</p>}

        <section className="hlMid">
          <div className="hlPanel hlViewfinder">
            <header>
              <strong>VIEWFINDER</strong>
              <span className="hlHint">reticle on current focus · FOLLOW={String(run?.follow_current)}</span>
            </header>
            <div className="hlReticleWrap">
              <CustodyGraph nodes={graphNodes} edges={graphEdges} pulseIds={focusId ? [focusId] : []} focusId={focusId} />
              <div className="hlReticle" aria-hidden />
            </div>
            <div className="hlModelLadder" aria-label="Model size ladder">
              {(run?.model_ladder || []).map((m, i) => (
                <div
                  key={m.tag}
                  className={`hlModelChip ${i === run?.active_model_index ? "active" : ""} status-${m.status}`}
                  style={{ width: m.diameter_px, height: m.diameter_px }}
                  title={`${m.tag} dig=${m.digest_abbrev} status=${m.status}`}
                >
                  <span>{m.params_b}B</span>
                </div>
              ))}
            </div>
            {run?.escalation_reason && <p className="hlBanner">{run.escalation_reason}</p>}
          </div>

          <div className="hlPanel">
            <header>
              <strong>EVENT LEDGER</strong>
              <span className="hlHint">session FCG deltas</span>
            </header>
            <ol className="hlChain">
              {(run?.transitions || []).map((t) => (
                <li key={t.seq}>
                  <span className="seq">#{t.seq}</span>
                  <span className="type">{t.phase}</span>
                  <span className="hash">{short(t.fcg_root_before)}→{short(t.fcg_root_after)}</span>
                  <span className="ver">{t.status}</span>
                  <div className="hlMuted">{t.summary}</div>
                </li>
              ))}
              {!run?.transitions?.length && <li className="hlMuted">Authorize a judge session to begin</li>}
            </ol>
          </div>
        </section>

        <section className="hlPanel hlInspector">
          <header>
            <strong>TRANSITION INSPECTOR</strong>
          </header>
          <dl className="hlInspectGrid">
            <div><dt>action</dt><dd>{last?.action || "—"}</dd></div>
            <div><dt>actor</dt><dd>{last?.actor || "—"}</dd></div>
            <div><dt>tool/provider</dt><dd>{last?.tool_provider || "—"}</dd></div>
            <div><dt>model</dt><dd>{last?.model ? `${last.model.tag} · ${last.model.params_b}B` : "—"}</dd></div>
            <div><dt>input FCO</dt><dd className="mono">{last?.input_fco || "—"}</dd></div>
            <div><dt>output FCO</dt><dd className="mono">{last?.output_fco || "—"}</dd></div>
            <div><dt>FCG before</dt><dd className="mono">{last?.fcg_root_before || "—"}</dd></div>
            <div><dt>FCG after</dt><dd className="mono">{last?.fcg_root_after || "—"}</dd></div>
            <div><dt>evidence class</dt><dd>{last?.evidence_class || "—"}</dd></div>
            <div><dt>claim ceiling</dt><dd>{last?.claim_ceiling || run?.claim_ceiling || "—"}</dd></div>
            <div><dt>Cloudflare</dt><dd>{run?.providers.cloudflare || "—"}</dd></div>
            <div><dt>Runtype</dt><dd>{run?.providers.runtype || "—"}</dd></div>
            <div><dt>Mitosis</dt><dd>{run?.providers.mitosis || "—"}</dd></div>
            <div><dt>Mistral</dt><dd>{run?.providers.mistral || "FUTURE_OPTIONAL"}</dd></div>
          </dl>
        </section>

        {run?.result_panel && (
          <section className="hlFinal">
            <h2>RESULT</h2>
            <ul>
              {Object.entries(run.result_panel).map(([k, v]) => (
                <li key={k}>
                  <strong>{k}</strong> {String(v)}
                </li>
              ))}
            </ul>
            <button
              className="hlPrimary"
              onClick={() => void act("focus", { focus: "divergence" })}
            >
              TRACE THE REPAIR
            </button>
          </section>
        )}

        <section className="hlPanel">
          <header>
            <button className="hlSecondary" type="button" onClick={() => setDrawer((d) => !d)}>
              REAL HYDRADG EVIDENCE
            </button>
          </header>
          {drawer && (
            <div>
              <div className="hlCenterBar">
                {(["historical", "demo", "dev", "future"] as const).map((t) => (
                  <button key={t} className="hlSecondary" type="button" onClick={() => setEvidenceTab(t)}>
                    {t}
                  </button>
                ))}
              </div>
              {evidenceTab === "historical" && (
                <div className="hlMuted">
                  <p>LongMemEval-S full500 · n=500 · scored=470 · abstain=30</p>
                  <p>K5 Reference Hit@5≈0.96383 Recall@5≈0.90660 · Graph/context Hit@5≈0.94468 Recall@5≈0.84603 (NEGATIVE/null advantage)</p>
                  <p>K10 Reference Hit@10≈0.97872 Recall@10≈0.94535 · depth effect; NO_MODEL_BENEFIT</p>
                  <p>Source: docs/FINAL_ELIGIBILITY_EVIDENCE_MATRIX.json + CONTROL_RECONCILIATION_RECEIPT.json</p>
                </div>
              )}
              {evidenceTab === "demo" && (
                <div className="hlMuted">
                  <p>Session {run?.session_id || "—"} · run {run?.run_id || "—"}</p>
                  <p>FCG {short(run?.fcg_root_initial)} → {short(run?.fcg_root_current)}</p>
                  <p>Transitions: {run?.transitions.length || 0}</p>
                </div>
              )}
              {evidenceTab === "dev" && (
                <div className="hlMuted">
                  <p>Daisy 1020 matrix: NOT_ESTABLISHED (accounted_so_far=0)</p>
                  <p>ECA_RESTORATION_EMPIRICAL_STATE=NOT_ESTABLISHED (ECA EXT80 is transparent deterministic demo substrate)</p>
                  <p>Vithia LongMemEval companion: NOT_EXECUTED</p>
                </div>
              )}
              {evidenceTab === "future" && (
                <div className="hlMuted">
                  <p>Mistral: FUTURE_OPTIONAL</p>
                  <p>BEAM-10M: DEFERRED</p>
                  <p>Cloudflare Worker DO stub present — NOT LIVE until deploy + HYDRALAMP_CF_WORKER_URL</p>
                </div>
              )}
            </div>
          )}
        </section>

        <section className="hlPanel">
          <header>
            <strong>STATISTICS (receipt-bound)</strong>
          </header>
          <div className="hlMuted">
            <p>K5: A Hit 0.96383 / D Hit 0.94468 · A Recall 0.90660 / D Recall 0.84603 · evidence-path 0.63787</p>
            <p>K10: A Hit 0.97872 / D Hit 0.97021 · A Recall 0.94535 / D Recall 0.92273 · evidence-path 0.51511</p>
            <p>ΔHit K5 A−D positive for reference; graph/context did not establish advantage (preserve K5 negative/null).</p>
            <p>Paired McNemar on full500 ABCD case vectors: NOT_FOUND — do not invent significance.</p>
          </div>
        </section>
      </div>
    </main>
  );
}
