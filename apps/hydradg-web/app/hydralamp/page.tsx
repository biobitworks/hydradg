"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import SiteNav from "@/components/SiteNav";
import "./hydralamp.css";

type Ev = {
  run_id: string;
  seq: number;
  timestamp: string;
  lane: string;
  model_id?: string;
  runtype_execution_id?: string | null;
  type: string;
  tool?: string;
  summary: string;
  public_payload?: Record<string, unknown>;
};

type Perturbation =
  | "CONTROL"
  | "INVALID_PROOF"
  | "REPLAYED_PROOF"
  | "BROKEN_AUTHORIZATION_EDGE";

const LANE_COLOR: Record<string, string> = {
  "agent-a": "#7dd3fc",
  "agent-b": "#f9a8d4",
  "agent-c": "#fde68a",
  verifier: "#9bd59c",
  reference: "#e8e5dc",
  custody: "#c4b5fd",
};

export default function HydraLampLivePage() {
  const [demo20, setDemo20] = useState(false);
  const [perturbation, setPerturbation] = useState<Perturbation>("INVALID_PROOF");
  const [runId, setRunId] = useState<string | null>(null);
  const [mode, setMode] = useState<string>("");
  const [label, setLabel] = useState<string>("");
  const [events, setEvents] = useState<Ev[]>([]);
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef<number | null>(null);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    setDemo20(q.get("demo") === "20s");
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

  const start = useCallback(
    async (opts?: { synthetic?: boolean }) => {
      stopStream();
      setBusy(true);
      setEvents([]);
      setStatus(null);
      startRef.current = Date.now();
      setElapsed(0);

      const res = await fetch("/api/hydralamp/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          perturbation,
          demo_20s: demo20,
          allow_synthetic_ui_fixture: Boolean(opts?.synthetic),
        }),
      });
      const data = await res.json();
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
          setEvents((prev) => [...prev, payload as Ev]);
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
    [demo20, perturbation, refreshStatus, stopStream],
  );

  // Auto-start for recording mode
  useEffect(() => {
    if (!demo20) return;
    const t = setTimeout(() => {
      void start({ synthetic: true });
    }, 400);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demo20]);

  const laneEvents = useMemo(() => {
    const map: Record<string, Ev[]> = { "agent-a": [], "agent-b": [], "agent-c": [], verifier: [], reference: [] };
    for (const ev of events) {
      if (!map[ev.lane]) map[ev.lane] = [];
      map[ev.lane].push(ev);
    }
    return map;
  }, [events]);

  const finalFrame = (status?.final_frame || null) as null | {
    decisions: Array<{ lane: string; model_id: string; decision: string }>;
    earliest_divergence: string | null;
    fcg: { root_before: string | null; root_after: string | null };
    hydradb: { state: string };
  };

  const seconds = (elapsed / 1000).toFixed(1);

  return (
    <main className="hlPage">
      <SiteNav />
      <div className="hlInner">
        <header className="hlHero">
          <p className="hlEyebrow">HydraLamp × Runtype</p>
          <h1>Models propose. Custody decides.</h1>
          <p className="hlLead">
            Real streamed tool traces into a deterministic verifier. Synthetic fixtures stay labeled.
            No fabricated model activity.
          </p>
          {label && <p className="hlBanner">{label}</p>}
        </header>

        <section className="hlControls">
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
            {busy ? "RUNNING…" : "RUN LIVE EXPERIMENT"}
          </button>
          <button
            className="hlSecondary"
            disabled={busy}
            onClick={() => void start({ synthetic: true })}
            title="Layout-only path when Runtype key absent"
          >
            SYNTHETIC UI FIXTURE
          </button>
          <div className="hlMeta">
            <span>{demo20 ? "DEMO 20s" : "LIVE"}</span>
            <span>{seconds}s</span>
            {runId && <span>{runId}</span>}
            {mode && <span>{mode}</span>}
          </div>
        </section>

        <section className="hlGrid">
          <Lane
            title="REFERENCE / PERTURBATION"
            color={LANE_COLOR.reference}
            events={laneEvents.reference || []}
            badge="deterministic fixture"
          />
          <Lane title="MODEL A" color={LANE_COLOR["agent-a"]} events={laneEvents["agent-a"] || []} />
          <Lane title="MODEL B" color={LANE_COLOR["agent-b"]} events={laneEvents["agent-b"] || []} />
          <Lane title="MODEL C" color={LANE_COLOR["agent-c"]} events={laneEvents["agent-c"] || []} />
          <Lane
            title="DETERMINISTIC VERIFIER"
            color={LANE_COLOR.verifier}
            events={[...(laneEvents.verifier || []), ...(laneEvents.custody || [])]}
            badge="not a model"
            wide
          />
        </section>

        <svg className="hlGraph" viewBox="0 0 1000 280" role="img" aria-label="HydraLamp event graph">
          <defs>
            <radialGradient id="glow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#e8e5dc" stopOpacity="0.55" />
              <stop offset="100%" stopColor="#e8e5dc" stopOpacity="0" />
            </radialGradient>
          </defs>
          <circle cx="120" cy="140" r="34" fill="url(#glow)" />
          <circle cx="120" cy="140" r="18" fill="#e8e5dc" />
          <text x="120" y="185" textAnchor="middle" fill="#9298a2" fontSize="12">
            MUTATION
          </text>
          {(["agent-a", "agent-b", "agent-c"] as const).map((lane, i) => {
            const y = 50 + i * 90;
            const color = LANE_COLOR[lane];
            const tools = (laneEvents[lane] || []).filter((e) => e.type === "TOOL_CALL");
            return (
              <g key={lane}>
                <path
                  d={`M140,140 C280,140 280,${y} 360,${y}`}
                  stroke={color}
                  strokeWidth="2"
                  fill="none"
                  opacity="0.85"
                >
                  <animate attributeName="stroke-dasharray" from="0 400" to="400 0" dur="1.2s" fill="freeze" />
                </path>
                {tools.map((t, ti) => (
                  <g key={`${lane}-${ti}`}>
                    <circle cx={420 + ti * 70} cy={y} r="10" fill={color} />
                    <text x={420 + ti * 70} y={y + 28} textAnchor="middle" fill="#b0b5bc" fontSize="10">
                      {(t.tool || "").replace("_", "\n").slice(0, 12)}
                    </text>
                  </g>
                ))}
              </g>
            );
          })}
          <rect x="780" y="100" width="160" height="80" rx="10" fill="#15181d" stroke="#9bd59c" />
          <text x="860" y="145" textAnchor="middle" fill="#9bd59c" fontSize="13">
            VERIFIER
          </text>
        </svg>

        {finalFrame && (
          <section className="hlFinal">
            <h2>HYDRALAMP</h2>
            <p>3 models investigated the same corrupted state.</p>
            <ul>
              {finalFrame.decisions.map((d) => (
                <li key={d.lane}>
                  <strong>{d.lane.toUpperCase()}</strong> {d.model_id}: {d.decision}
                </li>
              ))}
            </ul>
            <p>
              Earliest divergence: <code>{finalFrame.earliest_divergence || "none"}</code>
            </p>
            <p>
              FCG: <code>{(finalFrame.fcg.root_before || "").slice(0, 10)}</code> →{" "}
              <code>{(finalFrame.fcg.root_after || "").slice(0, 10)}</code>
            </p>
            <p>HydraDB: {finalFrame.hydradb.state}</p>
            <p className="hlTag">Models propose. Custody decides.</p>
          </section>
        )}
      </div>
      
    </main>
  );
}

function Lane({
  title,
  color,
  events,
  badge,
  wide,
}: {
  title: string;
  color: string;
  events: Ev[];
  badge?: string;
  wide?: boolean;
}) {
  const active = events.some((e) => e.type === "MODEL_ACTIVE") && !events.some((e) => e.type === "MODEL_FINAL" || e.type === "TIMEOUT" || e.type === "ERROR");
  return (
    <article
      style={{
        gridColumn: wide ? "1 / -1" : undefined,
        border: `1px solid ${color}55`,
        borderRadius: 14,
        padding: "0.9rem 1rem",
        background: "#101216",
        minHeight: 150,
      }}
    >
      <header style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 8 }}>
        <strong style={{ color }}>{title}</strong>
        <span style={{ color: "#9298a2", fontSize: 11 }}>
          {badge || (active ? "MODEL ACTIVE / WAITING" : `${events.length} events`)}
        </span>
      </header>
      <ol style={{ margin: 0, paddingLeft: "1.1rem", fontSize: 12, color: "#c8ccd3" }}>
        {events.slice(-8).map((e) => (
          <li key={`${e.seq}-${e.type}`}>
            <code style={{ color }}>{e.type}</code> {e.summary}
            {e.runtype_execution_id ? ` · ${e.runtype_execution_id}` : ""}
          </li>
        ))}
        {!events.length && <li style={{ color: "#666" }}>waiting for real events…</li>}
      </ol>
    </article>
  );
}
