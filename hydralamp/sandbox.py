"""Sandbox boundary — defense-in-depth wrapper; capability remains trust root."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from hydralamp.gateway import HydraLampGateway


class WorldMode(str, Enum):
    SANDBOX = "SANDBOX"
    OPEN_WORLD = "OPEN_WORLD"


@dataclass
class SandboxBoundary:
    """Isolated execution envelope — blocks direct canonical write and raw FS escape."""

    blocked_operations: frozenset[str] = frozenset({
        "direct_canonical_write",
        "raw_filesystem_escape",
        "cross_actor_key_exfil",
    })
    allowed_network: bool = False
    defense_in_depth: bool = True
    is_trust_root: bool = False  # invariant

    def check_operation(self, op: str) -> tuple[bool, str]:
        if op in self.blocked_operations:
            return False, f"SANDBOX_BLOCKED:{op}"
        return True, "SANDBOX_ALLOWED"


@dataclass
class DualWorldResult:
    fixture_id: str
    perturbation_id: str
    sandbox: dict[str, Any]
    open_world: dict[str, Any]
    sandbox_extra_denials: int = 0
    open_world_false_denials: int = 0


@dataclass
class DualWorldRunner:
    boundary: SandboxBoundary = field(default_factory=SandboxBoundary)
    false_denials_sandbox: list[dict[str, Any]] = field(default_factory=list)
    false_denials_open: list[dict[str, Any]] = field(default_factory=list)

    def run_adversarial_fixture(
        self,
        gw: HydraLampGateway,
        *,
        fixture_id: str,
        perturbation_id: str,
        action: Callable[[HydraLampGateway, WorldMode], dict[str, Any]],
    ) -> DualWorldResult:
        sandbox_out = self._run_in_world(gw, WorldMode.SANDBOX, action)
        open_out = self._run_in_world(gw, WorldMode.OPEN_WORLD, action)
        return DualWorldResult(
            fixture_id=fixture_id,
            perturbation_id=perturbation_id,
            sandbox=sandbox_out,
            open_world=open_out,
            sandbox_extra_denials=sandbox_out.get("extra_denials", 0),
            open_world_false_denials=open_out.get("false_denials", 0),
        )

    def _run_in_world(
        self,
        gw: HydraLampGateway,
        mode: WorldMode,
        action: Callable[[HydraLampGateway, WorldMode], dict[str, Any]],
    ) -> dict[str, Any]:
        disclosures_before = gw.unauthorized_plaintext_disclosures
        writes_before = gw.unauthorized_canonical_writes
        result = action(gw, mode)
        if mode == WorldMode.SANDBOX:
            for op in ("direct_canonical_write", "raw_filesystem_escape"):
                ok, reason = self.boundary.check_operation(op)
                if not ok and result.get("attempted_op") == op:
                    result["sandbox_blocked"] = True
                    result["sandbox_reason"] = reason
        result["world_mode"] = mode.value
        result["unauthorized_plaintext_delta"] = gw.unauthorized_plaintext_disclosures - disclosures_before
        result["unauthorized_writes_delta"] = gw.unauthorized_canonical_writes - writes_before
        result["defense_in_depth"] = self.boundary.defense_in_depth
        result["trust_root"] = "SIGNED_CAPABILITY_NOT_SANDBOX"
        return result
