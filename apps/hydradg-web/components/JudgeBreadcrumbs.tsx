"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LABELS: Record<string, string> = {
  "/": "Overview",
  "/judge": "Judge walkthrough",
  "/track-fit": "Why Graph? · Track fit + math",
  "/track01": "Track 01",
  "/track02": "Track 02",
  "/track03": "Track 03",
  "/results/context-vs-entropy": "Context vs Entropy",
  "/graph": "4D FCG",
  "/knowledge": "Knowledge Base",
  "/how-to": "How to Use",
  "/evidence": "Evidence",
  "/evolution": "Evolution",
  "/eligibility": "Eligibility",
  "/demo": "Demo",
};

const LOOK_FOR: Record<string, string> = {
  "/": "Start with the context change, then follow highlighted terms into definitions, graph meaning, calculations, and custody evidence.",
  "/judge": "Check Reference → Poison → Antidote calculations and verify that restoration preserves the historical perturbation path.",
  "/track-fit": "Look for four signals: graph data model, retrieval/reasoning, relationship traversal/context, and why flattening to vector or relational lookup loses the chain.",
  "/track01": "Look for identity resolution, conflicting/current claims, provenance, and ontology edges that preserve why two records resolve together or apart.",
  "/track02": "Look for reverse dependency traversal, exact exposure paths, partial repair versus full repair, and independent set-equality checks.",
  "/track03": "Look for temporal state, supersession, contradiction, provenance, and the preserved null/negative retrieval result.",
  "/results/context-vs-entropy": "Look for raw counts, classification coverage, abstentions, and the separation between lexical detection and graph context.",
  "/graph": "Click a node: its state calculations, classification-colored values, FCO identity, relations, and Anticube consideration should be visible together.",
  "/knowledge": "Click a term to resolve definition → Knowledge FCO → graph query → upstream source or receipt.",
  "/how-to": "Follow the numbered path from visible context change to exact FCO identity, evidence, calculations, and release state.",
  "/evolution": "Compare historical presentation/release states without deleting superseded custody evidence.",
  "/eligibility": "Separate custody-supported evidence from human-only attestations; hashes support lineage, not intent.",
};

function labelFor(pathname: string) {
  if (LABELS[pathname]) return LABELS[pathname];
  if (pathname.startsWith("/fco/")) return "FCO inspector";
  return pathname.split("/").filter(Boolean).at(-1)?.replaceAll("-", " ") || "Page";
}

export default function JudgeBreadcrumbs() {
  const pathname = usePathname();
  const current = labelFor(pathname);
  const summary = LOOK_FOR[pathname] || "Use highlighted links to resolve claims and terminology into the How-To, Knowledge Base, terminology matrix, graph, or evidence route.";

  return (
    <aside aria-label="Judge breadcrumbs and page guidance" style={{ maxWidth: 1240, margin: "0 auto", padding: "12px 24px 4px" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8, fontSize: 13, marginBottom: 8 }}>
        <Link href="/">HydraDG</Link>
        <span aria-hidden="true">›</span>
        <strong>{current}</strong>
        <span style={{ opacity: 0.45 }}>·</span>
        <Link href="/how-to" style={{ padding: "3px 7px", borderRadius: 999, background: "rgba(90,169,255,0.12)" }}>How-To</Link>
        <Link href="/knowledge" style={{ padding: "3px 7px", borderRadius: 999, background: "rgba(182,156,255,0.12)" }}>Terminology matrix</Link>
        <Link href="/track-fit" style={{ padding: "3px 7px", borderRadius: 999, background: "rgba(246,200,95,0.14)" }}>Why Graph? + math</Link>
      </div>
      <div style={{ borderLeft: "3px solid rgba(246,200,95,0.9)", background: "rgba(246,200,95,0.07)", borderRadius: 8, padding: "8px 12px", fontSize: 13 }}>
        <strong style={{ marginRight: 6 }}>What to look for:</strong>{summary}
      </div>
    </aside>
  );
}
