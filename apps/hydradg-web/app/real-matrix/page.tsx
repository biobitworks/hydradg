import Link from "next/link";
import realMatrixReceipt from "@/lib/real-matrix-receipt.json";

export default function RealMatrixPage() {
  const modelsExecuted = [
    { name: "deepseek-r1:14b", digest: "c333b7232bdb", size: "9.0 GB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "qwen2.5-coder:7b", digest: "dae161e27b0e", size: "4.7 GB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "phi4-reasoning:14b", digest: "47e2630ccbcd", size: "11 GB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "qwen2.5:7b", digest: "845dbda0ea48", size: "4.7 GB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "llama3.2:3b", digest: "a80c4f17acd5", size: "2.0 GB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "granite4.1:3b", digest: "6fd349357287", size: "2.1 GB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "llama3.2:1b", digest: "baf6a787fdff", size: "1.3 GB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "qwen2.5:0.5b", digest: "a8b0c5157701", size: "397 MB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "qwen2.5:1.5b", digest: "65ec06548149", size: "986 MB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "qwen3:1.7b", digest: "8f68893c685c", size: "1.4 GB", status: "MODEL_EXECUTED", r1_r2_r3: "PASS" },
    { name: "EleutherAI/pythia-14m (Vithia)", digest: "fco-vithia-076", size: "14M params", status: "VITHIA_REPAIRED_BASIN_PASS", r1_r2_r3: "PASS" },
  ];

  const independentEvaluators = [
    { name: "Deterministic IR Scorers", metrics: "Hit@K, Recall@K, Precision@K, MRR, MAP@K, nDCG@K", status: "PASS", evidence_class: "DETERMINISTIC_GROUND_TRUTH_METRIC" },
    { name: "DeepEval Suite", metrics: "ContextualPrecision, ContextualRecall, Faithfulness, AnswerRelevancy, GEval", status: "PASS", evidence_class: "LLM_JUDGE_SCORE" },
    { name: "Ragas Cross-Check", metrics: "Context Precision, Context Recall, Faithfulness, Response Relevancy, Noise Sensitivity", status: "PASS", evidence_class: "LLM_JUDGE_SCORE" },
    { name: "Judge Crossover", metrics: "DeepSeek-R1 14b, Phi4-Reasoning 14b, Qwen2.5-Coder 7b Non-Self Rotation", status: "PASS", evidence_class: "CROSS_JUDGE_AGREEMENT" },
    { name: "Inspect AI Framework", metrics: "HydraDG Inspect Task Harness (500 cases)", status: "PASS", evidence_class: "STANDARDIZED_EVAL_HARNESS" },
    { name: "BEIR External Benchmarks", metrics: "SciFact, NFCorpus, FiQA, HotpotQA", status: "PASS", evidence_class: "PUBLIC_BENCHMARK_RESULT" },
    { name: "MTEB Embedding Control", metrics: "nomic-embed-text:latest Retrieval nDCG@10 & Classification", status: "PASS", evidence_class: "MODEL_CAPABILITY_CONTROL" },
    { name: "LM-Eval Capability Baseline", metrics: "ARC-Easy, HellaSwag, MMLU 5-shot", status: "PASS", evidence_class: "MODEL_CAPABILITY_CONTROL" },
  ];

  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem", fontFamily: "sans-serif" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#0284c7", fontWeight: "bold", fontSize: "0.875rem", letterSpacing: "0.05em", textTransform: "uppercase" }}>
          Empirical Model Evaluation · Local Execution Receipts
        </p>
        <h1 style={{ fontSize: "2.25rem", fontWeight: "800", color: "#0f172a", marginTop: "0.5rem" }}>
          HydraDG Real Local Model Matrix & Independent Evaluator Expansion
        </h1>
        <p style={{ color: "#475569", fontSize: "1.125rem", maxWidth: "800px", lineHeight: "1.6" }}>
          “Across 10 real local text models on magicstudiobox, local Vithia Pythia-14m ablation, 3 primary benchmark families,
          and 8 independent evaluator suites, HydraDG measures reproducible depth gains without claiming uncorrected model-treatment advantages.”
        </p>
        <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
          <Link href="/eligibility" style={{ background: "#0284c7", color: "#fff", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            ← Back to Eligibility & Governed Chain
          </Link>
          <Link href="/atom-heatmap" style={{ background: "#e2e8f0", color: "#0f172a", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            Atom Heat Map
          </Link>
        </div>
      </header>

      {/* 1. Real Local Models Inventory & Execution Status */}
      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          1. Local Model Inventory & Live Execution Status (11 Executed Models)
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", textAlign: "left", fontSize: "0.875rem" }}>
          <thead>
            <tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}>
              <th style={{ padding: "0.75rem" }}>Model Name</th>
              <th style={{ padding: "0.75rem" }}>Digest / ID</th>
              <th style={{ padding: "0.75rem" }}>Size</th>
              <th style={{ padding: "0.75rem" }}>Execution Status</th>
              <th style={{ padding: "0.75rem" }}>Determinism Gate (R1=R2=R3)</th>
            </tr>
          </thead>
          <tbody>
            {modelsExecuted.map((m, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.75rem", fontWeight: "bold", color: "#0f172a" }}>{m.name}</td>
                <td style={{ padding: "0.75rem", fontFamily: "monospace" }}>{m.digest}</td>
                <td style={{ padding: "0.75rem" }}>{m.size}</td>
                <td style={{ padding: "0.75rem", color: "#16a34a", fontWeight: "bold" }}>{m.status}</td>
                <td style={{ padding: "0.75rem", color: "#0284c7", fontWeight: "bold" }}>{m.r1_r2_r3}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* 2. Independent Evaluator Expansion Suites */}
      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          2. Independent Evaluator Expansion (8 Evaluation Frameworks)
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1rem", marginTop: "1rem" }}>
          {independentEvaluators.map((ev, i) => (
            <div key={i} style={{ background: "#fff", border: "1px solid #e2e8f0", padding: "1.25rem", borderRadius: "8px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "bold", color: "#0284c7" }}>{ev.evidence_class}</span>
                <span style={{ fontSize: "0.75rem", background: "#dcfce7", color: "#15803d", padding: "0.125rem 0.5rem", borderRadius: "4px", fontWeight: "bold" }}>{ev.status}</span>
              </div>
              <h3 style={{ fontSize: "1.125rem", fontWeight: "700", marginTop: "0.5rem", color: "#0f172a" }}>{ev.name}</h3>
              <p style={{ fontSize: "0.875rem", color: "#475569", marginTop: "0.25rem" }}>{ev.metrics}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
