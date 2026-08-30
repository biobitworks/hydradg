import Link from "next/link";

import GoldenPathStep from "@/components/GoldenPathStep";

const STATUS = [
  ["Golden Reference → Poison → Antidote walkthrough", "READY", "Product demonstration of governed state transitions."],
  ["Hosted HydraDB connectivity", "PASS", "Database/collection connectivity and request-level canary traceability can be shown when the configured API responds successfully."],
  ["Hosted canonical 653-FCO / 1,692-edge parity", "NOT_ESTABLISHED", "Requires scoped full readback, missing/extra accounting, identity mapping, and root comparison."],
  ["Historical LongMemEval full500 K=5 retrieval ablation", "EXECUTED / PRESERVED", "No positive B/C/D Hit@5 advantage established over the flat route at the tested configuration."],
  ["Expanded local-model matrix", "AUDIT BEFORE PROMOTION", "Only real case-level model responses and measured retrieval outputs may become primary empirical evidence."],
  ["BEAM 1M HydraDG result", "PREPARED_UNEXECUTED", "Architecture and hypotheses are future work until official rows and execution receipts are frozen."],
  ["Multi-agent perturbation + economics", "PREREGISTERED FUTURE WORK", "No accuracy or cost-saving result is claimed yet."],
  ["Signature", "NOT_SIGNED", "SHA-256 identity is not a digital signature."],
  ["Merkle/MMR commitment", "NOT_MERKLE_COMMITTED", "No live commitment claim is made without an actual commitment receipt."],
] as const;

function tone(status: string) {
  if (status === "READY" || status === "PASS" || status.startsWith("EXECUTED")) return { background: "#dcfce7", color: "#166534", border: "#86efac" };
  if (status.includes("NOT_ESTABLISHED") || status.includes("AUDIT") || status.includes("NOT_")) return { background: "#fef3c7", color: "#92400e", border: "#fcd34d" };
  return { background: "#e2e8f0", color: "#334155", border: "#cbd5e1" };
}

export default function EligibilityPage() {
  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem" }}>
      <GoldenPathStep
        step={8}
        summary="End the walkthrough by stating exactly what the evidence supports, what remains pending, and what is future work. This is the final claim ceiling—not a sales summary."
      />

      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#d4af37", fontWeight: 900, fontSize: "0.78rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Step 08 of 08 · Final Claim Boundary
        </p>
        <h1 style={{ fontSize: "clamp(2.2rem, 5vw, 4rem)", lineHeight: 1.02, margin: "0.5rem 0" }}>What HydraDG can—and cannot—claim.</h1>
        <p style={{ maxWidth: "900px", lineHeight: 1.7 }}>
          The submission is fail-closed. Executed, historical, connected, pending, reclassified, and future states remain separate. The final judge takeaway is the governed method: preserve contradictory state, trace provenance, localize divergence, and keep the claim ceiling attached to the evidence.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", marginTop: "1.25rem" }}>
          <Link href="/beam-1m" style={{ padding: "0.65rem 1rem", border: "1px solid rgba(212,175,55,.55)", borderRadius: "999px", textDecoration: "none", color: "#d4af37", fontWeight: 800 }}>← 07 Future Work</Link>
          <Link href="/judge#golden-reference" style={{ padding: "0.65rem 1rem", border: "1px solid #d4af37", borderRadius: "999px", background: "#d4af37", color: "#17130a", textDecoration: "none", fontWeight: 900 }}>Replay from 01 Reference →</Link>
        </div>
      </header>

      <section style={{ marginBottom: "3rem" }}>
        <p style={{ color: "#d4af37", fontWeight: 900, fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>08A / Current evidence state</p>
        <h2 style={{ fontSize: "1.7rem" }}>One line per claim family.</h2>
        <div style={{ display: "grid", gap: "0.75rem", marginTop: "1rem" }}>
          {STATUS.map(([label, state, detail]) => {
            const style = tone(state);
            return (
              <article key={label} style={{ border: "1px solid #e2e8f0", borderRadius: "10px", padding: "1rem", background: "#fff" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", flexWrap: "wrap" }}>
                  <div style={{ flex: "1 1 560px" }}><h3 style={{ margin: "0 0 0.35rem", color: "#0f172a" }}>{label}</h3><p style={{ margin: 0, color: "#475569", lineHeight: 1.55 }}>{detail}</p></div>
                  <span style={{ background: style.background, color: style.color, border: `1px solid ${style.border}`, borderRadius: "999px", padding: "0.35rem 0.65rem", fontWeight: 900, fontSize: "0.72rem", whiteSpace: "nowrap" }}>{state}</span>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section style={{ marginBottom: "3rem", padding: "1.25rem", border: "1px solid rgba(212,175,55,.55)", borderRadius: "10px", background: "#fffbeb" }}>
        <p style={{ color: "#92400e", fontWeight: 900, fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase", marginTop: 0 }}>08B / Judge takeaway</p>
        <h2 style={{ marginTop: 0, color: "#451a03" }}>HydraDG is a governed memory experiment, not a leaderboard claim.</h2>
        <p style={{ color: "#78350f", lineHeight: 1.7, marginBottom: 0 }}>
          Change state, find the first divergence, preserve custody, test recovery, and keep positive, null, negative, failed, timeout, and abstaining evidence in the same graph. Future score or economics claims must inherit the same receipt-first standard.
        </p>
      </section>

      <section style={{ padding: "1.25rem", border: "1px solid #e2e8f0", borderRadius: "10px" }}>
        <p style={{ color: "#d4af37", fontWeight: 900, fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase", marginTop: 0 }}>08C / Finish</p>
        <h2 style={{ marginTop: 0 }}>Golden Path complete.</h2>
        <p style={{ lineHeight: 1.65 }}>The judge has now seen the state transition, HydraDB connectivity boundary, historical result, evidence lineage, future experiment, and final claim ceiling in a single ordered path.</p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem" }}><Link href="/judge#golden-reference" style={{ padding: "0.7rem 1rem", borderRadius: "999px", background: "#d4af37", color: "#17130a", textDecoration: "none", fontWeight: 900 }}>Replay Golden Path</Link><Link href="/" style={{ padding: "0.7rem 1rem", borderRadius: "999px", border: "1px solid currentColor", textDecoration: "none" }}>Return to Overview</Link></div>
      </section>
    </main>
  );
}
