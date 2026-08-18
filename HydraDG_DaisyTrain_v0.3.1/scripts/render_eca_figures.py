from pathlib import Path
import argparse,json
ap=argparse.ArgumentParser(); ap.add_argument("result"); ap.add_argument("--outdir",required=True); args=ap.parse_args()
try:
    import matplotlib.pyplot as plt
except ImportError:
    raise SystemExit("matplotlib is required locally: python -m pip install matplotlib")
x=json.loads(Path(args.result).read_text())
out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)

# Figure 1: mean Hamming/blast-radius trajectories by rule and condition.
rules=sorted(set(r["rule"] for r in x["trajectories"]))
conditions=["cell_tamper","rule_drift","oracle_repair"]
for rule in rules:
    plt.figure(figsize=(8,4.5))
    for cond in conditions:
        rows=[r for r in x["trajectories"] if r["rule"]==rule and r["condition"]==cond]
        if not rows: continue
        n=len(rows); T=len(rows[0]["hamming_by_step"])
        mean=[sum(r["hamming_by_step"][t] for r in rows)/n for t in range(T)]
        plt.plot(range(T),mean,label=cond)
    plt.xlabel("time step"); plt.ylabel("mean cells different from reference")
    plt.title(f"ECA Rule {rule}: perturbation propagation")
    plt.legend(); plt.tight_layout()
    plt.savefig(out/f"eca_rule_{rule}_impact.png",dpi=180); plt.close()

# Figure 2: summary bars.
s=x["summary"]
plt.figure(figsize=(7,4))
labels=["first-divergence exact","oracle state-exact recovery"]
vals=[
    s["first_divergence_exact"]/max(1,s["perturbed_trajectories"]),
    s["state_exact_recovery"]/max(1,s["oracle_repair_trajectories"])
]
plt.bar(labels,vals)
plt.ylim(0,1.05); plt.ylabel("fraction"); plt.title(x["experiment_id"])
plt.tight_layout(); plt.savefig(out/"eca_extension_summary.png",dpi=180); plt.close()
print(f"wrote figures to {out}")
