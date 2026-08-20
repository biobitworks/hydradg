#!/usr/bin/env python3
"""Deterministic fail-closed information-savings calculator for HydraDG.

SPDX-License-Identifier: Apache-2.0

Separates byte-level deduplication, atom/key reuse accounting, and theoretical
compute/energy-equivalent scenarios. It does not convert modeled counts into
measured bytes, tokenizer tokens, model execution, or electrical energy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

getcontext().prec = 50
HEX64 = re.compile(r"^[0-9a-f]{64}$")

CONTRACT: dict[str, Any] = {
    "schema": "hydradg.information_savings_calculation_contract.v1",
    "integer_arithmetic": "all count and byte arithmetic uses nonnegative integers",
    "ratio_formula": "100*(raw-unique)/raw using Decimal; raw must be > 0 and unique <= raw",
    "combined_formula": "sum lanes independently before computing combined duplicate count and ratio",
    "byte_formula": "raw_download_bytes=sum(file size); unique_content_bytes=sum one size per distinct sha256); same sha256 with conflicting size => FAIL",
    "byte_no_manifest_state": "NOT_MEASURED",
    "compute_formula": "theoretical_flops_avoided=flops_per_parameter_per_token*params*assumed_delta_tokens",
    "energy_formula": "theoretical_energy_equivalent_wh=theoretical_flops_avoided/efficiency_flops_per_second_per_watt/3600",
    "energy_state": "THEORETICAL_EQUIVALENT_ONLY; measured_energy_wh remains null unless measured",
    "digest_formula": "sha256(canonical sorted UTF-8 JSON with compact separators)",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def require_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return value


def ratio(raw: int, unique: int) -> str:
    if raw <= 0 or unique > raw:
        raise ValueError("raw must be > 0 and unique must not exceed raw")
    return str((Decimal(100) * Decimal(raw - unique) / Decimal(raw)).quantize(Decimal("0.000001")))


def lane(source: dict[str, Any], label: str) -> dict[str, Any]:
    raw = require_int(source.get("raw"), f"{label}.raw")
    unique = require_int(source.get("unique"), f"{label}.unique")
    if raw <= 0 or unique > raw:
        raise ValueError(f"invalid {label} counts")
    return {"raw": raw, "unique": unique, "duplicate": raw - unique, "reuse_percent": ratio(raw, unique)}


def byte_savings(files: list[dict[str, Any]]) -> dict[str, Any]:
    if not files:
        return {
            "state": "NOT_MEASURED",
            "raw_download_bytes": None,
            "unique_content_bytes": None,
            "duplicate_download_bytes": None,
            "dedup_ratio_percent": None,
        }
    raw = 0
    sizes_by_hash: dict[str, int] = {}
    for index, item in enumerate(files):
        sha = str(item.get("sha256", "")).lower()
        if not HEX64.fullmatch(sha):
            raise ValueError(f"download_files[{index}].sha256 must be 64 lowercase hex")
        size = require_int(item.get("size_bytes"), f"download_files[{index}].size_bytes")
        raw += size
        previous = sizes_by_hash.get(sha)
        if previous is not None and previous != size:
            raise ValueError(f"same SHA-256 has conflicting sizes: {sha}: {previous} != {size}")
        sizes_by_hash[sha] = size
    if raw <= 0:
        raise ValueError("download manifest raw byte total must be > 0")
    unique = sum(sizes_by_hash.values())
    duplicate = raw - unique
    return {
        "state": "MEASURED_FROM_HASHED_BYTE_MANIFEST",
        "raw_download_bytes": raw,
        "unique_content_bytes": unique,
        "duplicate_download_bytes": duplicate,
        "dedup_ratio_percent": str((Decimal(100) * Decimal(duplicate) / Decimal(raw)).quantize(Decimal("0.000001"))),
    }


def compute_scenarios(scenarios: list[dict[str, Any]], duplicates: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, item in enumerate(scenarios):
        params = require_int(item.get("params"), f"scenario[{index}].params")
        flops_per = require_int(item.get("flops_per_parameter_per_token"), f"scenario[{index}].flops_per_parameter_per_token")
        token_factor = Decimal(str(item.get("tokens_per_duplicate_atom_assumption")))
        assumed_decimal = Decimal(duplicates) * token_factor
        if assumed_decimal < 0 or assumed_decimal != assumed_decimal.to_integral_value():
            raise ValueError(f"scenario[{index}] must produce a nonnegative integer token count")
        assumed_tokens = int(assumed_decimal)
        efficiency = Decimal(str(item.get("efficiency_flops_per_second_per_watt")))
        if efficiency <= 0:
            raise ValueError(f"scenario[{index}] efficiency must be > 0")
        flops = flops_per * params * assumed_tokens
        wh = Decimal(flops) / efficiency / Decimal(3600)
        out.append({
            "id": str(item.get("id")),
            "assumed_delta_tokens": assumed_tokens,
            "theoretical_flops_avoided": flops,
            "theoretical_energy_equivalent_wh": str(wh.quantize(Decimal("0.000001"))),
            "measured_energy_wh": item.get("measured_energy_wh"),
            "energy_measurement_state": "MEASURED_EXTERNAL_INPUT" if item.get("measured_energy_wh") is not None else "NOT_MEASURED",
            "scenario_state": "THEORETICAL_ONLY",
        })
    return out


def calculate(source: dict[str, Any]) -> dict[str, Any]:
    counts = source.get("atom_counts") or {}
    word = lane(counts.get("word") or {}, "atom_counts.word")
    sentence = lane(counts.get("sentence") or {}, "atom_counts.sentence")
    combined_raw = word["raw"] + sentence["raw"]
    combined_unique = word["unique"] + sentence["unique"]
    combined = {
        "raw": combined_raw,
        "unique": combined_unique,
        "duplicate": combined_raw - combined_unique,
        "reuse_percent": ratio(combined_raw, combined_unique),
    }
    parquet = source.get("canonical_parquet") or {}
    word_bytes = require_int(parquet.get("word_bytes"), "canonical_parquet.word_bytes")
    sentence_bytes = require_int(parquet.get("sentence_bytes"), "canonical_parquet.sentence_bytes")
    results = {
        "word": word,
        "sentence": sentence,
        "combined": combined,
        "canonical_parquet": {
            "declared_total_bytes": word_bytes + sentence_bytes,
            "state": parquet.get("state", "DECLARED_NOT_REVERIFIED"),
        },
        "download_byte_savings": byte_savings(source.get("download_files") or []),
        "compute_scenarios": compute_scenarios(source.get("compute_scenarios") or [], combined["duplicate"]),
    }
    payload = {
        "schema": "hydradg.information_savings_receipt.v2",
        "source_commit": source.get("source_commit"),
        "input_sha256": sha256_json(source),
        "calculation_contract_sha256": sha256_json(CONTRACT),
        "results": results,
        "invariants": {
            "word_raw_equals_unique_plus_duplicate": word["raw"] == word["unique"] + word["duplicate"],
            "sentence_raw_equals_unique_plus_duplicate": sentence["raw"] == sentence["unique"] + sentence["duplicate"],
            "combined_raw_equals_unique_plus_duplicate": combined["raw"] == combined["unique"] + combined["duplicate"],
            "download_manifest_fail_closed": True,
            "measured_energy_not_fabricated": all(
                x["measured_energy_wh"] is not None or x["energy_measurement_state"] == "NOT_MEASURED"
                for x in results["compute_scenarios"]
            ),
        },
        "status": "PASS_WITH_NOT_MEASURED_LANES",
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
        "license": source.get("license", "CC-BY-NC-ND-4.0"),
        "claim_ceiling": source.get("claim_ceiling"),
    }
    return {**payload, "receipt_sha256": sha256_json(payload)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        source = json.loads(args.input.read_text(encoding="utf-8"))
        calculated = calculate(source)
        if args.verify:
            existing = json.loads(args.output.read_text(encoding="utf-8"))
            if existing != calculated:
                print("INFORMATION_SAVINGS_VERIFY=FAIL", file=sys.stderr)
                print(f"expected_receipt_sha256={calculated['receipt_sha256']}", file=sys.stderr)
                print(f"observed_receipt_sha256={existing.get('receipt_sha256')}", file=sys.stderr)
                return 1
            print("INFORMATION_SAVINGS_VERIFY=PASS")
            print(f"input_sha256={calculated['input_sha256']}")
            print(f"contract_sha256={calculated['calculation_contract_sha256']}")
            print(f"receipt_sha256={calculated['receipt_sha256']}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(calculated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("INFORMATION_SAVINGS_BUILD=PASS")
        print(f"receipt_sha256={calculated['receipt_sha256']}")
        return 0
    except Exception as exc:
        print("INFORMATION_SAVINGS=FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
