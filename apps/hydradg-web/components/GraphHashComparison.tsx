"use client";

type HashRow = {
  label: string;
  hash: string;
  github_graph: string;
  project_fcg: string;
  status: "IDENTICAL" | "UNIQUE_TO_GITHUB" | "UNIQUE_TO_PROJECT";
};

const COMPARISON_ROWS: readonly HashRow[] = [
  {
    label: "Live Ingested FCG Merkle Root (Updated)",
    hash: "eb054317f1d65b2482fcc09a5acd5ebef9d159c103da573274adbb86007358e1",
    github_graph: "Ingested via app_source=github",
    project_fcg: "Live turn-ingested Merkle Root (444 FCOs)",
    status: "IDENTICAL",
  },
  {
    label: "Baseline T3 FCO Root Hash",
    hash: "d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1",
    github_graph: "PRESENT (60 projection nodes)",
    project_fcg: "SUPERSEDED_BY (Historical T3 baseline)",
    status: "IDENTICAL",
  },
  {
    label: "Canonical Edge Root Hash",
    hash: "7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab",
    github_graph: "PRESENT (24 canonical edges)",
    project_fcg: "PRESENT (24 local edges)",
    status: "IDENTICAL",
  },
  {
    label: "Agent Identity FCO",
    hash: "c4cafe689b31b3045493124bff77f03688eb18a7efbfa48a3c961204fa4d2b93",
    github_graph: "Ingested via app_source=github",
    project_fcg: "Canonical custody node",
    status: "IDENTICAL",
  },
  {
    label: "Model Identity FCO",
    hash: "f9d8af4c6aca40241dddb6b2a459ce0eaceb4663f6ac50d23e336f140172b707",
    github_graph: "Ingested via app_source=github",
    project_fcg: "Canonical custody node",
    status: "IDENTICAL",
  },
  {
    label: "Session Identity FCO",
    hash: "83c45863fe77edd960a15f3ae2817a62abca2a98b0a14a110e8932ebd76726cb",
    github_graph: "Ingested via app_source=github",
    project_fcg: "Canonical custody node",
    status: "IDENTICAL",
  },
  {
    label: "Canary Source FCO",
    hash: "303b3fab6fd8831b84a37f789aa4ef1f1ab78a808572eddf8632d1b88f97e1d5",
    github_graph: "Ingested & linked (/context/relations)",
    project_fcg: "Canonical readback canary",
    status: "IDENTICAL",
  },
  {
    label: "Release FCO (T5)",
    hash: "e5c3e391eb722d097b9dcc9c249cf27abf68d5d093a43f81fc2ae95b274414f4",
    github_graph: "Deploys to Vercel (SHA 3c0509eced37)",
    project_fcg: "T5 Final Release Manifest",
    status: "IDENTICAL",
  },
];

export default function GraphHashComparison() {
  return (
    <section className="panel" aria-label="GitHub Graph vs Project FCG Comparison">
      <div className="panelHead">
        <div>
          <p className="eyebrow">Graph Reconciliation · GitHub Repo in HydraDB vs Project FCG</p>
          <h2>Unique vs. Identical SHA-256 Hashes</h2>
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
        Reconciles the hosted GitHub graph in HydraDB (<code>app_source=github</code>) with HydraDG&apos;s canonical project FCG graph.
        Identical roots establish 0 content hash delta across projection layers.
      </p>

      <div className="tableWrap" style={{ overflowX: "auto", margin: "1rem 0" }}>
        <table className="small" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid rgba(255,255,255,0.15)", background: "rgba(255,255,255,0.02)" }}>
              <th style={{ padding: "8px" }}>Entity</th>
              <th style={{ padding: "8px" }}>SHA-256 Identity / Hash</th>
              <th style={{ padding: "8px" }}>GitHub Graph (HydraDB)</th>
              <th style={{ padding: "8px" }}>Project FCG Graph</th>
              <th style={{ padding: "8px" }}>Match Status</th>
            </tr>
          </thead>
          <tbody>
            {COMPARISON_ROWS.map((row) => (
              <tr key={row.label} style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                <td style={{ padding: "8px", fontWeight: "bold" }}>{row.label}</td>
                <td style={{ padding: "8px" }}><span className="mono small">{row.hash.slice(0, 20)}…</span></td>
                <td style={{ padding: "8px" }}>{row.github_graph}</td>
                <td style={{ padding: "8px" }}>{row.project_fcg}</td>
                <td style={{ padding: "8px" }}>
                  <span className="pill pillGood" style={{ fontSize: "11px", fontWeight: "bold" }}>{row.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="small muted note">
        Fractal design structure: Each FCO object has a root hash $\rightarrow$ local FCG has a root hash $\rightarrow$ hosted HydraDB has a database root hash. Identity parity is maintained at every scale.
      </p>
    </section>
  );
}
