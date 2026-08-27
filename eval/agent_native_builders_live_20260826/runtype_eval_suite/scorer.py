#!/usr/bin/env python3
"""Deterministic HydraDG grade scorer for ANB Runtype product eval V1.

Evidence class when executed: DETERMINISTIC_TOOL_OUTPUT
Does not establish scientific claim promotion by itself.
No secrets. No network. Pure schema/key/quarantine checks.
"""
from __future__ import annotations

import json
import sys
from typing import Any


REQUIRED_KEYS = ("claim_class", "claim_ceiling")
FORBIDDEN_SUBSTRINGS = (
    "sk-",
    "api_key",
    "Bearer ",
    "EVAL_ONLY",
)


def score_case(case: dict[str, Any], model_output: str | None) -> dict[str, Any]:
    result = {
        "case_id": case.get("case_id"),
        "valid_json": False,
        "expected_keys_present": False,
        "nonempty_response": False,
        "forbidden_token_absent": True,
        "hydradg_deterministic_grade": 0.0,
        "error_class": None,
    }
    if model_output is None or not str(model_output).strip():
        result["error_class"] = "MISSING_OUTPUT"
        return result
    text = str(model_output)
    result["nonempty_response"] = True
    lower = text.lower()
    for token in FORBIDDEN_SUBSTRINGS:
        if token.lower() in lower:
            result["forbidden_token_absent"] = False
            result["error_class"] = "FORBIDDEN_TOKEN"
            return result
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        result["error_class"] = "INVALID_JSON"
        return result
    result["valid_json"] = True
    if not isinstance(payload, dict):
        result["error_class"] = "JSON_NOT_OBJECT"
        return result
    keys_ok = all(k in payload and payload[k] not in (None, "") for k in REQUIRED_KEYS)
    result["expected_keys_present"] = keys_ok
    if not keys_ok:
        result["error_class"] = "MISSING_EXPECTED_KEYS"
        return result
    # Grade: equal weight on the three deterministic checks.
    grade = 0.0
    grade += 1.0 / 3.0  # valid_json
    grade += 1.0 / 3.0  # expected_keys_present
    grade += 1.0 / 3.0  # nonempty_response
    if not result["forbidden_token_absent"]:
        grade = 0.0
    result["hydradg_deterministic_grade"] = round(grade, 6)
    return result


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <case.json> <model_output.txt>", file=sys.stderr)
        return 2
    case = json.loads(open(argv[1], encoding="utf-8").read())
    output = open(argv[2], encoding="utf-8").read()
    print(json.dumps(score_case(case, output), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
