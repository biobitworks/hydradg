"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";
import SiteNav from "@/components/SiteNav";
import JudgeMetricStrip from "@/components/hydralamp/JudgeMetricStrip";
import { verifyEventHash } from "@/lib/hydralamp/hashBrowser";
import "./hydralamp.css";

const CustodyGraph = dynamic(() => import("@/components/hydralamp/CustodyGraph"), {
  ssr: false,
  loading: () => <div className="hlCyto hlCytoPlaceholder">Loading graph…</div>,
});

type Ev = {
  run_id: string;
  seq: number;
  timestamp: string;
  lane: string;
  actor_id?: string;
  model_id?: string | null;
  execution_id?: string | null;
  runtype_execution_id?: string | null;
  local_execution_id?: string | null;
  type: string;
  tool?: string;
  summary: string;
  public_payload?: Record<string, unknown>;
  prev_event_hash?: string;
  event_hash?: string;
  context_hash_before?: string | null;
  context_hash_after?: string | null;
  model_output_hash?: string | null;
  proposal_hash?: string | null;
  fcg_root_before?: string | null;
  fcg_root_after?: string | null;
  context_delta?: {
    nodes_added: number;
    nodes_removed: number;
    edges_added: number;
    edges_removed: number;
    contradictions_delta: number;
    quarantine_delta: number;
    canonical_delta: number;
    cloud_drift_0_100: number | "NOT_COMPUTED";
  } | null;
  verification_result?: string | null;
  evidence_class?: string;
};

type Perturbation =
  | "CONTROL"
  | "INVALID_PROOF"
  | "REPLAYED_PROOF"
  | "BROKEN_AUTHORIZATION_EDGE";

type ModeRequest = "DETERMINISTIC_FIXTURE" | "LOCAL_MODEL_GUM_OLLARMA" | "LIVE_RUNTYPE";

const LANE_META: Record<string, { title: string; shape: string; tone: string }> = {
  "agent-a": { title: "QWEN / A", shape: "◆", tone: "#7dd3fc" },
  "agent-b": { title: "MISTRAL / B", shape: "●", tone: "#f9a8d4" },
  "agent-c": { title: "PEER / C", shape: "▲", tone: "#fde68a" },
  poison: { title: "POISON", shape: "⬡", tone: "#fb7185" },
  repair: { title: "REPAIR", shape: "★", tone: "#38bdf8" },
  verifier: { title: "VERIFIER", shape: "■", tone: "#9bd59c" },
  reference: { title: "REFERENCE", shape: "○", tone: "#e8e5dc" },
  custody: { title: "CUSTODY", shape: "▣", tone: "#c4b5fd" },
};

function shortHash(h?: string | null) {
  if (!h) return "—";
  return `${h.slice(0, 4)}…${h.slice(-2)}`;
}

export default function HydraLampLivePage() {
  const [demo20, setDemo20] = useState(false);
  const [perturbation, setPerturbation] = useState<Perturbation>("INVALID_PROOF");
  const [modeReq, setModeReq] = useState<ModeRequest>("DETERMINISTIC_FIXTURE");
  const [vercelRuntime, setVercelRuntime] = useState(false);
  const [runId, setRunId] = useState<string | null>(null);
  const [mode, setMode] = useState<string>("");
  const [label, setLabel] = useState<string>("");
  const [events, setEvents] = useState<Ev[]>([]);
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [hashChecks, setHashChecks] = useState<
    Record<number, { verified: boolean; client: string; server: string | null }>
  >({});
  const [chainGap, setChainGap] = useState<string | null>(null);
  const [judgeSurface, setJudgeSurface] = useState<Record<string, unknown> | null>(null);
  const startRef = useRef<number | null>(null);
  const esRef = useRef<EventSource | null>(null);
  const lastHashRef = useRef<string | null>(null);

  useEffect(() => {
    void fetch("/demo/judge-metric-surface.json")
      .then((r) => r.json())
      .then((d) => setJudgeSurface(d))
      .catch(() => {
        /* frozen defaults in component */
      });
  }, []);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    setDemo20(q.get("demo") === "20s");
  }, []);

  useEffect(() => {
    void fetch("/api/hydralamp/run")
      .then((r) => r.json())
      .then((data: { vercel_runtime?: boolean; modes?: string[] }) => {
        setVercelRuntime(Boolean(data.vercel_runtime));
        if (data.vercel_runtime && modeReq === "LOCAL_MODEL_GUM_OLLARMA") {
          setModeReq("DETERMINISTIC_FIXTURE");
        }
      })
      .catch(() => {
        /* inventory is optional */
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!busy || !startRef.current) return;
    const t = setInterval(() => {
      setElapsed(Date.now() - (startRef.current || Date.now()));
    }, 100);
    return () => clearInterval(t);
  }, [busy]);

  const stopStream = useCallback(() => {
    esRef.current?.close();
    esRef.current = null;
  }, []);

  const refreshStatus = useCallback(async (id: string) => {
    const r = await fetch(`/api/hydralamp/status?run_id=${id}`);
    if (r.ok) setStatus(await r.json());
  }, []);

  const ingestEvent = useCallback(async (payload: Ev) => {
    setEvents((prev) => [...prev, payload]);
    if (payload.prev_event_hash && lastHashRef.current && payload.prev_event_hash !== lastHashRef.current) {
      setChainGap(`CHAIN GAP at seq=${payload.seq}: prev≠last`);
    }
    if (payload.event_hash) lastHashRef.current = payload.event_hash;

    if (payload.event_hash) {
      const v = await verifyEventHash(payload as unknown as Record<string, unknown>);
      setHashChecks((prev) => ({
        ...prev,
        [payload.seq]: {
          verified: v.verified,
          client: v.client_recompute,
          server: v.server_hash,
        },
      }));
    }
  }, []);

  const start = useCallback(
    async (opts?: { mode?: ModeRequest }) => {
      stopStream();
      setBusy(true);
      setEvents([]);
      setStatus(null);
      setHashChecks({});
      setChainGap(null);
      lastHashRef.current = null;
      startRef.current = Date.now();
      setElapsed(0);

      const chosen = opts?.mode || modeReq;
      const res = await fetch("/api/hydralamp/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          perturbation,
          demo_20s: demo20,
          mode: chosen,
          allow_synthetic_ui_fixture: chosen === "DETERMINISTIC_FIXTURE",
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setLabel(data.error || data.label || "BLOCKED");
        setMode(data.mode || "BLOCKED");
        setBusy(false);
        return;
      }
      setRunId(data.run_id);
      setMode(data.mode);
      setLabel(data.label || "");

      const es = new EventSource(data.stream_url);
      esRef.current = es;
      es.onmessage = (msg) => {
        try {
          const payload = JSON.parse(msg.data);
          if (payload.type === "DONE_SENTINEL") {
            void refreshStatus(data.run_id);
            setBusy(false);
            es.close();
            return;
          }
          void ingestEvent(payload as Ev);
          if (payload.type === "DONE") {
            void refreshStatus(data.run_id);
            setBusy(false);
          }
        } catch {
          /* ignore malformed */
        }
      };
      es.onerror = () => {
        void refreshStatus(data.run_id);
      };
    },
    [demo20, ingestEvent, modeReq, perturbation, refreshStatus, stopStream],
  );

  useEffect(() => {
    if (!demo20) return;
    const t = setTimeout(() => {
      void start({ mode: "DETERMINISTIC_FIXTURE" });
    }, 400);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demo20]);

  const laneEvents = useMemo(() => {
    const map: Record<string, Ev[]> = {};
    for (const ev of events) {
      if (!map[ev.lane]) map[ev.lane] = [];
      map[ev.lane].push(ev);
    }
    return map;
  }, [events]);

  const latestDelta = useMemo(() => {
    for (let i = events.length - 1; i >= 0; i--) {
      if (events[i].context_delta) return events[i].context_delta;
    }
    return null;
  }, [events]);

  const graphNodes = (status?.graph_nodes || []) as Array<{
    id: string;
    label: string;
    visual_class: string;
  }>;
  const graphEdges = (status?.graph_edges || []) as Array<{
    id: string;
    source: string;
    target: string;
    label: string;
  }>;

  const pulseIds = useMemo(() => {
    const last = [...events].reverse().find((e) => e.type === "QUARANTINE" || e.type === "FCG_APPEND");
    if (!last?.public_payload) return [];
    return [];
  }, [events]);

  const verifiedCount = Object.values(hashChecks).filter((h) => h.verified).length;
  const mismatchCount = Object.values(hashChecks).filter((h) => !h.verified).length;
  const seconds = (elapsed / 1000).toFixed(1);
  const demoPhase =
    demo20 && elapsed < 3000
      ? "0–3s reference KG"
      : demo20 && elapsed < 7000
        ? "3–7s model context"
        : demo20 && elapsed < 11000
          ? "7–11s proposals diverge"
          : demo20 && elapsed < 14000
            ? "11–14s verifier"
            : demo20 && elapsed < 17000
              ? "14–17s quarantine / repair"
              : demo20
                ? "17–20s root + receipt"
                : null;

  const finalFrame = status?.final_frame as
    | {
        decisions: Array<Record<string, string | null | undefined>>;
        earliest_divergence: string | null;
        fcg: { root_before: string | null; root_after: string | null };
        quarantine?: { count: number };
        hydradb: { state: string };
        hash_chain_ok?: boolean;
      }
    | null
    | undefined;

  return (
    <main className="hlPage">
      <SiteNav />
      <div className="hlInner hlMicroscope">
        <header className="hlHero">
          <p className="hlEyebrow">HydraLamp Custody Microscope</p>
          <h1>Models propose. Custody decides.</h1>
          <p className="hlLead">
            SHA-256 proves byte/state identity only. Context change is structural delta (+ CloudDrift when
            resolved) — never hash Hamming distance.
          </p>
          {vercelRuntime && (
            <p className="hlBanner">
              Vercel is the public control plane. Ollarma / GUM Doctor are not hosted here. Scientific
              execution authority remains magicSTUDIObox.local.
            </p>
          )}
          {label && <p className="hlBanner">{label}</p>}
          {mode === "LIVE_RUNTYPE" && <p className="hlLive">LIVE RUNTYPE</p>}
          {chainGap && <p className="hlBanner">{chainGap}</p>}
        </header>

        <JudgeMetricStrip data={judgeSurface as never} />

        <section className="hlControls">
          <label>
            Mode
            <select
              value={modeReq}
              onChange={(e) => setModeReq(e.target.value as ModeRequest)}
              disabled={busy}
            >
              <option value="DETERMINISTIC_FIXTURE">DETERMINISTIC_FIXTURE</option>
              {!vercelRuntime && (
                <option value="LOCAL_MODEL_GUM_OLLARMA">LOCAL_MODEL_GUM_OLLARMA</option>
              )}
              <option value="LIVE_RUNTYPE">LIVE_RUNTYPE</option>
            </select>
          </label>
          <label>
            Perturbation
            <select
              value={perturbation}
              onChange={(e) => setPerturbation(e.target.value as Perturbation)}
              disabled={busy}
            >
              <option value="CONTROL">CONTROL</option>
              <option value="INVALID_PROOF">INVALID PROOF</option>
              <option value="REPLAYED_PROOF">REPLAYED PROOF</option>
              <option value="BROKEN_AUTHORIZATION_EDGE">BROKEN AUTHORIZATION EDGE</option>
            </select>
          </label>
          <button className="hlPrimary" disabled={busy} onClick={() => void start()}>
            {busy ? "RUNNING…" : "RUN"}
          </button>
          <div className="hlMeta">
            <span>{demo20 ? "DEMO 20s" : "LIVE"}</span>
            {demoPhase && <span>{demoPhase}</span>}
            <span>{seconds}s</span>
            {runId && <span>{runId}</span>}
            {mode && <span>{mode}</span>}
            <span>
              HASH ✓{verifiedCount} ✕{mismatchCount}
            </span>
          </div>
        </section>

        <section className="hlLanes">
          {(["agent-a", "agent-b", "agent-c", "poison", "repair", "verifier"] as const).map((lane) => (
            <LaneCard key={lane} lane={lane} events={laneEvents[lane] || []} hashChecks={hashChecks} />
          ))}
        </section>

        <section className="hlMid">
          <div className="hlPanel">
            <header>
              <strong>LIVE KG / FCG</strong>
              <span className="hlHint">shape + label + color · Cytoscape.js</span>
            </header>
            <CustodyGraph nodes={graphNodes} edges={graphEdges} pulseIds={pulseIds} />
            <div className="hlLegend">
              <span>○ reference</span>
              <span>□ canonical</span>
              <span>◆ proposal</span>
              <span>⬡ quarantine</span>
              <span>△ contradicted</span>
              <span>⬡ verified</span>
              <span>★ repaired</span>
            </div>
          </div>
          <div className="hlPanel">
            <header>
              <strong>CONTEXT Δ</strong>
              <span className="hlHint">not hash distance</span>
            </header>
            {latestDelta ? (
              <ul className="hlDelta">
                <li>
                  nodes <b>+{latestDelta.nodes_added}</b> / −{latestDelta.nodes_removed}
                </li>
                <li>
                  edges <b>+{latestDelta.edges_added}</b> / −{latestDelta.edges_removed}
                </li>
                <li>contradictions Δ {latestDelta.contradictions_delta}</li>
                <li>quarantine Δ {latestDelta.quarantine_delta}</li>
                <li>canonical Δ {latestDelta.canonical_delta}</li>
                <li>
                  CloudDrift={" "}
                  {latestDelta.cloud_drift_0_100 === "NOT_COMPUTED"
                    ? "NOT_COMPUTED"
                    : latestDelta.cloud_drift_0_100}
                </li>
              </ul>
            ) : (
              <p className="hlMuted">Waiting for structural delta events…</p>
            )}
            <HashInspector events={events} hashChecks={hashChecks} />
          </div>
        </section>

        <section className="hlPanel hlTimeline">
          <header>
            <strong>HASH / CUSTODY TIMELINE</strong>
            <span className="hlHint">client Web Crypto recompute</span>
          </header>
          <ol className="hlChain">
            {events.map((e) => {
              const chk = hashChecks[e.seq];
              const rootSame =
                e.fcg_root_before && e.fcg_root_after && e.fcg_root_before === e.fcg_root_after;
              const rootChanged =
                e.fcg_root_before && e.fcg_root_after && e.fcg_root_before !== e.fcg_root_after;
              return (
                <li key={e.seq} className={chk?.verified ? "ok" : chk ? "bad" : ""}>
                  <span className="seq">e{e.seq}</span>
                  <span className="type">{e.type}</span>
                  <span className="hash" title={e.event_hash || ""}>
                    {shortHash(e.event_hash)}
                  </span>
                  {chk?.verified ? (
                    <span className="ver">VERIFIED ✓</span>
                  ) : chk ? (
                    <span className="ver bad">HASH MISMATCH ✕</span>
                  ) : (
                    <span className="ver">…</span>
                  )}
                  {rootSame && <span className="root">ROOT SAME ✓</span>}
                  {rootChanged && (
                    <span className="root chg">
                      {shortHash(e.fcg_root_before)}→{shortHash(e.fcg_root_after)} CHANGED ✓
                    </span>
                  )}
                </li>
              );
            })}
            {!events.length && <li className="hlMuted">No SSE events yet</li>}
          </ol>
        </section>

        {finalFrame && (
          <section className="hlFinal">
            <h2>HYDRALAMP</h2>
            <p>Models propose. Custody decides.</p>
            <ul>
              {finalFrame.decisions.map((d) => (
                <li key={String(d.lane)}>
                  <strong>{String(d.lane).toUpperCase()}</strong> {d.model_id}: {d.decision}
                  {d.context_hash ? ` · CTX=${shortHash(d.context_hash)}` : ""}
                  {d.fcg_before || d.fcg_after
                    ? ` · FCG=${shortHash(d.fcg_before)}→${shortHash(d.fcg_after)}`
                    : ""}
                </li>
              ))}
            </ul>
            <p>
              Quarantine count: {finalFrame.quarantine?.count ?? 0} · Hash chain:{" "}
              {finalFrame.hash_chain_ok ? "OK" : "CHECK"}
            </p>
            <p>
              FCG: <code>{(finalFrame.fcg.root_before || "").slice(0, 10)}</code> →{" "}
              <code>{(finalFrame.fcg.root_after || "").slice(0, 10)}</code>
            </p>
            <p className="hlTag">Models propose. Custody decides.</p>
          </section>
        )}
      </div>
    </main>
  );
}

function LaneCard({
  lane,
  events,
  hashChecks,
}: {
  lane: string;
  events: Ev[];
  hashChecks: Record<number, { verified: boolean }>;
}) {
  const meta = LANE_META[lane] || { title: lane, shape: "•", tone: "#94a3b8" };
  const last = events[events.length - 1];
  return (
    <article className="hlLane" style={{ borderColor: `${meta.tone}66` }}>
      <header>
        <span style={{ color: meta.tone }}>
          {meta.shape} {meta.title}
        </span>
        <span>{events.length}</span>
      </header>
      <ol>
        {events.slice(-5).map((e) => (
          <li key={e.seq}>
            <code style={{ color: meta.tone }}>{e.type}</code> {e.summary}
            {e.model_id ? ` · MODEL=${e.model_id}` : ""}
            {e.execution_id || e.runtype_execution_id || e.local_execution_id
              ? ` · EXEC=${e.execution_id || e.runtype_execution_id || e.local_execution_id}`
              : ""}
            {hashChecks[e.seq]?.verified ? " · ✓" : ""}
          </li>
        ))}
        {!events.length && <li className="hlMuted">idle</li>}
      </ol>
      {last?.verification_result && (
        <footer>
          VERIFIER={last.verification_result} · FCG={shortHash(last.fcg_root_before)}→
          {shortHash(last.fcg_root_after)}
        </footer>
      )}
    </article>
  );
}

function HashInspector({
  events,
  hashChecks,
}: {
  events: Ev[];
  hashChecks: Record<number, { verified: boolean; client: string; server: string | null }>;
}) {
  const last = [...events].reverse().find((e) => e.event_hash);
  if (!last) return null;
  const chk = hashChecks[last.seq];
  return (
    <div className="hlInspect">
      <div>SERVER HASH {shortHash(chk?.server || last.event_hash)}</div>
      <div>CLIENT RECOMPUTE {shortHash(chk?.client)}</div>
      <div>{chk?.verified ? "VERIFIED ✓" : chk ? "HASH MISMATCH ✕" : "…"}</div>
      <p className="hlHint">Never verified merely because a hash string exists.</p>
    </div>
  );
}
