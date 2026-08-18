from pathlib import Path
import argparse,json
ap=argparse.ArgumentParser(); ap.add_argument("result"); args=ap.parse_args()
x=json.loads(Path(args.result).read_text())
s=x["summary"]
problems=[]
if x["experiment_id"]=="ECA-EXT80" and s["total_trajectories"]!=80: problems.append("expected 80 trajectories")
if s["first_divergence_exact"]!=s["perturbed_trajectories"]: problems.append("first divergence mismatch")
if s["state_exact_recovery"]!=s["oracle_repair_trajectories"]: problems.append("oracle recovery mismatch")
if problems:
    print("FAIL", problems); raise SystemExit(1)
print("PASS", json.dumps(s,sort_keys=True))
