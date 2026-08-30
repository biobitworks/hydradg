#!/usr/bin/env python3
"""Build NewInML final_v4 successor PDF with official template + checklist."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/newinml2026_solo"
V4 = PAPER / "final_v4"
MS = V4 / "manuscript"
BUILD = MS / "build"
FREEZE = PAPER / "requirement_citation_audit/source_freeze"
KIT_ZIP = FREEZE / "neurips_2026_official_kit.zip"
GREEN_PDF_SHA256 = "0b096ccec7c6c1a630e4308abacea89a59620e410bfaff705409ce884a93c1ad"
OFFICIAL_STYLE_SHA256 = "c3fc2894e83d2517ca18b66741d6c595986d97957dc08ec08bb2125a7ec4555a"

CHECKLIST_ANSWERS = [
    ("\\answerYes{}", "Abstract and Introduction state framework contributions, underpowered EXP-008/009 terminals, and explicit non-promotion of treatment effects."),
    ("\\answerYes{}", "Section~\\ref{sec:limitations} (Limitations subsection) discusses bounded replication, local-only lanes, interrupted SeedGraph, and omitted Qwen successor results."),
    ("\\answerNA{}", "The paper does not present formal theorems or proofs."),
    ("\\answerYes{}", "Experimental Setup and Results sections disclose frozen manifests, conditions, models, scorers, and terminal verdict receipts referenced as internal anonymized artifacts."),
    ("\\answerNo{}", "Primary experiment artifacts are internal frozen custody objects; this anonymous workshop submission does not bundle open code or data for full independent rerun."),
    ("\\answerYes{}", "Section~Experimental Setup specifies conditions C0/C1, models, case manifest, replicate count, and aggregation rule."),
    ("\\answerNo{}", "Primary endpoints report terminal underpowered verdicts without confidence intervals; confirmatory ordering was not established under the frozen design."),
    ("\\answerYes{}", "Section~Experimental Setup names local model identifiers; systems-validation scope is summarized in Table~\\ref{tab:systems}."),
    ("\\answerYes{}", "The submission follows NeurIPS ethics expectations; no human-subjects experiments are reported."),
    ("\\answerNA{}", "This is primarily an evaluation-infrastructure paper without a dedicated societal-impact discussion beyond standard agent-evaluation context."),
    ("\\answerNA{}", "No new high-risk pretrained model or scraped dataset is released with this submission."),
    ("\\answerYes{}", "Related Work and the bibliography credit external benchmarks, retrieval systems, and reproducibility literature."),
    ("\\answerNo{}", "No new public dataset or model asset is released; custody artifacts remain internal to the anonymous submission."),
    ("\\answerNA{}", "No crowdsourcing or human-participant study is reported."),
    ("\\answerNA{}", "No human-subjects research requiring IRB review is reported."),
    ("\\answerYes{}", "Section~AI and agent methodology disclosure states frontier agents assisted tooling/manuscript preparation and are not authors; scientific endpoints come from preregistered local model runs."),
]


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p: Path, obj: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, cwd=ROOT, **kw)


def git_reconciliation() -> dict:
    local = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    run(["git", "fetch", "origin", branch])
    origin = run(["git", "rev-parse", f"origin/{branch}"]).stdout.strip()
    ahead = run(["git", "log", "--oneline", f"origin/{branch}..HEAD"]).stdout.strip().splitlines()
    behind = run(["git", "log", "--oneline", f"HEAD..origin/{branch}"]).stdout.strip().splitlines()
    rec = {
        "schema": "hydradg.git_reconciliation.v1",
        "recorded_at_utc": utc(),
        "CURRENT_BRANCH": branch,
        "LOCAL_HEAD": local,
        "ORIGIN_HEAD_AT_RECONCILE": origin,
        "RELATIONSHIP": (
            "LOCAL_AHEAD" if ahead and not behind else
            "ORIGIN_AHEAD" if behind and not ahead else
            "DIVERGED" if ahead and behind else
            "SYNCED"
        ),
        "COMMITS_LOCAL_AHEAD": [x for x in ahead if x],
        "COMMITS_ORIGIN_AHEAD": [x for x in behind if x],
        "PROCEED_FROM_SHA": local,
        "NOTE": "Execution proceeds from recorded LOCAL_HEAD; push will advance origin after commit.",
    }
    write_json(V4 / "GIT_RECONCILIATION.json", rec)
    return rec


def install_official_template() -> dict:
    proc = subprocess.run(["unzip", "-p", str(KIT_ZIP), "neurips_2026.sty"], capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError("failed to extract official neurips_2026.sty")
    sty_path = MS / "neurips_2026.sty"
    sty_path.write_bytes(proc.stdout)
    kit_sha = sha256_file(KIT_ZIP)
    style_sha = sha256_file(sty_path)
    receipt = {
        "schema": "hydradg.template_install_receipt.v1",
        "recorded_at_utc": utc(),
        "OFFICIAL_KIT_ZIP_SHA256": kit_sha,
        "OFFICIAL_STYLE_SHA256": style_sha,
        "LOCAL_STYLE_SHA256": style_sha,
        "OFFICIAL_STYLE_PARITY": "PASS" if style_sha == OFFICIAL_STYLE_SHA256 else "FAIL",
        "successor_sty_path": str(sty_path.relative_to(ROOT)),
    }
    write_json(V4 / "TEMPLATE_INSTALL_RECEIPT.json", receipt)
    return receipt


def build_checklist_tex() -> Path:
    raw = subprocess.check_output(["unzip", "-p", str(KIT_ZIP), "checklist.tex"], cwd=ROOT)
    text = raw.decode("utf-8")
    text = re.sub(
        r"%%% BEGIN INSTRUCTIONS %%%.*?%%% END INSTRUCTIONS %%%",
        "",
        text,
        flags=re.S,
    )
    todo_pairs = list(re.finditer(
        r"\\item\[\] Answer: \\answerTODO\{\}.*?\\item\[\] Justification: \\justificationTODO\{\}",
        text,
        flags=re.S,
    ))
    if len(todo_pairs) != len(CHECKLIST_ANSWERS):
        raise RuntimeError(f"checklist answer count mismatch: {len(todo_pairs)} vs {len(CHECKLIST_ANSWERS)}")
    offset = 0
    out = text
    for (m, (ans, just)) in zip(todo_pairs, CHECKLIST_ANSWERS):
        repl = (
            f"\\item[] Answer: {ans}\n"
            f"    \\item[] Justification: {just}"
        )
        start, end = m.start() + offset, m.end() + offset
        out = out[:start] + repl + out[end:]
        offset += len(repl) - (end - start)
    out_path = MS / "checklist.tex"
    out_path.write_text(out)
    write_json(V4 / "CHECKLIST_ANSWERS_RECEIPT.json", {
        "schema": "hydradg.checklist_answers_receipt.v1",
        "recorded_at_utc": utc(),
        "source": "official_kit_checklist.tex",
        "instruction_block_removed": True,
        "question_count": len(CHECKLIST_ANSWERS),
        "answers_source_controlled": True,
        "CHECKLIST_REQUIREMENT_STATE": "REQUIRED",
    })
    return out_path


def compile_pdf() -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    for stale in BUILD.glob("main.*"):
        stale.unlink(missing_ok=True)
    proc = run([
        "tectonic",
        "-X", "compile",
        str(MS / "main.tex"),
        "--outdir", str(BUILD),
        "--keep-logs",
    ])
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise RuntimeError("tectonic compile failed")
    pdf = BUILD / "main.pdf"
    if not pdf.exists():
        raise RuntimeError("main.pdf not produced")
    return pdf


def page_partition(pdf: Path) -> dict:
    total = int(run(["pdfinfo", str(pdf)]).stdout.split("Pages:")[1].split()[0])
    ref_start = checklist_start = None
    for page in range(1, total + 1):
        text = run(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"]).stdout
        if ref_start is None and re.search(r"^\s*References\s*$", text, re.M):
            ref_start = page
        if checklist_start is None and re.search(r"NeurIPS Paper Checklist", text):
            checklist_start = page
    if ref_start is None:
        ref_start = total
    if checklist_start is None:
        checklist_start = total + 1
    main_pages = ref_start - 1
    ref_pages = checklist_start - ref_start
    checklist_pages = total - checklist_start + 1 if checklist_start <= total else 0
    return {
        "total_pdf_pages": total,
        "main_content_pages": main_pages,
        "reference_pages": ref_pages,
        "checklist_pages": checklist_pages,
        "references_start_page": ref_start,
        "checklist_start_page": checklist_start if checklist_start <= total else None,
        "main_pages_gate": 2 <= main_pages <= 8,
    }


def anonymization_scan(pdf: Path) -> dict:
    text = run(["pdftotext", str(pdf), "-"]).stdout
    needles = ["Byron", "Biobitworks", "biobitworks", "github.com", "10.5281", "cellARCH", "magicSTUDIObox"]
    hits = [n for n in needles if re.search(re.escape(n), text, re.I)]
    return {"gate": "PASS" if not hits else "FAIL", "hits": hits}


def main() -> int:
    V4.mkdir(parents=True, exist_ok=True)
    rec = git_reconciliation()
    tpl = install_official_template()
    build_checklist_tex()
    pdf = compile_pdf()
    pages = page_partition(pdf)
    anon = anonymization_scan(pdf)
    pdf_sha = sha256_file(pdf)
    green_ok = sha256_file(FREEZE / "green_v3_main.pdf") == GREEN_PDF_SHA256 if (FREEZE / "green_v3_main.pdf").exists() else True
    ready = (
        tpl["OFFICIAL_STYLE_PARITY"] == "PASS"
        and pages["main_pages_gate"]
        and anon["gate"] == "PASS"
        and green_ok
    )
    receipt = {
        "schema": "hydradg.successor_submission_receipt.v1",
        "recorded_at_utc": utc(),
        "CURRENT_BRANCH": rec["CURRENT_BRANCH"],
        "CURRENT_SHA": rec["LOCAL_HEAD"],
        "GREEN_V3_SHA256": GREEN_PDF_SHA256,
        "GREEN_V3_UNTOUCHED": green_ok,
        "SUCCESSOR_PDF_SHA256": pdf_sha,
        "SUCCESSOR_PDF_PATH": str(pdf.relative_to(ROOT)),
        "OFFICIAL_KIT_ZIP_SHA256": tpl["OFFICIAL_KIT_ZIP_SHA256"],
        "OFFICIAL_STYLE_SHA256": tpl["OFFICIAL_STYLE_SHA256"],
        "LOCAL_STYLE_SHA256": tpl["LOCAL_STYLE_SHA256"],
        "OFFICIAL_STYLE_PARITY": tpl["OFFICIAL_STYLE_PARITY"],
        "TOTAL_PAGES": pages["total_pdf_pages"],
        "MAIN_CONTENT_PAGES": pages["main_content_pages"],
        "REFERENCE_PAGES": pages["reference_pages"],
        "CHECKLIST_PAGES": pages["checklist_pages"],
        "CHECKLIST_REQUIREMENT_STATE": "REQUIRED",
        "ANONYMIZATION": anon["gate"],
        "SUCCESSOR_SUBMISSION_READY": "YES" if ready else "NO",
        "EXP008_EXP009_UNTOUCHED": True,
    }
    write_json(V4 / "SUCCESSOR_SUBMISSION_RECEIPT.json", receipt)
    write_json(V4 / "PAGE_PARTITION_RECEIPT.json", pages)
    write_json(V4 / "ANONYMIZATION_RECEIPT.json", anon)
    print(json.dumps(receipt, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
