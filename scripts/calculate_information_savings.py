#!/usr/bin/env python3
"""Deterministic fail-closed information-savings calculator for HydraDG.

Software license: Apache-2.0.

This calculator deliberately separates:
1. byte-level download/storage deduplication,
2. atom/key reuse accounting,
3. theoretical compute/energy-equivalent scenarios.

It does not turn modeled counts into measured bytes, tokenizer tokens, energy, SeedGraph
admission, or HydraDB write/read evidence.
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
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def require_nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return value


def ratio_percent(raw: int, unique: int) -> str:
    if raw <= 0:
        raise ValueError("raw count must be greater than zero")
    if unique > raw:
        raise ValueError("unique count cannot exceed raw count")
    duplicate = raw - unique
    return str(
        (Decimal(100) * Decimal(duplicate) / Decimal(raw)).quantize(
            Decimal("0.000001")
        )
    )


def calculate_lane(lane: dict[str, Any], label: str) -> dict[str, Any]:
    raw = require_nonnegative_int(lane.get("raw"), f"{label}.raw")
    unique = require_nonnegative_int(lane.get("unique"), f"{label}.unique")
    if raw == 0:
        raise ValueError(f"{label}.raw must be > 0")
    if unique > raw:
        raise ValueError(f"{label}.unique cannot exceed raw")
    duplicate = raw - unique
    return {
        "raw": raw,
        "unique": unique,
        "duplicate": duplicate,
        "reuse_percent": ratio_percent(raw, unique),
    }


def calculate_download_bytes(files: list[dict[str, Any]]) -> dict[str, Any]:
    if not files:
        return {
            "state": "NOT_MEASURED",
            "raw_download_bytes": None,
            "unique_content_bytes": None,
            "duplicate_download_bytes": None,
            "dedup_ratio_percent": None,
        }

    sizes_by_hash: dict[str, int] = {}
    raw_bytes = 0
    for index, item in enumerate(files):
        sha = str(item.get("sha256", "")).lower()
        if not HEX64.fullmatch(sha):
            raise ValueError(f"download_files[{index}].sha256 must be 64 lowercase hex")
        size = require_nonnegative_int(
            item.get("size_bytes"), f"download_files[{index}].size_bytes"
        )
        raw_bytes += size
        previous = sizes_by_hash.get(sha)
        if previous is not None and previous != size:
            raise ValueError(
                f"same SHA-256 has conflicting sizes: {sha}: {previous} != {size}"
            )
        sizes_by_hash[sha] = size

    if raw_bytes == 0:
        raise ValueError("download manifest raw byte total must be > 0")
    unique_bytes = sum(sizes_by_hash.values())
    duplicate_bytes = raw_bytes - unique_bytes
    return {
        "state": "MEASURED_FROM_HASHED_BYTE_MANIFEST",
        "raw_download_bytes": raw_bytes,
        "unique_content_bytes": unique_bytes,
        "duplicate_download_bytes": duplicate_bytes,
        "dedup_ratio_percent": str(
            (Decimal(100) * Decimal(duplicate_bytes) / Decimal(raw_bytes)).quantize(
                Decimal("0.000001")
            )
        ),
    }


def calculate_compute_scenarios(
    scenarios: list[dict[str, Any]], combined_duplicate: int
) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        params = require_nonnegative_int(scenario.get("params"), f"scenario[{index}].params")
        flops_per = require_nonnegative_int(
            scenario.get("flops_per_parameter_per_token"),
            f"scenario[{index}].flops_per_parameter_per_token",
        )
        efficiency_raw = scenario.get("efficiency_flops_per_second_per_watt")
        try:
            efficiency = Decimal(str(efficiency_raw))
        except Exception as exc:
            raise ValueError(f"scenario[{index}] efficiency must be numeric") from exc
        if efficiency <= 0:
            raise ValueError(f"scenario[{index}] efficiency must be > 0")

        assumption = Decimal(str(scenario.get("tokens_per_duplicate_atom_assumption")))
        if assumption < 0:
            raise ValueError(f"scenario[{index}] token assumption must be >= 0")
        assumed_delta_tokens_decimal = Decimal(combined_duplicate) * assumption
        if assumed_delta_tokens_decimal != assumed_delta_tokens_decimal.to_integral_value():
            raise ValueError(
                f"scenario[{index}] produces a fractional token count; use an explicit integer-token scenario"
            )
        assumed_delta_tokens = int(assumed_delta_tokens_decimal)
        flops = flops_per * params * assumed_delta_tokens
        energy_equivalent_wh = Decimal(flops) / efficiency / Decimal(3600)

        outputs.append(
            {
                "id": str(scenario.get("id")),
                "assumed_delta_tokens": assumed_delta_tokens,
                "theoretical_flops_avoided": flops,
                "theoretical_energy_equivalent_wh": str(
                    energy_equivalent_wh.quantize(Decimal("0.000001"))
                ),
                "measured_energy_wh": scenario.get("measured_energy_wh"),
                "energy_measurement_state": (
                    "MEASURED_EXTERNAL_INPUT"
                    if scenario.get("measured_energy_wh") is not None
                    else "NOT_MEASURED"
                ),
                "scenario_state": "THEORETICAL_ONLY",
            }
        )
    return outputs


def calculate_receipt(source: dict[str, Any]) -> dict[str, Any]:
    atom_counts = source.get("atom_counts") or {}
    word = calculate_lane(atom_counts.get("word") or {}, "atom_counts.word")
    sentence = calculate_lane(atom_counts.get("sentence") or {}, "atom_counts.sentence")

    combined_raw = word["raw"] + sentence["raw"]
    combined_unique = word["unique"] + sentence["unique"]
    combined_duplicate = combined_raw - combined_unique
    combined = {
        "raw": combined_raw,
        "unique": combined_unique,
        "duplicate": combined_duplicate,
        "reuse_percent": ratio_percent(combined_raw, combined_unique),
    }

    parquet = source.get("canonical_parquet") or {}
    word_bytes = require_nonnegative_int(parquet.get("word_bytes"), "canonical_parquet.word_bytes")
    sentence_bytes = require_nonnegative_int(
        parquet.get("sentence_bytes"), "canonical_parquet.sentence_bytes"
    )

    results = {
        "word": word,
        "sentence": sentence,
        "combined": combined,
        "canonical_parquet": {
            "declared_total_bytes": word_bytes + sentence_bytes,
            "state": parquet.get("state", "DECLARED_NOT_REVERIFIED"),
        },
        "download_byte_savings": calculate_download_bytes(source.get("download_files") or []),
        "compute_scenarios": calculate_compute_scenarios(
            source.get("compute_scenarios") or [], combined_duplicate
        ),
    }

    payload = {
        "schema": "hydradg.information_savings_receipt.v2",
        "source_commit": source.get("source_commit"),
        "input_sha256": sha256_json(source),
        "calculation_contract_sha256": sha256_json(CONTRACT),
        "results": results,
        "invariants": {
            "word_raw_equals_unique_plus_duplicate": word["raw"]
            == word["unique"] + word["duplicate"],
            "sentence_raw_equals_unique_plus_duplicate": sentence["raw"]
            == sentence["unique"] + sentence["duplicate"],
            "combined_raw_equals_unique_plus_duplicate": combined["raw"]
            == combined["unique"] + combined["duplicate"],
            "download_manifest_fail_closed": True,
            "measured_energy_not_fabricated": all(
                item["measured_energy_wh"] is not None
                or item["energy_measurement_state"] == "NOT_MEASURED"
                for item in results["compute_scenarios"]
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
        calculated = calculate_receipt(source)
        rendered = json.dumps(calculated, indent=2, sort_keys=True) + "\n"

        if args.verify:
            if not args.output.exists():
                raise ValueError(f"verification output does not exist: {args.output}")
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
        args.output.write_text(rendered, encoding="utf-8")
        print("INFORMATION_SAVINGS_BUILD=PASS")
        print(f"input_sha256={calculated['input_sha256']}")
        print(f"contract_sha256={calculated['calculation_contract_sha256']}")
        print(f"receipt_sha256={calculated['receipt_sha256']}")
        return 0
    except Exception as exc:
        print("INFORMATION_SAVINGS=FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
