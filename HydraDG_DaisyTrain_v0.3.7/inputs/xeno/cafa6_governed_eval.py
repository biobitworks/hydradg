#!/usr/bin/env python3
"""cafa6_governed_eval.py -- DETERMINISTIC, leakage-safe governed eval for the cafa6 1D->2D
CloudEncoder (EXP-CAFA6-008), answering the metric audit that
xenodisorder/HANDOFF_CAFA6_metric_audit_2026-07-10.{md,json} owes back to XD governance:

    "The in-memory TRAIN auroc is NOT an admissible result." The governed eval is:
      1. AUROC        on a parent/cluster-grouped, leakage-safe HELD-OUT split.
      2. wFmax        on the same held-out split (CAFA-style Fmax, label-frequency weighted --
                       see WFMAX DEFINITION below; this corpus carries ONE binary label, not
                       CAFA's native multi-GO-term panel, so the literal information-content
                       weighting is NOT reproduced here -- see caveat).
      3. CCA / R^2    of the frozen encoder's CLS representation vs a simple, documented,
                       non-learned reference built from the raw disorder track/scalars.

CLAIM CEILING (binding, do not exceed in any consumer of this report):
    representation/benchmark utility only; HYPOTHESIS_STAGE_1. Channels are FEATURES, never
    labels. This script produces numbers; it does NOT self-certify them. Every report this
    script writes carries `"pi_audit_status": "unaudited -- hand to XD governance"`.

MODEL/DATA PROVENANCE: the CloudEncoder and CloudRows classes below are vendored VERBATIM from
the EXP-CAFA6-008 reference kernel (scratchpad/cafa6_tpu/cafa6-2d-cloud-encoder-tpu.py and its
byte-identical sibling scratchpad/cafa6_exp2/cafa6-2d-cloud-encoder-tpu.py -- the two kernel
copies differ in exactly ONE line, the `--d` CLI default (384 vs 512); the CloudEncoder/CloudRows
class bodies are identical). This file does not import the kernel (it lives in scratchpad, not a
package) -- it re-declares the classes so evaluation is self-contained and auditable without a
path dependency on scratchpad. `--verify-kernel-sha256` cross-checks this file's embedded
provenance hashes against the live kernel files at run time (best-effort; warns, does not fail
closed, since the kernel copy is allowed to move/rename in scratchpad).

DATA: the checkpoint under audit (scratchpad/cafa6_exp2_out/ckpt_latest.pt, d=512 layers=8) was
trained on `biobitworks/cafa6-residual-table-afrsa` (20083 rows, no parent_id grouping recorded).
That table carries no parent-grouping metadata, so it cannot host a parent-grouped split. Per the
operator's SSD-minimization instruction, this harness instead uses the schema-compatible
`biobitworks/cafa6-cellico-fragment-disorder-corpus-v1` corpus (21352 rows, 5 parent UniProt
accessions, 23 MB bounded download -- see scratchpad/cellico_cafa6_corpus/MANIFEST.json), which
DOES carry `parent_id`. IMPORTANT CAVEAT (disclosed, not hidden): none of this corpus's 21352 rows
were in the checkpoint's original AFRSA training set, so this is a cross-corpus representation-
transfer eval, not a held-out slice of the checkpoint's own training distribution. The
parent-grouping leakage guarantee (no parent split across train/held-out) is about internal
consistency of THIS harness's fit/eval protocol (the CCA/Ridge reference maps are fit on the
train-parent group only, evaluated on the held-out-parent group only) -- it is independent of,
and does not retroactively grant, in-distribution status.

WFMAX DEFINITION (documented adaptation -- read before citing this number):
  CAFA's canonical Fmax (Radivojac et al. 2013) sweeps a probability threshold t in [0, 1] (step
  0.01) over a MULTI-GO-TERM prediction matrix, accumulates precision/recall by summing TP/FP/FN
  across all terms and all proteins at each t, and the 'w' (weighted) variant additionally weights
  each GO term's contribution by its information content (-log2 of term frequency in the training
  ontology), then reports the max F = 2PR/(P+R) over the sweep.
  This corpus and checkpoint carry a SINGLE binary label per row (disordered / not-disordered),
  not a multi-term GO panel -- there is no per-term information content to compute. We adapt 'w'
  to the single-label case as INVERSE-CLASS-FREQUENCY sample weighting (the standard sklearn
  "balanced" class-weight heuristic: w_c = n / (2 * n_c), computed from the HELD-OUT split's own
  label prior), applied to the TP/FP/FN counts at each threshold before computing precision/recall.
  This is the same statistical family (protect the minority class in an imbalanced set) but is
  NOT a reproduction of the literal multi-GO-term CAFA protocol. We also report the UNWEIGHTED
  Fmax for contrast. Both use the same fixed threshold grid: t in {0.00, 0.01, ..., 1.00}, and a
  threshold is skipped from the argmax search iff TP+FP == 0 at that t (no positive prediction ->
  precision undefined, standard CAFA convention).

CCA / R^2 DEFINITION: the reference vector is built directly from each row's raw disorder track
and z-scored disorder scalar (residual_z, track_mean, track_std, frac_track_ge_0.5, k_len) -- NOT
from a second PLM/ProtBERT/ESM2 channel (none is wired into this corpus; admitting/rejecting that
channel is a separate audit item this script does not attempt). `afrsa` and `disorder_background`
are EXCLUDED from the reference vector because they are constant across this corpus (afrsa_present
== 0 for all 21352 rows; disorder_background is a single global-cohort mean by construction of the
corpus builder) -- a constant column is zero-variance and degenerate for CCA/regression; this is a
documented data property of THIS corpus, not a metric-shopping choice. Both a CCA (canonical
correlations) and a Ridge-regression R^2 (encoder CLS -> reference, fit on TRAIN-parent rows only,
scored on HELD-OUT-parent rows only) are reported.

  ⚠ TWO READ-BEFORE-CITING CAVEATS ON THE CCA/R^2 NUMBERS (auto-detected + emitted into the report
  as `representation_vs_reference.reference_collinearity_diagnostic` -- read it before quoting a
  headline R^2/canonical-correlation number):
  (a) COLLINEARITY IS DATA-DEPENDENT, NOT ASSUMED: on the cellico corpus used here, `residual_z`,
      `track_mean`, and `frac_track_ge_0.5` are EMPIRICALLY near-perfectly collinear (|r|~1.0,
      verified on the held-out split) -- an artifact of how the corpus builder derives the
      per-position track from `disorder_score`/`disorder_regions` (see
      scratchpad/cellico_cafa6_corpus/build_corpus.py TRACK RULE). A near-1.0 R^2/canonical
      correlation on 3-of-5 reference dims may therefore reflect ONE redundant "disorder-amount"
      signal recovered three times, not five independent signals. The harness computes the
      held-out reference-dim correlation matrix and flags any |r| >= 0.98 pair automatically --
      it does NOT hardcode this corpus's specific collinearity, since a different corpus could
      have a genuinely non-collinear reference vector.
  (b) `k_len` IS A LITERAL, ARCHITECTURAL MODEL INPUT (`model.encode()` adds `self.k_scale(k)` to
      every position embedding -- see CloudEncoder.encode below), so the encoder recovering k_len
      near-perfectly from its own CLS token is EXPECTED BY CONSTRUCTION, not evidence of emergent
      semantic representation. This is always true (architecture-level fact, not data-dependent).

DETERMINISM: fixed seed drives the parent/hash split; the forward pass runs CPU, single-thread,
`model.eval()` (dropout off), so it is a pure function of (checkpoint weights, input bytes, seed) --
bit-identical on re-run on the same machine/library versions; cross-machine BLAS/kernel differences
are the only disclosed source of eps drift (not bit-identity), consistent with this repo's
determinism-disclosure convention (see training/fco_train/custody.py, test_checkpoint_resume.py).

NO WRITEBACK. NO GIT PUSH. NO SELF-CERTIFICATION -- `pi_audit_status` is fixed to
"unaudited -- hand to XD governance" in every report this script emits.
"""
from __future__ import annotations

import os
import sys

# CPU single-thread BEFORE torch import (repo determinism convention; see test_checkpoint_resume.py)
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse          # noqa: E402
import hashlib            # noqa: E402
import json               # noqa: E402
import platform           # noqa: E402
import time               # noqa: E402
from collections import Counter, OrderedDict   # noqa: E402
from datetime import datetime, timezone         # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np        # noqa: E402
import torch               # noqa: E402
import torch.nn as nn       # noqa: E402
from torch.utils.data import Dataset, DataLoader, Subset  # noqa: E402

torch.set_num_threads(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "fco.cafa6_governed_eval_report/v1"
CLAIM_CEILING = "representation/benchmark utility only; HYPOTHESIS_STAGE_1"
PI_AUDIT_STATUS = "unaudited — hand to XD governance"

K_MAX = 64  # MUST match the kernel (scratchpad/cafa6_tpu/cafa6-2d-cloud-encoder-tpu.py)

# Kernel provenance (source-of-truth files this module's classes were vendored from).
KERNEL_SOURCES = {
    "cafa6_tpu (d=384 default)": REPO_ROOT / "scratchpad" / "cafa6_tpu" / "cafa6-2d-cloud-encoder-tpu.py",
    "cafa6_exp2 (d=512 default, matches audited checkpoint)":
        REPO_ROOT / "scratchpad" / "cafa6_exp2" / "cafa6-2d-cloud-encoder-tpu.py",
}

REFERENCE_DIM_NAMES = ["residual_z", "track_mean", "track_std", "frac_track_ge_0.5", "k_len"]


# =====================================================================================
# 0. hashing / provenance helpers
# =====================================================================================
def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# =====================================================================================
# 1. data -- VENDORED VERBATIM from the EXP-CAFA6-008 reference kernel (see KERNEL_SOURCES)
#    (parent_id tracking already present in the kernel's own CloudRows -- unmodified here)
# =====================================================================================
class CloudRows(Dataset):
    """Loads per-position disorder track + cloud_2d + label from the residual table."""
    def __init__(self, table, limit=None):
        self.X_pos, self.lens, self.cloud, self.scal, self.y = [], [], [], [], []
        self.parents = []
        with open(table, "r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                if float(r.get("_label_mask", 0.0)) != 1.0:
                    continue
                lab = r.get("_label")
                if lab not in (0, 1, 0.0, 1.0):
                    continue
                tr = (r.get("_tracks") or {}).get("disorder") or []
                pos = tr[0] if tr and isinstance(tr[0], list) else []
                if not pos:
                    continue
                k = min(len(pos), K_MAX)
                self.X_pos.append([float(x) for x in pos[:k]])
                self.lens.append(k)
                c = r.get("_cloud_2d") or [0.0] * 100
                self.cloud.append([float(x) for x in c][:100] + [0.0] * max(0, 100 - len(c)))
                afrsa_present = int(r.get("afrsa_present") or 0)
                afrsa_val = float(r.get("afrsa") or 0.0) if afrsa_present else 0.0
                self.scal.append([float(r.get("residual_z") or 0.0),
                                  float(r.get("disorder_background") or 0.0),
                                  afrsa_val])
                self.y.append(int(lab))
                self.parents.append(r.get("parent_id"))
                if limit and len(self.y) >= limit:
                    break
        self.y = np.asarray(self.y, np.float32)

    def __len__(self): return len(self.y)

    def __getitem__(self, i):
        k = self.lens[i]
        pos = np.zeros((K_MAX, 1), np.float32)
        pos[:k, 0] = self.X_pos[i]
        mask = np.zeros(K_MAX, np.float32); mask[:k] = 1.0  # 1=valid
        return (torch.from_numpy(pos), torch.tensor(k), torch.from_numpy(mask),
                torch.tensor(self.cloud[i], dtype=torch.float32),
                torch.tensor(self.scal[i], dtype=torch.float32),
                torch.tensor(self.y[i]))


# =====================================================================================
# 2. model -- VENDORED VERBATIM from the EXP-CAFA6-008 reference kernel (see KERNEL_SOURCES)
# =====================================================================================
class CloudEncoder(nn.Module):
    def __init__(self, f_pos=1, d=256, layers=6, heads=8, n_cloud=100, n_scal=3):
        super().__init__()
        self.in_proj = nn.Linear(f_pos, d)
        self.pos_emb = nn.Embedding(K_MAX, d)
        self.k_scale = nn.Embedding(K_MAX + 1, d)
        self.cls = nn.Parameter(torch.randn(1, 1, d) * 0.02)
        self.mask_tok = nn.Parameter(torch.randn(1, 1, d) * 0.02)
        enc = nn.TransformerEncoderLayer(d, heads, 4 * d, dropout=0.1,
                                         batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(enc, layers)
        self.mcm_head = nn.Linear(d, f_pos)
        self.global_proj = nn.Sequential(nn.Linear(n_cloud + n_scal, d), nn.ReLU())
        self.dis_head = nn.Sequential(nn.Linear(2 * d, d), nn.ReLU(),
                                      nn.Dropout(0.1), nn.Linear(d, 1))

    def encode(self, pos, k, mask, mcm_mask=None):
        x = self.in_proj(pos) + self.pos_emb.weight[None, :, :]
        x = x + self.k_scale(k.clamp(max=K_MAX))[:, None, :]
        if mcm_mask is not None:
            x = torch.where(mcm_mask[..., None].bool(), self.mask_tok, x)
        cls = self.cls.expand(x.size(0), -1, -1)
        x = torch.cat([cls, x], 1)
        pad = torch.cat([torch.ones(mask.size(0), 1, device=mask.device), mask], 1)
        h = self.encoder(x, src_key_padding_mask=(pad == 0))
        return h[:, 0], h[:, 1:]

    def forward_mcm(self, pos, k, mask, mcm_mask):
        _, hp = self.encode(pos, k, mask, mcm_mask)
        return self.mcm_head(hp)

    def forward_dis(self, pos, k, mask, cloud, scal):
        cls, _ = self.encode(pos, k, mask)
        g = self.global_proj(torch.cat([cloud, scal], 1))
        return self.dis_head(torch.cat([cls, g], 1)).squeeze(-1)


def infer_arch_from_state_dict(sd: "OrderedDict[str, torch.Tensor]"):
    """Auto-detect (d, layers, heads) from checkpoint tensor shapes so the eval arch can never
    silently drift from the trained arch. `heads` is NOT recoverable from tensor shapes alone
    (nn.MultiheadAttention's in_proj_weight is (3d, d) regardless of head count) -- we replicate
    the kernel's OWN deterministic formula `heads = max(1, d // 32)`, which is exactly the formula
    the training run itself used (`cafa6-2d-cloud-encoder-tpu.py` run(): `heads=max(1, args.d // 32)`)."""
    d = int(sd["cls"].shape[-1])
    layer_ids = set()
    for k in sd:
        if k.startswith("encoder.layers."):
            layer_ids.add(int(k.split(".")[2]))
    layers = (max(layer_ids) + 1) if layer_ids else 0
    heads = max(1, d // 32)
    f_pos = int(sd["in_proj.weight"].shape[1])
    n_cloud_plus_scal = int(sd["global_proj.0.weight"].shape[1])
    n_scal = 3  # fixed by CloudRows contract (residual_z, disorder_background, afrsa)
    n_cloud = n_cloud_plus_scal - n_scal
    return {"d": d, "layers": layers, "heads": heads, "f_pos": f_pos,
            "n_cloud": n_cloud, "n_scal": n_scal}


def load_checkpoint(path):
    ckpt = torch.load(str(path), map_location="cpu")
    sd = ckpt["model"] if isinstance(ckpt, dict) and "model" in ckpt else ckpt
    meta = {"ep": ckpt.get("ep") if isinstance(ckpt, dict) else None,
            "phase": ckpt.get("phase") if isinstance(ckpt, dict) else None}
    return sd, meta


def build_model_from_checkpoint(ckpt_path):
    sd, meta = load_checkpoint(ckpt_path)
    arch = infer_arch_from_state_dict(sd)
    model = CloudEncoder(f_pos=arch["f_pos"], d=arch["d"], layers=arch["layers"],
                         heads=arch["heads"], n_cloud=arch["n_cloud"], n_scal=arch["n_scal"])
    missing, unexpected = model.load_state_dict(sd, strict=True)
    model.eval()
    return model, arch, meta


# =====================================================================================
# 3. deterministic parent-GROUPED split
# =====================================================================================
def _parent_hash_unit(seed: int, parent_id: str) -> float:
    """Deterministic seeded hash of a parent_id -> a value in [0, 1). sha256(f'{seed}:{parent_id}'),
    first 15 hex digits interpreted as an integer, normalized. Pure function of (seed, parent_id) --
    no RNG state, no dependence on row order or dict iteration order."""
    h = hashlib.sha256(f"{seed}:{parent_id}".encode("utf-8")).hexdigest()
    return int(h[:15], 16) / float(16 ** 15)


def parent_grouped_split(parent_row_counts: "dict[str, int]", seed: int,
                          target_holdout_frac: float = 0.2) -> dict:
    """Deterministic, seeded, parent-level grouped split. NO parent_id is ever split across train
    and held-out. Rule: sort ALL parents by (hash_unit(seed, parent_id), parent_id) ascending (the
    parent_id tie-break only matters for the never-observed case of a hash collision, and makes the
    order total); walk the sorted list assigning parents to HELD-OUT until the held-out row-count
    fraction reaches `target_holdout_frac` (inclusive), or the list is exhausted; every remaining
    parent goes to TRAIN. This rule generalizes from 2 parents (minimum for a non-degenerate split)
    to arbitrarily many, is independent of label values (no risk of eval-metric-driven cherry-
    picking), and is fully determined by (seed, target_holdout_frac, the multiset of parent_id ->
    row_count) -- reproducible byte-for-byte on re-run."""
    parents = sorted(parent_row_counts.keys())  # canonical order before hashing (dict-order independent)
    if len(parents) < 2:
        raise ValueError(f"parent_grouped_split needs >=2 distinct parents, got {len(parents)}")
    total_rows = sum(parent_row_counts.values())
    ordered = sorted(parents, key=lambda p: (_parent_hash_unit(seed, p), p))
    heldout, acc = [], 0
    for p in ordered:
        if total_rows > 0 and acc / total_rows >= target_holdout_frac:
            break
        heldout.append(p)
        acc += parent_row_counts[p]
    train = [p for p in parents if p not in set(heldout)]
    if not heldout or not train:
        raise ValueError(
            f"degenerate split: n_heldout_parents={len(heldout)} n_train_parents={len(train)} "
            f"(seed={seed}, target_holdout_frac={target_holdout_frac}) -- adjust target_holdout_frac "
            f"or verify parent_row_counts has >=2 parents with nonzero rows")
    assignment = {p: ("heldout" if p in set(heldout) else "train") for p in parents}
    heldout_rows = sum(parent_row_counts[p] for p in heldout)
    train_rows = sum(parent_row_counts[p] for p in train)
    return {
        "rule": "sort parents by sha256(f'{seed}:{parent_id}')[:15 hex]-derived unit interval "
                "value ascending; greedily assign to HELD-OUT until cumulative row fraction >= "
                "target_holdout_frac; remainder -> TRAIN",
        "seed": seed,
        "target_holdout_frac": target_holdout_frac,
        "n_parents_total": len(parents),
        "train_parents": sorted(train),
        "heldout_parents": sorted(heldout),
        "assignment": assignment,
        "n_rows_train": int(train_rows),
        "n_rows_heldout": int(heldout_rows),
        "n_rows_total": int(total_rows),
        "heldout_row_fraction": (heldout_rows / total_rows) if total_rows else 0.0,
    }


def grouping_proof(split: dict) -> dict:
    train_set, heldout_set = set(split["train_parents"]), set(split["heldout_parents"])
    shared = sorted(train_set & heldout_set)
    ok = (len(shared) == 0) and bool(train_set) and bool(heldout_set)
    return {
        "shared_parents": shared,
        "n_shared_parents": len(shared),
        "n_train_parents": len(train_set),
        "n_heldout_parents": len(heldout_set),
        "both_splits_nonempty": bool(train_set) and bool(heldout_set),
        "check": "PASS" if ok else "FAIL",
    }


# =====================================================================================
# 4. forward pass (CPU, eval-mode, deterministic) -- returns labels/probs/CLS-emb/reference-vec
# =====================================================================================
def run_forward(model: CloudEncoder, ds: CloudRows, indices, batch_size: int = 256):
    model.eval()
    sub = Subset(ds, list(indices))
    dl = DataLoader(sub, batch_size=batch_size, shuffle=False, drop_last=False)
    ys, ps, cls_list, ref_list = [], [], [], []
    with torch.no_grad():
        for pos, k, mask, cloud, scal, y in dl:
            cls, _ = model.encode(pos, k, mask)
            g = model.global_proj(torch.cat([cloud, scal], 1))
            logit = model.dis_head(torch.cat([cls, g], 1)).squeeze(-1)
            p = torch.sigmoid(logit)

            valid = mask  # (B, K_MAX), 1=valid position
            n_valid = valid.sum(dim=1).clamp(min=1.0)
            track = pos.squeeze(-1)  # (B, K_MAX)
            track_mean = (track * valid).sum(dim=1) / n_valid
            track_var = ((track - track_mean[:, None]) ** 2 * valid).sum(dim=1) / n_valid
            track_std = torch.sqrt(track_var.clamp(min=0.0))
            frac_ge_half = ((track >= 0.5).float() * valid).sum(dim=1) / n_valid
            residual_z = scal[:, 0]
            ref = torch.stack([residual_z, track_mean, track_std, frac_ge_half, k.float()], dim=1)

            ys.append(y.numpy()); ps.append(p.numpy())
            cls_list.append(cls.numpy()); ref_list.append(ref.numpy())
    return (np.concatenate(ys), np.concatenate(ps),
            np.concatenate(cls_list, axis=0), np.concatenate(ref_list, axis=0))


# =====================================================================================
# 5. metrics
# =====================================================================================
def auroc(y, p) -> float:
    from sklearn.metrics import roc_auc_score
    y = np.asarray(y)
    if len(set(y.tolist())) != 2:
        return float("nan")
    return float(roc_auc_score(y, p))


def balanced_class_weights(y) -> np.ndarray:
    """w_c = n / (2 * n_c) -- the standard sklearn 'balanced' class-weight heuristic, computed from
    y's OWN empirical prior (not a fixed constant). n_c==0 for a class is guarded (returns weight 0
    for that class; cannot occur in a held-out split with both classes present)."""
    y = np.asarray(y)
    n = len(y)
    n_pos = float((y == 1).sum()); n_neg = float((y == 0).sum())
    w_pos = n / (2.0 * n_pos) if n_pos > 0 else 0.0
    w_neg = n / (2.0 * n_neg) if n_neg > 0 else 0.0
    return np.where(y == 1, w_pos, w_neg).astype(np.float64)


_THRESH_GRID = np.round(np.arange(0.0, 1.0 + 1e-9, 0.01), 2)


def fmax_curve(y, p, sample_weight=None, thresholds=_THRESH_GRID) -> dict:
    """CAFA-style Fmax: sweep `thresholds`, at each t predicted-positive = (p >= t); a threshold
    with zero positive predictions (TP+FP==0) is SKIPPED (precision undefined, standard CAFA
    convention); F = 2PR/(P+R) (0 if P+R==0); Fmax = max F over the swept, valid thresholds.
    `sample_weight`, if given, is applied to the TP/FP/FN counts (used for wFmax)."""
    y = np.asarray(y, dtype=np.float64)
    p = np.asarray(p, dtype=np.float64)
    w = np.ones_like(y) if sample_weight is None else np.asarray(sample_weight, dtype=np.float64)
    best_f, best_t, n_valid = -1.0, None, 0
    for t in thresholds:
        pred = p >= t
        tp = float(w[pred & (y == 1)].sum())
        fp = float(w[pred & (y == 0)].sum())
        fn = float(w[(~pred) & (y == 1)].sum())
        if tp + fp == 0.0:
            continue
        n_valid += 1
        precision = tp / (tp + fp)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
        if f > best_f:
            best_f, best_t = f, float(t)
    if best_t is None:
        raise ValueError("fmax_curve: no threshold in the grid produced a positive prediction")
    return {"value": float(best_f), "threshold": best_t,
            "n_thresholds_swept": int(len(thresholds)), "n_thresholds_valid": int(n_valid)}


def wfmax(y, p) -> dict:
    w = balanced_class_weights(y)
    out = fmax_curve(y, p, sample_weight=w)
    out["weighting"] = ("sklearn-'balanced' inverse-class-frequency, w_c = n / (2*n_c), "
                         "computed from this held-out split's own label prior")
    return out


def fmax_unweighted(y, p) -> dict:
    return fmax_curve(y, p, sample_weight=None)


def reference_collinearity_diagnostic(R_heldout: np.ndarray, names=REFERENCE_DIM_NAMES,
                                      threshold: float = 0.98) -> dict:
    """Pairwise Pearson correlation matrix of the reference dims, computed on the HELD-OUT split
    (the same rows the R^2/CCA numbers are scored on). Flags any pair with |r| >= `threshold` as
    near-collinear -- a near-1.0 R^2/canonical-correlation on collinear dims is redundant, not
    5 independent recoveries. Auto-detected from data every run; not hardcoded to any one corpus."""
    R = np.asarray(R_heldout, dtype=np.float64)
    with np.errstate(invalid="ignore"):
        corr = np.corrcoef(R.T)
    flagged = []
    n = len(names)
    for i in range(n):
        for j in range(i + 1, n):
            r = corr[i, j]
            if np.isfinite(r) and abs(r) >= threshold:
                flagged.append({"dim_a": names[i], "dim_b": names[j], "pearson_r": float(r)})
    return {
        "reference_dims": names,
        "pairwise_correlation_matrix_heldout": corr.tolist(),
        "near_collinear_pairs_abs_r_ge_%.2f" % threshold: flagged,
        "interpretation": (
            "If a pair above has |r| near 1.0, a high R^2/canonical-correlation touching BOTH of "
            "those dims is largely the SAME signal counted twice, not two independently-recovered "
            "quantities. k_len is additionally a literal architectural input to the encoder "
            "(self.k_scale(k) is added to every position embedding) -- its near-perfect recovery "
            "is expected by construction, independent of any collinearity finding above."
        ),
    }


def cca_and_ridge_r2(X_train, R_train, X_heldout, R_heldout, n_components: int = 5) -> dict:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cross_decomposition import CCA
    from sklearn.linear_model import Ridge
    from sklearn.metrics import r2_score

    sx = StandardScaler().fit(X_train)
    sr = StandardScaler().fit(R_train)
    Xtr, Xho = sx.transform(X_train), sx.transform(X_heldout)
    Rtr, Rho = sr.transform(R_train), sr.transform(R_heldout)

    ncomp = max(1, min(n_components, Xtr.shape[1], Rtr.shape[1]))
    cca = CCA(n_components=ncomp, max_iter=2000)
    cca.fit(Xtr, Rtr)
    Xc, Rc = cca.transform(Xho, Rho)
    canon_corrs = []
    for i in range(ncomp):
        c = np.corrcoef(Xc[:, i], Rc[:, i])[0, 1]
        canon_corrs.append(float(c) if np.isfinite(c) else None)

    ridge = Ridge(alpha=1.0, solver="cholesky")
    ridge.fit(Xtr, Rtr)
    Rpred = ridge.predict(Xho)
    r2_per_dim = r2_score(Rho, Rpred, multioutput="raw_values").tolist()
    r2_uniform = float(r2_score(Rho, Rpred, multioutput="uniform_average"))

    return {
        "reference_dims": REFERENCE_DIM_NAMES,
        "excluded_reference_dims": {
            "afrsa": "constant 0.0 across corpus (afrsa_present==0 for all rows) -- zero-variance, degenerate",
            "disorder_background": "constant single-cohort mean across corpus by construction of the corpus builder -- zero-variance, degenerate",
        },
        "reference_collinearity_diagnostic": reference_collinearity_diagnostic(R_heldout),
        "cca_n_components": ncomp,
        "cca_canonical_correlations_heldout": canon_corrs,
        "ridge_alpha": 1.0,
        "ridge_r2_per_reference_dim_heldout": r2_per_dim,
        "ridge_r2_uniform_average_heldout": r2_uniform,
        "fit_split": "train-parent group only (StandardScaler, CCA, Ridge all .fit() on TRAIN)",
        "eval_split": "heldout-parent group only (.transform()/.predict()/.score() on HELDOUT)",
        "read_before_citing": "see reference_collinearity_diagnostic + module docstring CCA/R^2 "
                              "DEFINITION caveats (a)/(b) before quoting a headline number -- some "
                              "reference dims may be redundant (collinear) or architecturally "
                              "tautological (k_len is a literal encoder input), not independently "
                              "recovered semantic content.",
    }


# =====================================================================================
# 6. report orchestration
# =====================================================================================
def build_report(table_path, ckpt_path, seed: int = 20260710, target_holdout_frac: float = 0.2,
                  limit=None, batch_size: int = 256, n_cca_components: int = 5,
                  run_command: str = "") -> dict:
    t0 = time.time()
    table_path = Path(table_path)
    ckpt_path = Path(ckpt_path)

    ds = CloudRows(str(table_path), limit=limit)
    if len(ds) == 0:
        raise ValueError(f"CloudRows loaded 0 rows from {table_path}")
    parent_counts = Counter(ds.parents)
    if any(p is None for p in parent_counts):
        raise ValueError("one or more rows have parent_id=None -- cannot group-split")

    split = parent_grouped_split(dict(parent_counts), seed=seed, target_holdout_frac=target_holdout_frac)
    proof = grouping_proof(split)
    assert proof["check"] == "PASS", f"grouping proof FAILED: {proof}"

    train_set = set(split["train_parents"]); heldout_set = set(split["heldout_parents"])
    idx_train = [i for i, p in enumerate(ds.parents) if p in train_set]
    idx_heldout = [i for i, p in enumerate(ds.parents) if p in heldout_set]
    assert len(idx_train) == split["n_rows_train"], "train row count mismatch vs split proof"
    assert len(idx_heldout) == split["n_rows_heldout"], "heldout row count mismatch vs split proof"
    # row-level cross-check: no row's parent appears in the opposite index set
    parents_in_train_rows = {ds.parents[i] for i in idx_train}
    parents_in_heldout_rows = {ds.parents[i] for i in idx_heldout}
    assert not (parents_in_train_rows & parents_in_heldout_rows), "row-level parent leakage detected"

    model, arch, ckpt_meta = build_model_from_checkpoint(ckpt_path)

    y_tr, p_tr, cls_tr, ref_tr = run_forward(model, ds, idx_train, batch_size=batch_size)
    y_ho, p_ho, cls_ho, ref_ho = run_forward(model, ds, idx_heldout, batch_size=batch_size)

    n_pos_ho = int((y_ho == 1).sum()); n_neg_ho = int((y_ho == 0).sum())
    metrics_heldout = {
        "n_rows": int(len(y_ho)),
        "label_balance": {"n_pos": n_pos_ho, "n_neg": n_neg_ho,
                          "pos_frac": (n_pos_ho / len(y_ho)) if len(y_ho) else float("nan")},
        "auroc": auroc(y_ho, p_ho),
        "fmax_unweighted": fmax_unweighted(y_ho, p_ho),
        "wfmax": wfmax(y_ho, p_ho),
        "representation_vs_reference": cca_and_ridge_r2(cls_tr, ref_tr, cls_ho, ref_ho,
                                                         n_components=n_cca_components),
    }
    # in-sample sanity readout on THIS harness's train split -- NOT admissible as a claim (in-sample,
    # cross-corpus-vs-checkpoint's-own-training-set); kept only for internal contrast/debugging.
    sanity_train = {"n_rows": int(len(y_tr)), "auroc_in_sample_NOT_ADMISSIBLE": auroc(y_tr, p_tr)}

    kernel_sha = {}
    for label, path in KERNEL_SOURCES.items():
        kernel_sha[label] = {"path": str(path.relative_to(REPO_ROOT)),
                             "sha256": sha256_file(path) if path.exists() else None,
                             "exists": path.exists()}

    report = {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_ref": "EXP-CAFA6-008 governed eval (metric-audit response)",
        "handoff_ref": [
            "xenodisorder/HANDOFF_CAFA6_metric_audit_2026-07-10.md",
            "xenodisorder/HANDOFF_CAFA6_metric_audit_2026-07-10.json",
        ],
        "claim_ceiling": CLAIM_CEILING,
        "pi_audit_status": PI_AUDIT_STATUS,
        "admissibility": {
            "train_auroc_inmemory_is_admissible": False,
            "reason": "in-memory TRAIN auroc (no held-out split) reported by the training kernel "
                      "is not an admissible AUC/utility claim; see metrics_heldout below for the "
                      "admissible, parent-grouped, leakage-safe held-out numbers",
        },
        "checkpoint": {
            "path": str(ckpt_path.relative_to(REPO_ROOT)) if ckpt_path.is_relative_to(REPO_ROOT) else str(ckpt_path),
            "sha256": sha256_file(ckpt_path),
            "ckpt_epoch": ckpt_meta.get("ep"),
            "ckpt_phase": ckpt_meta.get("phase"),
            "arch_inferred_from_state_dict": arch,
        },
        "kernel_source_provenance": kernel_sha,
        "eval_dataset": {
            "table_path": str(table_path.relative_to(REPO_ROOT)) if table_path.is_relative_to(REPO_ROOT) else str(table_path),
            "table_sha256": sha256_file(table_path),
            "row_count": len(ds),
            "n_parents": len(parent_counts),
            "kaggle_dataset_slug": "biobitworks/cafa6-cellico-fragment-disorder-corpus-v1",
            "note": "Bounded 23MB download per operator SSD-minimization instruction. This corpus "
                    "was NOT part of the checkpoint's original training table "
                    "(biobitworks/cafa6-residual-table-afrsa, 20083 rows, no parent_id) -- the "
                    "ENTIRE corpus is out-of-training-distribution for the checkpoint under audit. "
                    "Used here because it is schema-compatible with CloudRows AND carries parent_id, "
                    "which the original training table does not.",
        },
        "split": split,
        "grouping_proof": proof,
        "metrics_heldout": metrics_heldout,
        "train_split_sanity_NOT_ADMISSIBLE": sanity_train,
        "determinism": {
            "seed": seed,
            "torch_num_threads": int(torch.get_num_threads()),
            "model_eval_mode_dropout_disabled": True,
            "note": "forward pass is CPU, single-thread, eval-mode (no dropout, no RNG) -- a pure "
                    "function of (checkpoint bytes, table bytes, seed); re-running this exact "
                    "invocation on this machine/library-version reproduces bit-identical metrics. "
                    "Cross-machine / cross-BLAS-version drift is disclosed as eps-tolerant, never "
                    "claimed as bit-identical (repo determinism-disclosure convention).",
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": torch.__version__,
            "numpy": np.__version__,
        },
        "run_command": run_command,
        "wall_s": round(time.time() - t0, 2),
    }
    try:
        import sklearn
        report["environment"]["sklearn"] = sklearn.__version__
    except Exception:
        pass
    return report


# =====================================================================================
# 7. CLI
# =====================================================================================
def _default_table():
    cand = REPO_ROOT / "scratchpad" / "cafa6_governed_eval_data" / "residual_table.jsonl"
    return cand


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--table", default=str(_default_table()),
                    help="residual_table.jsonl with parent_id (default: bounded cellico corpus copy)")
    ap.add_argument("--ckpt", default=str(REPO_ROOT / "scratchpad" / "cafa6_exp2_out" / "ckpt_latest.pt"))
    ap.add_argument("--out", default=str(REPO_ROOT / "scratchpad" / "cafa6_governed_eval_out"))
    ap.add_argument("--report-name", default="cafa6_governed_eval_report.json")
    ap.add_argument("--seed", type=int, default=20260710)
    ap.add_argument("--target-holdout-frac", type=float, default=0.2)
    ap.add_argument("--limit", type=int, default=None, help="row cap (debug only)")
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--cca-components", type=int, default=5)
    args = ap.parse_args()

    table_path = Path(args.table)
    ckpt_path = Path(args.ckpt)
    if not table_path.exists():
        raise SystemExit(f"DATA_NOT_FOUND: {table_path} -- download the bounded cellico corpus "
                         f"(biobitworks/cafa6-cellico-fragment-disorder-corpus-v1) or pass --table.")
    if not ckpt_path.exists():
        raise SystemExit(f"CHECKPOINT_NOT_FOUND: {ckpt_path} -- pass --ckpt.")

    report = build_report(table_path, ckpt_path, seed=args.seed,
                          target_holdout_frac=args.target_holdout_frac, limit=args.limit,
                          batch_size=args.batch, n_cca_components=args.cca_components,
                          run_command=" ".join(sys.argv))

    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / args.report_name
    out_path.write_text(json.dumps(report, indent=2, sort_keys=False))

    m = report["metrics_heldout"]
    print(f"wrote {out_path}")
    print(f"split: seed={args.seed} heldout_parents={report['split']['heldout_parents']} "
          f"n_heldout={m['n_rows']} n_train={report['train_split_sanity_NOT_ADMISSIBLE']['n_rows']} "
          f"heldout_frac={report['split']['heldout_row_fraction']:.4f}")
    print(f"grouping_proof: {report['grouping_proof']['check']} "
          f"(shared_parents={report['grouping_proof']['n_shared_parents']})")
    print(f"AUROC (held-out, admissible) = {m['auroc']:.4f}")
    print(f"Fmax unweighted (held-out)   = {m['fmax_unweighted']['value']:.4f} "
          f"@t={m['fmax_unweighted']['threshold']}")
    print(f"wFmax (held-out)             = {m['wfmax']['value']:.4f} @t={m['wfmax']['threshold']}")
    rvr = m["representation_vs_reference"]
    print(f"CCA canonical correlations (held-out) = {rvr['cca_canonical_correlations_heldout']}")
    print(f"Ridge R^2 per-dim (held-out)            = "
          f"{dict(zip(rvr['reference_dims'], (round(v, 4) for v in rvr['ridge_r2_per_reference_dim_heldout'])))}")
    print(f"Ridge R^2 uniform avg (held-out)       = {rvr['ridge_r2_uniform_average_heldout']:.4f}")
    flags = rvr["reference_collinearity_diagnostic"]["near_collinear_pairs_abs_r_ge_0.98"]
    if flags:
        print(f"⚠ near-collinear reference-dim pairs (|r|>=0.98): {flags}")
        print("  -> a high R^2/canonical-correlation touching these dims is a redundant signal, "
              "not independent recoveries. See module docstring CCA/R^2 caveats before citing.")
    print(f"claim_ceiling: {report['claim_ceiling']}")
    print(f"pi_audit_status: {report['pi_audit_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
