#!/usr/bin/env python3
"""Local preflight for SGLang BCG Kaggle stress — fail closed before push."""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
KAGGLE = EXP / "kaggle"
SECRET_PATTERNS = [
    # Literal credential assignments only (not $(...) / json.load loaders).
    re.compile(r"KAGGLE_KEY\s*=\s*['\"][A-Za-z0-9]{20,}['\"]"),
    re.compile(r"api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9]{20,}['\"]", re.I),
    re.compile(r"BEGIN (RSA |OPENSSH )?PRIVATE KEY"),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fail(msg: str) -> None:
    print(f"PREFLIGHT=FAIL reason={msg}")
    raise SystemExit(1)


def main() -> None:
    runner = KAGGLE / "run_sglang_bcg_stress.py"
    meta = KAGGLE / "kernel-metadata.json"
    prereg = KAGGLE / "PREREGISTRATION.json"
    fixtures = KAGGLE / "fixtures.jsonl"
    manifest = KAGGLE / "MANIFEST.json"
    for p in (runner, meta, prereg, fixtures, manifest):
        if not p.exists():
            fail(f"missing {p}")

    # Syntax check runners
    for py in [runner, *EXP.joinpath("scripts").glob("*.py")]:
        if not py.exists():
            continue
        try:
            ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError as e:
            fail(f"syntax {py}: {e}")

    # JSON validate
    for jp in (meta, prereg, manifest):
        json.loads(jp.read_text(encoding="utf-8"))

    rows = [json.loads(l) for l in fixtures.read_text(encoding="utf-8").splitlines() if l.strip()]
    man = json.loads(manifest.read_text(encoding="utf-8"))
    pre = json.loads(prereg.read_text(encoding="utf-8"))

    if sha256(fixtures) != man.get("fixtures_sha256"):
        fail("fixtures hash != MANIFEST.fixtures_sha256")
    if sha256(fixtures) != pre["CORPUS"]["fixtures_sha256"]:
        fail("fixtures hash != PREREGISTRATION")
    if len(rows) != man.get("fixture_rows"):
        fail("fixture row count mismatch")
    if man.get("cells_expected") != len(rows) * 3:
        fail("cells_expected mismatch")

    conds = man.get("conditions") or []
    if len(conds) != 3:
        fail("expected exactly 3 conditions")
    expected = [
        ("C0", "disabled", "full"),
        ("C1", "tc_piecewise", "full"),
        ("C2", "breakable", "full"),
    ]
    for (eid, ep, ed), c in zip(expected, conds):
        if c["condition_id"] != eid or c["prefill_backend"] != ep or c["decode_backend"] != ed:
            fail(f"condition mismatch {c}")

    wids = [r["workload_id"] for r in rows]
    if wids != man.get("workload_ids"):
        fail("workload_id ordering mismatch vs manifest")
    if any(r.get("label") != "SYNTHETIC_ENGINEERING_FIXTURE" for r in rows):
        fail("non-synthetic label present")

    # Secrets scan bounded tree
    for path in EXP.rglob("*"):
        if path.is_dir() or path.suffix in {".pt", ".bin", ".safetensors"}:
            continue
        if ".tools" in path.parts or "results" in path.parts and path.suffix == ".csv":
            pass
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                fail(f"secret-like pattern in {path}")

    # No Daisy write paths / HydraDB write / scientific scorer in runner
    runner_txt = runner.read_text(encoding="utf-8")
    banned_substrings = [
        "hydradb.write",
        "HydraDB(",
        "scientific_scorer",
        "daisy_train",
        "studio_daisy_20260821",
        "eval/studio_daisy",
    ]
    low = runner_txt.lower()
    for b in banned_substrings:
        if b.lower() in low:
            fail(f"banned reference {b} in runner")
    if "hydradb" in low and "not_touched" not in low:
        fail("HydraDB mentioned without NOT_TOUCHED guard")
    # Distinct output dirs by condition
    if "COND_DIR" not in runner_txt and "conditions" not in runner_txt:
        fail("runner missing per-condition output dir")

    km = json.loads(meta.read_text(encoding="utf-8"))
    if km.get("is_private") is not True or km.get("enable_gpu") is not True:
        fail("kernel must be private+gpu")

    print("PREFLIGHT=PASS")
    print(f"FIXTURES_SHA256={sha256(fixtures)}")
    print(f"MANIFEST_SHA256={sha256(manifest)}")
    print(f"CELLS_EXPECTED={man['cells_expected']}")
    print(f"CONDITIONS={','.join(c['condition_id'] for c in conds)}")


if __name__ == "__main__":
    main()
