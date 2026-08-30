"use client";

type HashRow = {
  label: string;
  hash: string;
  github_graph: string;
  project_fcg: string;
  status: "HISTORICAL_MATCH" | "PRESENT" | "RECONCILIATION_REQUIRED" | "NOT_ESTABLISHED";
};

const COMPARISON_ROWS: readonly HashRow[] = [
  {
    label: "Historical T3 bounded FCO root",
    hash: "d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1",
    github_graph: "Retained historical hosted projection/readback scope",
    project_fcg: "36 canonical FCO scope · SUPERSEDED_BY later project states",
    status: "HISTORICAL_MATCH",
  },
  {
    label: "Historical T3 24-edge root",
    hash: "7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab",
    github_graph: "Retained historical hosted projection/readback scope",
    project_fcg: "24 canonical edge scope only",
    status: "HISTORICAL_MATCH",
  },
  {
    label: "Expanded project FCG computed root",
    hash: "bb0adb5a6453a6493e51363f33e7782b3d79dd82b27ceb8678173ce53f1ce72b",
    github_graph: "Expanded hosted/root comparison not independently established",
    project_fcg: "Retained computed scope: 653 FCO nodes / 1,692 edges",
    status: "RECONCILIATION_REQUIRED",
  },
  {
    label: "Deterministic information-savings receipt",
    hash: "8d60ab68f989e88aec9446fc06739d2c52f4af911b673af058889c9f52afdf36",
    github_graph: "Repository artifact present via GitHub connector source lane",
    project_fcg: "Scale-economics evidence receipt; expanded hosted FCO readback not established",
    status: "PRESENT",
  },
  {
    label: "Public canary source identity",
    hash: "303b3fab6fd8831b84a37f789aa4ef1f1ab78a808572eddf8632d1b88f97e1d5",
    github_graph: "Repository identity retained",
    project_fcg: "Canonical custody/readback canary identity",
    status: "PRESENT",
  },
];

function statusClass(status: HashRow["status"]) {
  return status === "HISTORICAL_MATCH" || status === "PRESENT" ? "pill pillGood" : "pill pillMuted";
}

export default function GraphHashComparison() {
  return (
    <section className="panel" aria-label="GitHub Graph vs Project FCG Comparison">
      <div className="panelHead">
        <div>
          <p className="eyebrow">Graph reconciliation · scoped, not flattened</p>
          <h2>GitHub connector graph vs canonical project FCG</h2>
        </div>
        <a
          className="secondary"
          href="https://dashboard.hydradb.com/graph?tenant_id=hydradg&all_sub_tenants=true&app_source=github"
          target="_blank"
          rel="noreferrer"
        >
          Open HydraDB Dashboard ↗
        </a>
      </div>
      <p className="muted">
        The GitHub connector graph and the canonical project FCG are related projections, not the same graph.
        Historical 36-FCO/24-edge parity remains retained for its bounded T3 scope. The expanded conversation/project FCG
        must earn a new hosted comparison/readback receipt; it cannot inherit the historical green state.
      </p>

      <div className="tableWrap" style={{ overflowX: "auto", margin: "1rem 0" }}>
        <table className="small" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid rgba(255,255,255,0.15)", background: "rgba(255,255,255,0.02)" }}>
              <th style={{ padding: "8px" }}>Scope / entity</th>
              <th style={{ padding: "8px" }}>SHA-256 / root</th>
              <th style={{ padding: "8px" }}>GitHub graph / hosted lane</th>
              <th style={{ padding: "8px" }}>Canonical project FCG</th>
              <th style={{ padding: "8px" }}>State</th>
            </tr>
          </thead>
          <tbody>
            {COMPARISON_ROWS.map((row) => (
              <tr key={row.label} style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                <td style={{ padding: "8px", fontWeight: "bold" }}>{row.label}</td>
                <td style={{ padding: "8px" }}><span className="mono small">{row.hash.slice(0, 20)}…</span></td>
                <td style={{ padding: "8px" }}>{row.github_graph}</td>
                <td style={{ padding: "8px" }}>{row.project_fcg}</td>
                <td style={{ padding: "8px" }}><span className={statusClass(row.status)} style={{ fontSize: "11px", fontWeight: "bold" }}>{row.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="small muted note">
        Fractal custody means lower-level roots can become evidence inside higher-level FCOs while retaining explicit scope,
        ordering and provenance. A computed root is not automatically a Merkle commitment; project state remains NOT_MERKLE_COMMITTED unless an actual commitment operation is recorded.
      </p>
    </section>
  );
}
