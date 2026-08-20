"""XenoDisorder CAFA6 frozen-assets replay — Modal-stable launcher.

v0.3.2 disables automatic source inclusion and serializes the remote function so
the local launcher file cannot be invalidated by a live project watcher during build.
"""
from __future__ import annotations
import json
import modal

app = modal.App("hydradg-xenodisorder-cafa6-v032", include_source=False)
inputs = modal.Volume.from_name("hydradg-xeno-cafa6-input-v032", create_if_missing=False)
outputs = modal.Volume.from_name("hydradg-xeno-cafa6-output-v032", create_if_missing=True)
image = modal.Image.debian_slim(python_version="3.13")

@app.function(
    image=image,
    volumes={"/inputs":inputs,"/outputs":outputs},
    cpu=2.0,
    memory=8192,
    timeout=7200,
    include_source=False,
    serialized=True,
)
def replay():
    import hashlib, json, os, subprocess, tempfile
    from pathlib import Path

    def sha(p):
        h=hashlib.sha256()
        with Path(p).open("rb") as f:
            for b in iter(lambda:f.read(8*1024*1024),b""):
                h.update(b)
        return h.hexdigest()

    harness=Path("/inputs/cafa6_governed_eval.py")
    checkpoint=Path("/inputs/ckpt_latest.pt")
    table=Path("/inputs/residual_table.jsonl")
    contract_path=Path("/inputs/run_contract.json")
    for p in [harness,checkpoint,table,contract_path]:
        if not p.is_file():
            raise FileNotFoundError(str(p))

    contract=json.loads(contract_path.read_text())
    if any("REPLACE_WITH" in str(x) for x in contract.get("argv",[])):
        raise RuntimeError("run contract is still a template")

    with tempfile.TemporaryDirectory(prefix="xeno_modal_") as td:
        work=Path(td)
        (work/"outputs").mkdir()
        repl={
            "{HARNESS}":str(harness),
            "{CHECKPOINT}":str(checkpoint),
            "{TABLE}":str(table),
            "{WORKDIR}":str(work),
            "{OUTPUT_DIR}":str(work/"outputs"),
        }
        def subst(s):
            for a,b in repl.items():
                s=s.replace(a,b)
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
                try:
                    metrics[str(raw)]=json.loads(p.read_text())
                except Exception:
                    pass

        receipt={
            "schema":"hydradg.xeno_execution_receipt.v1",
            "mode":"modal",
            "argv":argv,
            "input_sha256":{
                "HARNESS":sha(harness),
                "CHECKPOINT":sha(checkpoint),
                "TABLE":sha(table),
                "CONTRACT":sha(contract_path),
            },
            "returncode":cp.returncode,
            "stdout":cp.stdout,
            "stderr":cp.stderr,
            "outputs":found,
            "metrics":metrics,
            "claim_boundary":"Execution receipt; correctness and historical identity are separate.",
        }
        out=Path("/outputs/run/xeno_modal_receipt.json")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        outputs.commit()
        if cp.returncode!=0:
            raise RuntimeError(f"evaluator exited {cp.returncode}")
        return {"receipt":str(out),"output_files":len(found),"metric_objects":len(metrics)}

@app.local_entrypoint()
def main():
    print(json.dumps(replay.remote(),indent=2,sort_keys=True))
