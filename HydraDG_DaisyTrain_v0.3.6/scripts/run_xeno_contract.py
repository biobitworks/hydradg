from pathlib import Path
import argparse, json, hashlib, subprocess, tempfile, os, glob, datetime, shutil

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("--manifest",required=True)
ap.add_argument("--mode",choices=["local"],default="local")
ap.add_argument("--out",required=True)
args=ap.parse_args()

m=json.loads(Path(args.manifest).read_text())
assets={k:Path(v["path"]) for k,v in m["assets"].items()}
for k,v in m["assets"].items():
    if sha(assets[k]) != v["sha256"]:
        raise RuntimeError(f"asset drift before run: {k}")

contract=m["contract"]
with tempfile.TemporaryDirectory(prefix="xeno_replay_") as td:
    work=Path(td)
    repl={
      "{HARNESS}": str(assets["HARNESS"]),
      "{CHECKPOINT}": str(assets["CHECKPOINT"]),
      "{TABLE}": str(assets["TABLE"]),
      "{WORKDIR}": str(work),
      "{OUTPUT_DIR}": str(work/"outputs")
    }
    (work/"outputs").mkdir()
    def subst(s):
        for a,b in repl.items(): s=s.replace(a,b)
        return s
    argv=[subst(str(x)) for x in contract["argv"]]
    cwd=Path(subst(contract.get("cwd","{WORKDIR}")))
    env=os.environ.copy()
    env.update({str(k):subst(str(v)) for k,v in contract.get("environment",{}).items()})
    cp=subprocess.run(argv,cwd=cwd,env=env,text=True,capture_output=True)
    found={}
    for pattern in contract.get("capture_globs",[]):
        for f in work.glob(pattern):
            if f.is_file():
                found[str(f.relative_to(work))]={"sha256":sha(f),"bytes":f.stat().st_size}
    metrics={}
    for raw in contract.get("metric_json_paths",[]):
        p=Path(subst(raw))
        if p.is_file():
            try: metrics[str(raw)]=json.loads(p.read_text())
            except Exception: pass
    receipt={
      "schema":"hydradg.xeno_execution_receipt.v1",
      "mode":"local",
      "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "argv":argv,
      "input_sha256":{k:v["sha256"] for k,v in m["assets"].items()},
      "returncode":cp.returncode,
      "stdout":cp.stdout,
      "stderr":cp.stderr,
      "outputs":found,
      "metrics":metrics,
      "claim_boundary":"Execution receipt; correctness and historical identity are separate."
    }
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"returncode":cp.returncode,"output_files":len(found),"metric_objects":len(metrics)},indent=2))
    if cp.returncode != 0:
        raise SystemExit(cp.returncode)
