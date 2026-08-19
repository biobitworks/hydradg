#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, sys

MODELS=["qwen2.5-coder:7b","qwen2.5:7b"]
class H(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def _send(self,obj,code=200):
        raw=json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/api/tags":
            return self._send({"models":[{"name":m,"model":m} for m in MODELS]})
        if self.path=="/health":
            return self._send({"status":"ok"})
        if self.path=="/api/iceberg/headline":
            return self._send({"delta_G_star":"-0.05","cloud_drift":"0 / 100","accuracy_delta":"+2.6%","recall_delta":"+7.7%"})
        if self.path=="/api/iceberg/full":
            return self._send({"js_divergence":0.0,"cloud_drift_0_100":0.0,"delta_g_star":-0.0547})
        if self.path=="/api/models/comparison":
            return self._send({"exact_agreement":1.0,"prospective_state":"PENDING_HELD_OUT_RUN_N_PLUS_1"})
        return self._send({"error":"not found"},404)
    def do_POST(self):
        if self.path!="/api/chat": return self._send({"error":"not found"},404)
        n=int(self.headers.get("Content-Length","0")); req=json.loads(self.rfile.read(n) or b"{}")
        model=req.get("model","")
        content={
            "mechanism_label":"DEPTH_RECOVERY",
            "expected_direction_next_run":{
                "delta_g_star":"DOWN","retrieval_cloud_drift":"UP","hit_at_k":"UP","recall_at_k":"UP"
            },
            "supporting_metrics":["delta_recall_at_k","delta_hit_at_k"],
            "counterevidence":["structural_cloud_drift"],
            "next_falsification_test":"Freeze K15 preregistration and compare prospective prediction to held-out result.",
            "abstain":False,
            "probabilities":{"recall_up":0.6,"recall_stable":0.25,"recall_down":0.15},
            "claim_ceiling":"PROBABILISTIC_MODEL_OUTPUT_ONLY"
        }
        self._send({
            "model":model,
            "message":{"role":"assistant","content":json.dumps(content)},
            "prompt_eval_count":100,"prompt_eval_duration":1000000,
            "eval_count":50,"eval_duration":5000000,"total_duration":7000000
        })
if __name__=="__main__":
    port=int(sys.argv[1]) if len(sys.argv)>1 else 18434
    HTTPServer(("127.0.0.1",port),H).serve_forever()
