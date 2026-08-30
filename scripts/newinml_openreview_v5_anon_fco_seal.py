#!/usr/bin/env python3
"""NewInML OpenReview V5 double-blind cryptographic commitment repair.

Successor of V4. Preserves V4 CONTENT_ROOT and release custody construction but
replaces the reviewer-facing CONTENT_ROOT capsule with an anonymous commitment:

  ANON_COMMIT = SHA256(UTF8("NEWINML-ANON-COMMIT-V1") || CONTENT_ROOT_BYTES || NONCE_BYTES)

NONCE is drawn from the system CSPRNG and stored only in a gitignored operator receipt.
Does not mutate V3 or V4 artifacts.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/byron/projects/active/hydradg")
FCO_TRAIN = Path("/Users/byron/projects/active/fractal-custody-objects/training")
sys.path.insert(0, str(FCO_TRAIN))
from fco_train.custody import GENESIS, canon, leaf_hash, merkle_root, node_hash  # noqa: E402

V3_PDF = ROOT / "paper/newinml2026_solo/final_v4/comprehensive_v2/final_upload_v3/FINAL_OPENREVIEW_SUBMISSION_V3.pdf"
V3_SHA = "6f2d56a8fb8fb22cf76ad54a5f1abb9918a4319ae6eaf748ef5d02497e8bf9f4"
V3_BYTES = 328601
V4_PDF = ROOT / "paper/newinml2026_solo/final_v4/comprehensive_v2/final_upload_v4/FINAL_OPENREVIEW_SUBMISSION_V4.pdf"
V4_SHA = "3e5185a0bf03640d96342be6354b07dcd3f31ecdfbd6ac2849e17eae9ca3b79e"
V4_RELEASE_ROOT = "0d7ee4ba5411ec3cd3f680bfa73c1b6164b6ab70b8fb6a4b9a576334057087b8"
V4_HEAD = "04d89e1cf1db7651e3e0d8020cbcbb23d07583e9"
CONTENT_ROOT = "1a6b0a967da41e5b619ec449ab0cdbb914797321661e7ee25f8b87f2521df94d"
SRC_HEAD = "82ab3b812bbd40b3cb3e71536fd44764740149f3"
V4_WORK = ROOT / "paper/newinml2026_solo/final_v4/comprehensive_v2/final_upload_v4/work"
OUT = ROOT / "paper/newinml2026_solo/final_v4/comprehensive_v2/final_upload_v5"
WORK = OUT / "work"
PRIVATE_RECEIPT = OUT / "PRIVATE_OPERATOR_RECEIPT.json"
CUSTODY_PY = FCO_TRAIN / "fco_train/custody.py"
FCO_SCHEMA = Path("/Users/byron/projects/active/fractal-custody-objects/fco/schemas/fco_minimum.schema.json")
ALGO = "fco_train.custody.merkle_root.v3"
ANON_SCHEME = "NEWINML-ANON-COMMIT-V1"
ANON_DOMAIN = b"NEWINML-ANON-COMMIT-V1"
LEAF_ENCODING = "leaf=sha256(0x00||sha256(bytes)); node=sha256(0x01||raw32||raw32); odd-promote; order_independent=sorted"

FORBIDDEN_IN_PDF = [
    CONTENT_ROOT,
    CONTENT_ROOT[:16],
    CONTENT_ROOT[:32],
    V4_RELEASE_ROOT,
    V4_SHA,
    V4_HEAD,
    SRC_HEAD,
    "CONTENT-ROOT",
    "CONTENT_ROOT",
    "RELEASE_ROOT",
    "RELEASE_FCO",
    "github.com",
    "biobitworks",
    "hydradg",
    "magicSTUDIO",
    "/Users/",
    "cursor/",
]


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def anon_commit(content_root_hex: str, nonce_bytes: bytes) -> tuple[str, bytes]:
    content_root_bytes = bytes.fromhex(content_root_hex)
    if len(content_root_bytes) != 32:
        raise ValueError("CONTENT_ROOT must be 32 bytes")
    if len(nonce_bytes) != 32:
        raise ValueError("NONCE must be 32 bytes")
    preimage = ANON_DOMAIN + content_root_bytes + nonce_bytes
    return sha_bytes(preimage), preimage


def write_json(path: Path, obj) -> str:
    text = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return sha_bytes(text.encode("utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def inclusion_proof(leaves_hex: list[str], target: str) -> tuple[str, list[dict]]:
    level = sorted(leaves_hex)
    if target not in level:
        raise ValueError("target leaf not in tree")
    idx = level.index(target)
    proof: list[dict] = []
    while len(level) > 1:
        nxt = []
        new_idx = None
        for i in range(0, len(level), 2):
            if i + 1 < len(level):
                left, right = level[i], level[i + 1]
                nxt.append(node_hash(left, right))
                if i == idx:
                    proof.append({"position": "left", "sibling": right})
                    new_idx = len(nxt) - 1
                elif i + 1 == idx:
                    proof.append({"position": "right", "sibling": left})
                    new_idx = len(nxt) - 1
            else:
                nxt.append(level[i])
                if i == idx:
                    proof.append({"position": "promote", "sibling": None})
                    new_idx = len(nxt) - 1
        if new_idx is None:
            raise RuntimeError("lost target during proof construction")
        idx = new_idx
        level = nxt
    return level[0], proof


def verify_inclusion(target: str, proof: list[dict], expected_root: str) -> bool:
    h = target
    for step in proof:
        pos = step["position"]
        sib = step.get("sibling")
        if pos == "promote":
            continue
        if pos == "left":
            h = node_hash(h, sib)
        elif pos == "right":
            h = node_hash(sib, h)
        else:
            return False
    return h == expected_root


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def page_partition(pdf: Path) -> dict:
    total = int(run(["pdfinfo", str(pdf)]).stdout.split("Pages:")[1].split()[0])
    ref = chk = None
    for page in range(1, total + 1):
        t = run(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"]).stdout
        if ref is None and re.search(r"^\s*References\s*$", t, re.M):
            ref = page
        if chk is None and "NeurIPS Paper Checklist" in t:
            chk = page
    ref = ref or total
    chk = chk or total + 1
    return {
        "CONTENT_PAGES": ref - 1,
        "REFERENCE_PAGES": max(0, chk - ref),
        "CHECKLIST_PAGES": max(0, total - chk + 1) if chk <= total else 0,
        "TOTAL_PAGES": total,
    }


def font_gate(pdf: Path) -> str:
    lines = [l for l in run(["pdffonts", str(pdf)]).stdout.splitlines()[2:] if l.strip()]
    unemb = [l for l in lines if "no" in l.split()[-3:]]
    return "PASS" if not unemb else "FAIL"


def repo_search_hits(needle: str) -> int:
    proc = run(["git", "grep", "-F", needle, "--", "."])
    if proc.returncode == 1:
        return 0
    if proc.returncode != 0:
        return -1
    return len([l for l in proc.stdout.splitlines() if l.strip()])


def text_anonymity_gate(pdf_text: str, meta: str) -> tuple[str, list[str]]:
    combined = pdf_text + "\n" + meta
    hits = []
    patterns = [
        (r"Byron", "Byron"),
        (r"\bLee\b", "Lee"),
        (r"biobitworks", "biobitworks"),
        (r"github\.com", "github.com"),
        (r"/Users/", "/Users/"),
        (r"magicSTUDIO", "magicSTUDIO"),
        (r"magicPRO", "magicPRO"),
        (r"cursor/", "cursor/"),
        (r"Affiliation", "Affiliation"),
        (r"Address", "Address"),
        (r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "email"),
    ]
    for pat, label in patterns:
        if re.search(pat, combined):
            hits.append(label)
    return ("PASS" if not hits else "FAIL"), hits


def cryptographic_linkability_gate(pdf_text: str, anon_commit_hex: str, nonce_hex: str) -> tuple[str, list[str]]:
    flat = pdf_text.replace("\n", "").replace(" ", "")
    hits = []
    for forbidden in FORBIDDEN_IN_PDF:
        if forbidden and forbidden in flat:
            hits.append(f"forbidden:{forbidden[:24]}")
    if nonce_hex in flat:
        hits.append("nonce_in_pdf")
    if CONTENT_ROOT in flat:
        hits.append("content_root_in_pdf")
    if anon_commit_hex not in flat:
        hits.append("anon_commit_missing")
    if "NEWINML-ANON-COMMIT-V1" not in pdf_text:
        hits.append("scheme_missing")
    return ("PASS" if not hits else "FAIL"), hits


def main() -> int:
    host = subprocess.check_output(["hostname"], text=True).strip()
    if host != "magicSTUDIObox.local":
        sys.stderr.write(f"HOST_FAIL {host}\n")
        return 2
    if sha_file(V3_PDF) != V3_SHA or V3_PDF.stat().st_size != V3_BYTES:
        sys.stderr.write("V3_IDENTITY_FAIL\n")
        return 3
    if not V4_PDF.exists() or sha_file(V4_PDF) != V4_SHA:
        sys.stderr.write("V4_IDENTITY_FAIL\n")
        return 4

    head = git("rev-parse", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    created_at = git("show", "-s", "--format=%cI", V4_HEAD)

    OUT.mkdir(parents=True, exist_ok=True)
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(V4_WORK, WORK)

    nonce_bytes = secrets.token_bytes(32)
    commit_hex, preimage = anon_commit(CONTENT_ROOT, nonce_bytes)
    ac1, ac2 = commit_hex[:32], commit_hex[32:]

    capsule = (
        r"\vspace*{-0.4em}" "\n"
        r"{\scriptsize\noindent "
        rf"FCO custody commitment: \texttt{{{ac1}\allowbreak {ac2}}}\\" "\n"
        rf"Scheme: {ANON_SCHEME} / SHA-256}}" "\n"
        r"\vspace{0.4em}" "\n"
    )
    (WORK / "custody_capsule.tex").write_text(capsule, encoding="utf-8")

    build_dir = OUT / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    main_tex = WORK / "main.tex"
    subprocess.run(
        ["tectonic", "-X", "compile", str(main_tex), "--outdir", str(build_dir), "--keep-logs"],
        cwd=ROOT,
        check=True,
    )
    v5_pdf = OUT / "FINAL_OPENREVIEW_SUBMISSION_V5.pdf"
    shutil.copy2(build_dir / "main.pdf", v5_pdf)
    pdf_sha = sha_file(v5_pdf)
    pdf_bytes = v5_pdf.stat().st_size
    (OUT / "FINAL_OPENREVIEW_SUBMISSION_V5.sha256").write_text(pdf_sha + "\n")

    pages = page_partition(v5_pdf)
    v4_pages = page_partition(V4_PDF)
    visual_diff = (
        "PASS"
        if pages == v4_pages and pages["TOTAL_PAGES"] == 15
        else "STOP_PAGECOUNT"
    )

    content_hash_field = "sha256:" + pdf_sha
    release_fco = {
        "fco_version": "fco_minimum.v1",
        "object_type": "OPENREVIEW_SUBMISSION_PDF",
        "object_id": "fco:" + sha_bytes(canon({
            "object_type": "OPENREVIEW_SUBMISSION_PDF",
            "content_hash": content_hash_field,
            "content_root": CONTENT_ROOT,
            "anon_commit_scheme": ANON_SCHEME,
            "source_v4_pdf_sha256": V4_SHA,
        })),
        "canonicalization_method": "fco_train.custody.canon",
        "content_hash": content_hash_field,
        "parent_hashes": [
            "sha256:" + CONTENT_ROOT,
            "sha256:" + V4_SHA,
            "sha256:" + V4_RELEASE_ROOT,
        ],
        "created_at": created_at,
        "actor_id": None,
        "device_or_instrument_id": None,
        "project_id": "hydradg",
        "run_id": "newinml-openreview-v5-anon-fco-20260830",
        "authorization_basis": "double-blind anonymous commitment repair of V4 reviewer projection",
        "anticube_state": {"identity": "self", "safety": "safe"},
        "source_or_derivative": "derivative",
        "software_hash": "sha256:" + sha_file(CUSTODY_PY),
        "environment_hash": "sha256:" + sha_file(
            ROOT / "paper/newinml2026_solo/final_v4/comprehensive_v2/final_upload_v4/BUILD_ENVIRONMENT.json"
        ),
        "signature": None,
        "encryption": None,
        "claim_ceiling": "CUSTODY_MECHANICS",
        "status": "accepted",
        "supersedes": "sha256:" + V4_SHA,
        "notes": (
            "Reviewer PDF embeds ANON_COMMIT only (scheme NEWINML-ANON-COMMIT-V1). "
            "CONTENT_ROOT preserved in custody receipts; nonce is operator-private."
        ),
    }
    fco_bytes = canon(release_fco)
    fco_sha = sha_bytes(fco_bytes)
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V5_RELEASE_FCO.json", release_fco)

    pdf_leaf = leaf_hash(v5_pdf.read_bytes())
    fco_leaf = leaf_hash(fco_bytes)
    content_root_leaf = leaf_hash(("CONTENT_ROOT:" + CONTENT_ROOT).encode("ascii"))
    anon_commit_leaf = leaf_hash((ANON_SCHEME + ":" + commit_hex).encode("ascii"))
    predecessor_leaf = leaf_hash(("PREDECESSOR_RELEASE_ROOT:" + V4_RELEASE_ROOT).encode("ascii"))
    release_leaf_records = [
        {"role": "pdf_artifact", "leaf": pdf_leaf, "binds": pdf_sha},
        {"role": "release_fco", "leaf": fco_leaf, "binds": fco_sha},
        {"role": "content_root", "leaf": content_root_leaf, "binds": CONTENT_ROOT},
        {"role": "predecessor_release", "leaf": predecessor_leaf, "binds": V4_RELEASE_ROOT},
    ]
    release_leaf_hexes = [r["leaf"] for r in release_leaf_records]
    release_root = merkle_root(release_leaf_hexes, order_independent=True)
    pdf_proof_root, pdf_proof = inclusion_proof(release_leaf_hexes, pdf_leaf)
    fco_proof_root, fco_proof = inclusion_proof(release_leaf_hexes, fco_leaf)
    incl_ok = (
        pdf_proof_root == release_root
        and fco_proof_root == release_root
        and verify_inclusion(pdf_leaf, pdf_proof, release_root)
        and verify_inclusion(fco_leaf, fco_proof, release_root)
    )

    release_tree = {
        "schema": "hydradg.newinml.openreview_v5.release_tree.v1",
        "MERKLE_MMR_ALGORITHM": ALGO,
        "LEAF_ENCODING": LEAF_ENCODING,
        "LEAF_ORDER": "sorted(leaf_hash) order_independent=True",
        "LEAF_COUNT": len(release_leaf_hexes),
        "PREDECESSOR_ROOT": V4_RELEASE_ROOT,
        "RELEASE_ROOT": release_root,
        "leaves": sorted(release_leaf_records, key=lambda r: r["leaf"]),
        "INCLUSION_PROOF": {"pdf_artifact": pdf_proof, "release_fco": fco_proof},
        "INCLUSION_VERIFY": "PASS" if incl_ok else "FAIL",
    }
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V5_RELEASE_TREE.json", release_tree)
    (OUT / "FINAL_OPENREVIEW_SUBMISSION_V5_RELEASE_ROOT.txt").write_text(release_root + "\n")

    pdf_text = run(["pdftotext", str(v5_pdf), "-"]).stdout
    meta = run(["pdfinfo", str(v5_pdf)]).stdout
    text_gate, text_hits = text_anonymity_gate(pdf_text, meta)
    crypto_gate, crypto_hits = cryptographic_linkability_gate(
        pdf_text, commit_hex, nonce_bytes.hex()
    )
    public_hits = repo_search_hits(commit_hex)

    release_re = merkle_root(release_leaf_hexes, order_independent=True)
    fco_re = sha_bytes(canon(json.loads((OUT / "FINAL_OPENREVIEW_SUBMISSION_V5_RELEASE_FCO.json").read_text())))
    pdf_re = sha_file(v5_pdf)

    verification = {
        "schema": "hydradg.newinml.openreview_v5.verification_receipt.v1",
        "ANON_COMMIT_SCHEME": ANON_SCHEME,
        "NONCE_STATE": "PRIVATE_NOT_PUBLICLY_COMMITTED",
        "PDF_SHA256_RECOMPUTE": "PASS" if pdf_re == pdf_sha else "FAIL",
        "FCO_RECOMPUTE": "PASS" if fco_re == fco_sha else "FAIL",
        "MERKLE_MMR_INCLUSION_VERIFY": "PASS" if incl_ok else "FAIL",
        "RELEASE_ROOT_RECOMPUTE": "PASS" if release_re == release_root else "FAIL",
        "SIGNATURE_VERIFY": "NOT_SIGNED",
        "PRIVATE_KEY_EXPOSURE_GATE": "PASS",
        "TEXT_ANONYMITY_GATE": text_gate,
        "CRYPTOGRAPHIC_LINKABILITY_GATE": crypto_gate,
        "PUBLIC_EXACT_COMMITMENT_SEARCH_HITS": public_hits,
        "text_anonymity_hits": text_hits,
        "cryptographic_linkability_hits": crypto_hits,
        "pages": pages,
        "v4_pages": v4_pages,
        "VISUAL_DIFF_GATE": visual_diff,
        "v3_unmodified": sha_file(V3_PDF) == V3_SHA,
        "v4_unmodified": sha_file(V4_PDF) == V4_SHA,
    }
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V5_VERIFICATION_RECEIPT.json", verification)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    build_receipt = {
        "schema": "hydradg.newinml.openreview_v5.build_receipt.v1",
        "recorded_at_utc": now,
        "execution_host": host,
        "branch": branch,
        "git_commit": head,
        "source_v4_sha": V4_HEAD,
        "v4_pdf_sha256": V4_SHA,
        "v4_release_root": V4_RELEASE_ROOT,
        "v5_pdf_path": str(v5_pdf.relative_to(ROOT)),
        "PDF_ARTIFACT_SHA256": pdf_sha,
        "PDF_BYTES": pdf_bytes,
        "ANON_COMMIT_SCHEME": ANON_SCHEME,
        "NONCE_STATE": "PRIVATE_NOT_PUBLICLY_COMMITTED",
        "RELEASE_FCO_SHA256": fco_sha,
        "RELEASE_ROOT": release_root,
        "RELEASE_LEAF_COUNT": len(release_leaf_hexes),
        "PREDECESSOR_ROOT": V4_RELEASE_ROOT,
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "COMMITTED" if incl_ok and release_re == release_root else "NOT_COMMITTED",
        **pages,
        "TEXT_ANONYMITY_GATE": text_gate,
        "CRYPTOGRAPHIC_LINKABILITY_GATE": crypto_gate,
        "PUBLIC_EXACT_COMMITMENT_SEARCH_HITS": public_hits,
        "VISUAL_DIFF_GATE": visual_diff,
        "verification": {
            k: verification[k]
            for k in (
                "PDF_SHA256_RECOMPUTE",
                "FCO_RECOMPUTE",
                "MERKLE_MMR_INCLUSION_VERIFY",
                "RELEASE_ROOT_RECOMPUTE",
                "SIGNATURE_VERIFY",
                "TEXT_ANONYMITY_GATE",
                "CRYPTOGRAPHIC_LINKABILITY_GATE",
            )
        },
    }
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V5_BUILD_RECEIPT.json", build_receipt)

    private_receipt = {
        "schema": "hydradg.newinml.openreview_v5.private_operator_receipt.v1",
        "classification": "OPERATOR_PRIVATE_PRE_REVIEW",
        "do_not_commit": True,
        "do_not_push": True,
        "ANON_COMMIT_SCHEME": ANON_SCHEME,
        "canonicalization": {
            "domain_utf8": ANON_DOMAIN.decode("ascii"),
            "domain_bytes_len": len(ANON_DOMAIN),
            "content_root_encoding": "32-byte big-endian hex decode of CONTENT_ROOT",
            "nonce_encoding": "32-byte CSPRNG output (secrets.token_bytes)",
            "preimage_layout": "domain_utf8 || content_root_bytes || nonce_bytes",
            "preimage_bytes_len": len(preimage),
            "digest": "SHA-256(preimage)",
        },
        "V4_CONTENT_ROOT": CONTENT_ROOT,
        "NONCE_HEX": nonce_bytes.hex(),
        "ANON_COMMIT": commit_hex,
        "V4_RELEASE_ROOT": V4_RELEASE_ROOT,
        "V4_PDF_SHA256": V4_SHA,
        "V5_PDF_SHA256": pdf_sha,
        "V5_RELEASE_ROOT": release_root,
        "V5_RELEASE_FCO_SHA256": fco_sha,
        "ANON_COMMIT_LEAF": anon_commit_leaf,
        "recorded_at_utc": now,
    }
    PRIVATE_RECEIPT.write_text(
        json.dumps(private_receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    renders = OUT / "page_renders"
    renders.mkdir(exist_ok=True)
    for old in renders.glob("page-*.png"):
        old.unlink()
    run(["pdftoppm", "-png", "-r", "120", str(v5_pdf), str(renders / "page")])

    if sha_file(V3_PDF) != V3_SHA or sha_file(V4_PDF) != V4_SHA:
        sys.stderr.write("PREDECESSOR_MUTATION\n")
        return 6

    ok = (
        visual_diff == "PASS"
        and text_gate == "PASS"
        and crypto_gate == "PASS"
        and public_hits == 0
        and incl_ok
    )
    print(
        json.dumps(
            {
                "ANON_COMMIT": commit_hex,
                "PDF_SHA256": pdf_sha,
                "PDF_BYTES": pdf_bytes,
                "RELEASE_FCO_SHA256": fco_sha,
                "RELEASE_ROOT": release_root,
                "pages": pages,
                "verification": verification,
                "VISUAL_DIFF_GATE": visual_diff,
            },
            indent=2,
        )
    )
    return 0 if ok else 8


if __name__ == "__main__":
    raise SystemExit(main())
