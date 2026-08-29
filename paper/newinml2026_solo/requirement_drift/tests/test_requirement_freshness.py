#!/usr/bin/env python3
"""Regression test: requirement freshness and supersession."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def reconcile(old_observations: list[dict], new_observation: dict) -> dict:
    """Preserve old values, detect conflict, mark supersession candidate."""
    active = [o for o in old_observations if o.get("state") == "ACTIVE"]
    conflicts = []
    for obs in active:
        if obs.get("value") != new_observation.get("value"):
            conflicts.append({"old": obs["requirement_id"], "new": new_observation["requirement_id"]})

    state = "ACTIVE" if not conflicts else "CONFLICT_REQUIRES_RECONCILIATION"
    return {
        "state": state,
        "preserved_old": old_observations,
        "new_observation": new_observation,
        "conflicts": conflicts,
    }


def human_reconcile(reconciliation: dict, decision: dict) -> dict:
    """Human selects active requirement; old retained, not deleted."""
    return {
        "state": "RECONCILED",
        "retained_history": reconciliation["preserved_old"],
        "active_requirement": decision["active_requirement_id"],
        "superseded": decision.get("superseded_ids", []),
        "decision_receipt": decision,
    }


def test_old_only_active() -> None:
    old = [{"requirement_id": "DERIVED-0859", "value": "2026-08-29T08:59:00Z", "state": "ACTIVE"}]
    assert reconcile(old, {"requirement_id": "X", "value": "2026-08-29T08:59:00Z"})["state"] == "ACTIVE"


def test_new_source_conflict() -> None:
    old = [{"requirement_id": "DERIVED-0859", "value": "2026-08-29T08:59:00Z", "state": "ACTIVE"}]
    new = {"requirement_id": "REQ-OPENREVIEW", "value": "2026-08-30T07:59:00Z"}
    result = reconcile(old, new)
    assert result["state"] == "CONFLICT_REQUIRES_RECONCILIATION"
    assert len(result["conflicts"]) == 1


def test_human_reconcile_preserves_old() -> None:
    old = [{"requirement_id": "DERIVED-0859", "value": "2026-08-29T08:59:00Z", "state": "ACTIVE"}]
    new = {"requirement_id": "REQ-OPENREVIEW", "value": "2026-08-30T07:59:00Z"}
    rec = reconcile(old, new)
    final = human_reconcile(
        rec,
        {
            "active_requirement_id": "REQ-OPENREVIEW",
            "superseded_ids": ["DERIVED-0859"],
            "reason": "STALE_SOURCE_INPUT",
        },
    )
    assert final["state"] == "RECONCILED"
    assert len(final["retained_history"]) == 1
    assert "DERIVED-0859" in final["superseded"]


def main() -> int:
    test_old_only_active()
    test_new_source_conflict()
    test_human_reconcile_preserves_old()
    print(json.dumps({"REQUIREMENT_FRESHNESS_REGRESSION": "PASS"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
