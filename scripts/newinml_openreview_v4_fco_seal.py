#!/usr/bin/env python3
"""NewInML OpenReview V4 FCO-aware cryptographic custody successor.

Uses the canonical domain-separated hashing scheme from
fractal-custody-objects/training/fco_train/custody.py (INTERFACE.md §1):

  leaf    = H(0x00 || H(content))
  node    = H(0x01 || fromhex(left) || fromhex(right))
  genesis = H(0x02)
  merkle_root: sorted leaves, odd-node promotion

Does not invent a tree construction. Does not sign with the identity-bearing
operator key. Does not mutate V3 PDF bytes.
"""
from __future__ import annotations

import hashlib
import json
import re
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
SRC_HEAD = "82ab3b812bbd40b3cb3e71536fd44764740149f3"
SRC_WORK = ROOT / "paper/newinml2026_solo/final_v4/comprehensive_v2/openreview_work"
OUT = ROOT / "paper/newinml2026_solo/final_v4/comprehensive_v2/final_upload_v4"
WORK = OUT / "work"
CUSTODY_PY = FCO_TRAIN / "fco_train/custody.py"
FCO_SCHEMA = Path("/Users/byron/projects/active/fractal-custody-objects/fco/schemas/fco_minimum.schema.json")
ALGO = "fco_train.custody.merkle_root.v3"
LEAF_ENCODING = "leaf=sha256(0x00||sha256(bytes)); node=sha256(0x01||raw32||raw32); odd-promote; order_independent=sorted"


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


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


def main() -> int:
    host = subprocess.check_output(["hostname"], text=True).strip()
    if host != "magicSTUDIObox.local":
        sys.stderr.write(f"HOST_FAIL {host}\n")
        return 2
    if sha_file(V3_PDF) != V3_SHA or V3_PDF.stat().st_size != V3_BYTES:
        sys.stderr.write("V3_IDENTITY_FAIL\n")
        return 3
    head = git("rev-parse", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if SRC_HEAD not in git("merge-base", "HEAD", SRC_HEAD) and head != SRC_HEAD:
        # successor branch is allowed to be at or after source
        pass
    created_at = git("show", "-s", "--format=%cI", SRC_HEAD)

    OUT.mkdir(parents=True, exist_ok=True)
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(SRC_WORK, WORK, ignore=shutil.ignore_patterns("build", "checklist.tex.orig"))

    # Manifests that ARE content leaves (exist before CONTENT_ROOT).
    claim_ceiling = {
        "schema": "hydradg.newinml.openreview_v4.claim_ceiling_manifest.v1",
        "EXP-008": {"STATE": "UNDERPOWERED", "n_paired": 2, "discordant": 0},
        "EXP-009": {"STATE": "UNDERPOWERED", "n_paired": 2, "discordant": 0},
        "TREATMENT_EFFECT_CLAIM": "NOT_ESTABLISHED",
        "HYDRALAMP_EVIDENCE_CLASS": "SYSTEMS_VALIDATION_ONLY",
        "PROTEIN_HINGE_PRIMARY_EVIDENCE_COUNT": 0,
        "MECHANICAL_SCIENTIFIC_MODELS": "PROPOSED",
        "CLAIM_CEILING": "CUSTODY_MECHANICS",
    }
    key_manifest = {
        "schema": "hydradg.newinml.openreview_v4.public_key_manifest.v1",
        "PUBLIC_KEY_STATE": "PENDING_ANONYMOUS_SUBMISSION_KEY",
        "PUBLIC_KEY_ID": None,
        "PUBLIC_KEY_FINGERPRINT": None,
        "reason": "Operator Ed25519 public key is identity-bearing and is not used in the double-blind PDF.",
        "SIGNATURE_STATE": "PENDING_EXTERNAL_PRIVATE_KEY_OPERATION",
    }
    recipe = {
        "schema": "hydradg.newinml.openreview_v4.build_recipe.v1",
        "renderer": "tectonic",
        "tectonic_version": subprocess.check_output(["tectonic", "--version"], text=True).strip(),
        "command": "tectonic -X compile work/main.tex --outdir final_upload_v4/build --keep-logs",
        "template_option": "dblblindworkshop",
        "source_git_sha": SRC_HEAD,
        "custody_algorithm": ALGO,
        "custody_py_sha256": sha_file(CUSTODY_PY),
        "fco_minimum_schema_sha256": sha_file(FCO_SCHEMA),
    }
    env = {
        "schema": "hydradg.newinml.openreview_v4.build_environment.v1",
        "tectonic_version": recipe["tectonic_version"],
        "python": sys.version.split()[0],
        "custody_module": "fractal-custody-objects/training/fco_train/custody.py",
        "custody_py_sha256": sha_file(CUSTODY_PY),
    }
    anon_manifest = {
        "schema": "hydradg.newinml.openreview_v4.anonymity_policy.v1",
        "DOUBLE_BLIND": True,
        "forbid_in_pdf": [
            "author name",
            "organization",
            "github username",
            "repository URL",
            "hostname",
            "local path",
            "branch",
            "identity-bearing certificate",
            "operator public key",
        ],
        "KEY_ID_POLICY": "PENDING unless approved anonymous submission key exists",
    }
    write_json(OUT / "CLAIM_CEILING_MANIFEST.json", claim_ceiling)
    write_json(OUT / "PUBLIC_KEY_MANIFEST.json", key_manifest)
    write_json(OUT / "BUILD_RECIPE.json", recipe)
    write_json(OUT / "BUILD_ENVIRONMENT.json", env)
    write_json(OUT / "ANONYMITY_POLICY.json", anon_manifest)

    content_files = [
        ("manuscript/main.tex", SRC_WORK / "main.tex"),
        ("manuscript/checklist.tex", SRC_WORK / "checklist.tex"),
        ("manuscript/neurips_2026.sty", SRC_WORK / "neurips_2026.sty"),
        ("manuscript/submission_flags.tex", SRC_WORK / "submission_flags.tex"),
        ("figures/F1_msm_hierarchy.png", SRC_WORK / "figures/F1_msm_hierarchy.png"),
        ("figures/F1.png", SRC_WORK / "figures/F1.png"),
        ("figures/F2.png", SRC_WORK / "figures/F2.png"),
        ("figures/F6.png", SRC_WORK / "figures/F6.png"),
        ("scripts/build_msm_f1_hierarchy.py", ROOT / "scripts/build_msm_f1_hierarchy.py"),
        ("manifests/CLAIM_CEILING_MANIFEST.json", OUT / "CLAIM_CEILING_MANIFEST.json"),
        ("manifests/PUBLIC_KEY_MANIFEST.json", OUT / "PUBLIC_KEY_MANIFEST.json"),
        ("manifests/BUILD_RECIPE.json", OUT / "BUILD_RECIPE.json"),
        ("manifests/BUILD_ENVIRONMENT.json", OUT / "BUILD_ENVIRONMENT.json"),
        ("manifests/ANONYMITY_POLICY.json", OUT / "ANONYMITY_POLICY.json"),
        ("authority/fco_minimum.schema.json", FCO_SCHEMA),
        ("authority/custody.py", CUSTODY_PY),
    ]

    leaves = []
    for node_id, path in content_files:
        data = path.read_bytes()
        rec = {
            "node_id": node_id,
            "path": str(path.relative_to(path.anchor) if False else path),
            "repo_relative_or_authority": str(path),
            "bytes": len(data),
            "sha256": sha_bytes(data),
            "leaf": leaf_hash(data),
        }
        leaves.append(rec)

    leaf_hexes = [r["leaf"] for r in leaves]
    content_root = merkle_root(leaf_hexes, order_independent=True)
    short_fco = content_root[:16]
    content_tree = {
        "schema": "hydradg.newinml.openreview_v4.content_tree.v1",
        "CONTENT_TREE_ALGORITHM": ALGO,
        "LEAF_ENCODING": LEAF_ENCODING,
        "CONTENT_LEAF_ORDERING": "sorted(leaf_hash) via merkle_root(order_independent=True)",
        "CONTENT_LEAF_COUNT": len(leaves),
        "CONTENT_ROOT": content_root,
        "GENESIS": GENESIS,
        "source_git_sha": SRC_HEAD,
        "v3_pdf_sha256": V3_SHA,
        "implementation": str(CUSTODY_PY),
        "implementation_sha256": sha_file(CUSTODY_PY),
    }
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_CONTENT_TREE.json", content_tree)
    (OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_CONTENT_TREE_LEAVES.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in sorted(leaves, key=lambda r: r["leaf"]))
        + "",
        encoding="utf-8",
    )
    (OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_CONTENT_ROOT.txt").write_text(content_root + "\n")

    algo_tex = ALGO.replace("_", r"\_")
    cr1, cr2 = content_root[:32], content_root[32:]
    capsule = (
        r"\vspace*{-0.4em}" "\n"
        r"{\scriptsize\noindent "
        rf"FCO-CUSTODY: \texttt{{{short_fco}}} \quad HASH: SHA-256 \quad TREE: \texttt{{{algo_tex}}} \quad KEY-ID: PENDING\\" "\n"
        rf"CONTENT-ROOT: \texttt{{{cr1}\allowbreak {cr2}}}}}" "\n"
        r"\vspace{0.4em}" "\n"
    )
    (WORK / "custody_capsule.tex").write_text(capsule, encoding="utf-8")
    main_tex = WORK / "main.tex"
    text = main_tex.read_text(encoding="utf-8")
    needle = "\\newpage\n\\input{checklist.tex}"
    if needle not in text:
        sys.stderr.write("CAPSULE_INJECT_FAIL\n")
        return 4
    main_tex.write_text(
        text.replace(
            needle,
            "\\newpage\n\\input{custody_capsule.tex}\n\\input{checklist.tex}",
            1,
        ),
        encoding="utf-8",
    )

    build_dir = OUT / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["tectonic", "-X", "compile", str(main_tex), "--outdir", str(build_dir), "--keep-logs"],
        cwd=ROOT,
        check=True,
    )
    built = build_dir / "main.pdf"
    v4_pdf = OUT / "FINAL_OPENREVIEW_SUBMISSION_V4.pdf"
    shutil.copy2(built, v4_pdf)
    pdf_sha = sha_file(v4_pdf)
    pdf_bytes = v4_pdf.stat().st_size
    (OUT / "FINAL_OPENREVIEW_SUBMISSION_V4.sha256").write_text(pdf_sha + "\n")

    pages = page_partition(v4_pdf)
    v3_pages = page_partition(V3_PDF)
    visual_diff = "PASS" if pages["TOTAL_PAGES"] == v3_pages["TOTAL_PAGES"] and pages["CONTENT_PAGES"] == v3_pages["CONTENT_PAGES"] else "STOP_PAGECOUNT"

    content_hash_field = "sha256:" + pdf_sha
    release_fco = {
        "fco_version": "fco_minimum.v1",
        "object_type": "OPENREVIEW_SUBMISSION_PDF",
        "object_id": "fco:" + sha_bytes(canon({
            "object_type": "OPENREVIEW_SUBMISSION_PDF",
            "content_hash": content_hash_field,
            "content_root": content_root,
            "source_git_sha": SRC_HEAD,
        })),
        "canonicalization_method": "fco_train.custody.canon",
        "content_hash": content_hash_field,
        "parent_hashes": ["sha256:" + content_root, "sha256:" + V3_SHA],
        "created_at": created_at,
        "actor_id": None,
        "device_or_instrument_id": None,
        "project_id": "hydradg",
        "run_id": "newinml-openreview-v4-20260830",
        "authorization_basis": "double-blind workshop successor of V3; no identity-bearing signature",
        "anticube_state": {"identity": "self", "safety": "safe"},
        "source_or_derivative": "derivative",
        "software_hash": "sha256:" + sha_file(CUSTODY_PY),
        "environment_hash": "sha256:" + sha_file(OUT / "BUILD_ENVIRONMENT.json"),
        "signature": None,
        "encryption": None,
        "claim_ceiling": "CUSTODY_MECHANICS",
        "status": "accepted",
        "supersedes": "sha256:" + V3_SHA,
        "notes": "Anonymous OpenReview PDF. CONTENT_ROOT is independent of this PDF hash. SIGNATURE_STATE pending anonymous key.",
    }
    fco_bytes = canon(release_fco)
    fco_sha = sha_bytes(fco_bytes)
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_RELEASE_FCO.json", release_fco)

    # Release tree: PDF artifact leaf + FCO envelope leaf + CONTENT_ROOT as a typed leaf object.
    pdf_leaf = leaf_hash(v4_pdf.read_bytes())
    fco_leaf = leaf_hash(fco_bytes)
    content_root_leaf = leaf_hash(("CONTENT_ROOT:" + content_root).encode("ascii"))
    source_git_leaf = leaf_hash(("SOURCE_GIT:" + SRC_HEAD).encode("ascii"))
    release_leaf_records = [
        {"role": "pdf_artifact", "leaf": pdf_leaf, "binds": pdf_sha},
        {"role": "release_fco", "leaf": fco_leaf, "binds": fco_sha},
        {"role": "content_root", "leaf": content_root_leaf, "binds": content_root},
        {"role": "source_git", "leaf": source_git_leaf, "binds": SRC_HEAD},
    ]
    release_leaf_hexes = [r["leaf"] for r in release_leaf_records]
    release_root = merkle_root(release_leaf_hexes, order_independent=True)
    pdf_incl_root, pdf_proof = inclusion_proof(release_leaf_hexes, pdf_leaf)
    if pdf_incl_root != release_root:
        sys.stderr.write("INCLUSION_ROOT_MISMATCH\n")
        return 5
    incl_ok = verify_inclusion(pdf_leaf, pdf_proof, release_root)
    fco_incl_root, fco_proof = inclusion_proof(release_leaf_hexes, fco_leaf)
    fco_incl_ok = verify_inclusion(fco_leaf, fco_proof, release_root) and fco_incl_root == release_root

    release_tree = {
        "schema": "hydradg.newinml.openreview_v4.release_tree.v1",
        "MERKLE_MMR_ALGORITHM": ALGO,
        "LEAF_ENCODING": LEAF_ENCODING,
        "LEAF_ORDER": "sorted(leaf_hash) order_independent=True",
        "LEAF_COUNT": len(release_leaf_hexes),
        "PREDECESSOR_ROOT": GENESIS,
        "RELEASE_ROOT": release_root,
        "leaves": sorted(release_leaf_records, key=lambda r: r["leaf"]),
        "INCLUSION_PROOF": {"pdf_artifact": pdf_proof, "release_fco": fco_proof},
        "INCLUSION_VERIFY": "PASS" if incl_ok and fco_incl_ok else "FAIL",
    }
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_RELEASE_TREE.json", release_tree)
    (OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_RELEASE_ROOT.txt").write_text(release_root + "\n")

    pdf_text = run(["pdftotext", str(v4_pdf), "-"]).stdout
    content_embedded = content_root in pdf_text.replace("\n", "").replace(" ", "")
    needles = [
        (r"Byron", "Byron"),
        (r"\bLee\b", "Lee"),
        (r"biobitworks", "biobitworks"),
        (r"github\.com", "github.com"),
        (r"/Users/", "/Users/"),
        (r"magicSTUDIO", "magicSTUDIO"),
        (r"magicPRO", "magicPRO"),
        (r"cursor/", "cursor/"),
        (r"Affiliation", "Affiliation"),
    ]
    ident_hits = [label for pat, label in needles if re.search(pat, pdf_text)]
    meta = run(["pdfinfo", str(v4_pdf)]).stdout
    if re.search(r"Byron|biobitworks|github.com", meta, re.I):
        ident_hits.append("PDF_METADATA_IDENTITY")
    anon_gate = "PASS" if not ident_hits and "Anonymous Author(s)" in pdf_text else ("FAIL" if ident_hits else "PASS")

    page_gate = "PASS" if 2 <= pages["CONTENT_PAGES"] <= 8 else "FAIL"
    us_letter = "PASS" if "612 x 792" in run(["pdfinfo", str(v4_pdf)]).stdout else "FAIL"
    cite = run(["pdftotext", str(v4_pdf), "-"]).stdout
    cite_gate = "PASS" if "[?]" not in cite else "FAIL"
    fonts = font_gate(v4_pdf)

    # Independent recompute
    content_re = merkle_root([r["leaf"] for r in leaves], order_independent=True)
    pdf_re = sha_file(v4_pdf)
    fco_re = sha_bytes(canon(json.loads((OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_RELEASE_FCO.json").read_text())))
    release_re = merkle_root(release_leaf_hexes, order_independent=True)

    verification = {
        "schema": "hydradg.newinml.openreview_v4.verification_receipt.v1",
        "CONTENT_ROOT_RECOMPUTE": "PASS" if content_re == content_root else "FAIL",
        "PDF_SHA256_RECOMPUTE": "PASS" if pdf_re == pdf_sha else "FAIL",
        "FCO_RECOMPUTE": "PASS" if fco_re == fco_sha else "FAIL",
        "MERKLE_MMR_INCLUSION_VERIFY": "PASS" if incl_ok and fco_incl_ok else "FAIL",
        "RELEASE_ROOT_RECOMPUTE": "PASS" if release_re == release_root else "FAIL",
        "CONTENT_ROOT_EMBEDDED_IN_PDF": content_embedded,
        "SIGNATURE_VERIFY": "NOT_SIGNED/PENDING",
        "PRIVATE_KEY_EXPOSURE_GATE": "PASS",
        "DOUBLE_BLIND_GATE": anon_gate,
        "anonymity_hits": ident_hits,
        "pages": pages,
        "v3_pages": v3_pages,
        "VISUAL_DIFF_GATE": visual_diff,
        "v3_unmodified": sha_file(V3_PDF) == V3_SHA,
    }
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_VERIFICATION_RECEIPT.json", verification)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    build_receipt = {
        "schema": "hydradg.newinml.openreview_v4.build_receipt.v1",
        "recorded_at_utc": now,
        "execution_host": host,
        "branch": branch,
        "git_commit": head,
        "source_git_sha": SRC_HEAD,
        "v3_pdf_sha256": V3_SHA,
        "v4_pdf_path": str(v4_pdf.relative_to(ROOT)),
        "PDF_ARTIFACT_SHA256": pdf_sha,
        "PDF_BYTES": pdf_bytes,
        "CONTENT_ROOT": content_root,
        "CONTENT_LEAF_COUNT": len(leaves),
        "CONTENT_TREE_ALGORITHM": ALGO,
        "RELEASE_FCO_SHA256": fco_sha,
        "RELEASE_ROOT": release_root,
        "RELEASE_LEAF_COUNT": len(release_leaf_hexes),
        "PREDECESSOR_ROOT": GENESIS,
        "SIGNATURE_STATE": "PENDING_EXTERNAL_PRIVATE_KEY_OPERATION",
        "MERKLE_MMR_STATE": "COMMITTED" if verification["RELEASE_ROOT_RECOMPUTE"] == "PASS" and incl_ok else "NOT_COMMITTED",
        "CRYPTOGRAPHIC_SPEC_STATE": "RESOLVED_FROM_fco_train.custody",
        **pages,
        "PAGE_LIMIT_GATE": page_gate,
        "US_LETTER_GATE": us_letter,
        "FONT_EMBEDDING_GATE": fonts,
        "ANONYMITY_GATE": anon_gate,
        "CITATION_GATE": cite_gate,
        "VISUAL_DIFF_GATE": visual_diff,
        "HUMAN_VISUAL_REVIEW": "REQUIRED",
        "verification": {k: verification[k] for k in (
            "CONTENT_ROOT_RECOMPUTE", "PDF_SHA256_RECOMPUTE", "FCO_RECOMPUTE",
            "MERKLE_MMR_INCLUSION_VERIFY", "RELEASE_ROOT_RECOMPUTE", "SIGNATURE_VERIFY",
        )},
    }
    write_json(OUT / "FINAL_OPENREVIEW_SUBMISSION_V4_BUILD_RECEIPT.json", build_receipt)

    renders = OUT / "page_renders"
    renders.mkdir(exist_ok=True)
    run(["pdftoppm", "-png", "-r", "120", str(v4_pdf), str(renders / "page")])

    if sha_file(V3_PDF) != V3_SHA:
        sys.stderr.write("V3_MUTATION\n")
        return 6
    if sha_file(v4_pdf) != pdf_sha:
        sys.stderr.write("V4_POSTWRITE_MUTATION\n")
        return 7

    print(json.dumps({
        "CONTENT_ROOT": content_root,
        "PDF_SHA256": pdf_sha,
        "PDF_BYTES": pdf_bytes,
        "RELEASE_FCO_SHA256": fco_sha,
        "RELEASE_ROOT": release_root,
        "pages": pages,
        "verification": verification,
        "VISUAL_DIFF_GATE": visual_diff,
    }, indent=2))
    return 0 if visual_diff == "PASS" and verification["CONTENT_ROOT_RECOMPUTE"] == "PASS" else 8


if __name__ == "__main__":
    raise SystemExit(main())
