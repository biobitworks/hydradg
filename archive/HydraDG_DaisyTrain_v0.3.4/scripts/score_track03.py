from pathlib import Path
import argparse,json,math

def pct(x):
    return "—" if x is None else f"{100*x:.2f}%"

def wilson(k,n,z=1.959963984540054):
    if not n: return None
    p=k/n; den=1+z*z/n
    ctr=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0,ctr-half),min(1,ctr+half)

ap=argparse.ArgumentParser()
ap.add_argument("results"); ap.add_argument("--out",required=True)
args=ap.parse_args()
x=json.loads(Path(args.results).read_text())
lm=x["longmemeval"]
if lm.get("n")!=500:
    raise SystemExit("LongMemEval final scorecard requires n=500; smoke subsets must not be promoted")

lines=[
 "# HydraDG Hack Hydra Track 03 Scorecard","",
 "## LongMemEval-S full500","",
 f"- N: **{lm['n']}**",
 f"- Overall: **{pct(lm.get('overall'))}**",
 f"- Information Extraction: {pct(lm.get('information_extraction'))}",
 f"- Multi-Session Reasoning: {pct(lm.get('multi_session_reasoning'))}",
 f"- Knowledge Updates: {pct(lm.get('knowledge_updates'))}",
 f"- Temporal Reasoning: {pct(lm.get('temporal_reasoning'))}",
 f"- Abstention: {pct(lm.get('abstention'))}",
 f"- Context tokens mean: {lm.get('context_tokens_mean','—')}",
 f"- Latency p50/p95 ms: {lm.get('latency_p50_ms','—')} / {lm.get('latency_p95_ms','—')}",
 "","## A-D ablations","",
 "| Config | N | Overall | Evidence path coverage | p50 ms | p95 ms | Context tokens |",
 "|---|---:|---:|---:|---:|---:|---:|"
]
for k in "ABCD":
    a=x["ablations"][k]
    lines.append(f"| {k} | {a.get('n','—')} | {pct(a.get('overall'))} | {pct(a.get('evidence_path_coverage'))} | {a.get('latency_p50_ms','—')} | {a.get('latency_p95_ms','—')} | {a.get('context_tokens_mean','—')} |")
if x.get("injected_perturbation"):
    p=x["injected_perturbation"]
    lines += ["","## Separate injected perturbation/recovery suite","",
      f"- N: {p.get('n','—')}",
      f"- First-divergence exact: {pct(p.get('first_divergence_exact'))}",
      f"- Impact precision / recall / F1: {pct(p.get('impact_precision'))} / {pct(p.get('impact_recall'))} / {pct(p.get('impact_f1'))}",
      f"- Impact exact match: {pct(p.get('impact_exact_match'))}",
      f"- Unsupported-claim rejection: {pct(p.get('unsupported_claim_rejection'))}",
      f"- Superseded-history reconstruction: {pct(p.get('history_reconstruction'))}",
      f"- Recovery-class accuracy: {pct(p.get('recovery_class_accuracy'))}"
    ]
lines += ["","## Evidence boundary","",
 "ECA, XenoDisorder, Vithia/Pythia and injected perturbation results are reported separately from the official LongMemEval denominator.",
 "No MMR/signature claim is made by this scorecard."
]
out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
out.write_text("\n".join(lines)+"\n")
print(out)
