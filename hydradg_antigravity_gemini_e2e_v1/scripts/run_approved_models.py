#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, time, urllib.request, urllib.error
from pathlib import Path
from e2e_lib import sha256_bytes, canonical_json_sha

ROOT = Path(__file__).resolve().parents[1]

def http_json(url, payload=None, timeout=180):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def get_models(base):
    obj = http_json(base.rstrip("/") + "/api/tags", timeout=15)
    names = []
    for m in obj.get("models", []):
        name = m.get("name") or m.get("model")
        if name: names.append(name)
    return names, obj

def build_prompt(packet):
    return """You are a bounded HydraDG local diagnostic model.
Return JSON only. Do not claim scientific verification.
Choose a mechanism label, predict the NEXT run direction, cite metric names only,
list counterevidence, specify one falsification test, or abstain.
claim_ceiling MUST equal PROBABILISTIC_MODEL_OUTPUT_ONLY.

FROZEN_PACKET:
""" + json.dumps(packet, sort_keys=True)

def run_one(base, model, packet, schema):
    prompt = build_prompt(packet)
    payload = {
        "model": model,
        "stream": False,
        "messages": [{"role":"user","content":prompt}],
        "format": schema,
        "options": {"temperature": 0}
    }
    raw_payload = json.dumps(payload, sort_keys=True).encode()
    t0 = time.time()
    try:
        out = http_json(base.rstrip("/") + "/api/chat", payload, timeout=300)
        mode = "JSON_SCHEMA"
    except urllib.error.HTTPError as e:
        # Compatibility fallback: still require parsed JSON and record fallback.
        payload["format"] = "json"
        out = http_json(base.rstrip("/") + "/api/chat", payload, timeout=300)
        mode = f"JSON_FALLBACK_AFTER_HTTP_{e.code}"
    elapsed = time.time() - t0
    content = out.get("message", {}).get("content", "")
    parsed = json.loads(content)
    required = {
        "mechanism_label","expected_direction_next_run","supporting_metrics",
        "counterevidence","next_falsification_test","abstain","claim_ceiling"
    }
    missing = required - set(parsed)
    if missing:
        raise ValueError(f"missing keys: {sorted(missing)}")
    if parsed["claim_ceiling"] != "PROBABILISTIC_MODEL_OUTPUT_ONLY":
        raise ValueError("claim ceiling mismatch")
    return {
        "model": model,
        "mode": mode,
        "prompt_sha256": sha256_bytes(prompt.encode()),
        "request_sha256": sha256_bytes(raw_payload),
        "raw_response_sha256": sha256_bytes(json.dumps(out, sort_keys=True).encode()),
        "parsed_response_sha256": canonical_json_sha(parsed),
        "parsed": parsed,
        "elapsed_seconds": elapsed,
        "ollama_metrics": {
            k: out.get(k) for k in [
                "total_duration","load_duration","prompt_eval_count","prompt_eval_duration",
                "eval_count","eval_duration"
            ] if k in out
        }
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.getenv("OLLARMA_BASE_URL","http://127.0.0.1:11434"))
    ap.add_argument("--packet", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    config = json.loads((ROOT/"configs/approved_models.json").read_text())
    schema = json.loads((ROOT/"schemas/ollarma_prediction.schema.json").read_text())
    packet = json.loads(Path(args.packet).read_text())
    installed, tags = get_models(args.base_url)
    result = {
        "schema":"hydradg.approved_model_replay.v1",
        "base_url":args.base_url,
        "installed_models":installed,
        "models":{},
        "claim_ceiling":"MODEL_REPLAY_STABILITY_ONLY"
    }
    for item in config["approved"]:
        model = item["model"]
        if model not in installed:
            raise SystemExit(f"BLOCKED_APPROVED_MODEL_MISSING {model}")
        reps = [run_one(args.base_url, model, packet, schema) for _ in range(item["repeats"])]
        labels = [r["parsed"]["mechanism_label"] for r in reps]
        result["models"][item["id"]] = {
            "model":model,
            "repeats":reps,
            "mechanism_labels":labels,
            "exact_label_stability":len(set(labels)) == 1
        }
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(f"STATE=PASS STAGE=APPROVED_MODEL_REPLAY OUTPUT={args.out}")
if __name__ == "__main__":
    main()
