import modal, json, hashlib
from pathlib import Path

app=modal.App("hydradg-eca-extension-v031")
vol=modal.Volume.from_name("hydradg-eca-extension-v031",create_if_missing=True)

# Self-contained source is mounted from the package; no external dataset is required.
image=(modal.Image.debian_slim(python_version="3.13")
       .add_local_file("scripts/eca_core.py","/opt/hydradg/eca_core.py",copy=True))

@app.function(image=image,volumes={"/vol":vol},cpu=1.0,memory=1024,timeout=600)
def execute(full: bool):
    import importlib.util
    spec=importlib.util.spec_from_file_location("eca_core","/opt/hydradg/eca_core.py")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    result=m.generate(full=full)
    name="eca_extension_80.json" if full else "eca_extension_quick.json"
    out=Path("/vol/runs")/name
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    vol.commit()
    return {"volume_path":str(out),"summary":result["summary"],"result_body_sha256":result["result_body_sha256"]}

@app.local_entrypoint()
def main(quick: bool=False):
    print(json.dumps(execute.remote(not quick),indent=2,sort_keys=True))
