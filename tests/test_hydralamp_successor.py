"""Extended HydraLamp tests — CFMO, MMR, sandbox, context score, SELF_SAFE."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hydralamp.cfmo import CFMOStore
from hydralamp.context_score import score_leaf, ContextScoreFCO
from hydralamp.mmr import MMRAccumulator, leaf_hash, MMR_ALGORITHM_ID
from hydralamp.sandbox import SandboxBoundary, DualWorldRunner, WorldMode
from hydralamp.self_safe import evaluate_self_safe, build_challenge
from hydralamp.crypto import generate_ed25519_keypair, sign_message
from hydralamp.toy_key import public_fcg_key_metadata, CLAIM_CEILING


class TestCFMO(unittest.TestCase):
    def test_append_only_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CFMOStore(Path(tmp) / "cfmo.json")
            v1 = store.append("POISON", {"id": "p1"}, actor_id="POISON_AGENT", event_index=1)
            v2 = store.append("QUARANTINE", {"id": "q1"}, actor_id="VERIFIER", event_index=2)
            self.assertEqual(len(store.versions), 2)
            self.assertTrue(v1["immutable"])
            self.assertEqual(store.versions[0]["state_type"], "POISON")


class TestMMR(unittest.TestCase):
    def test_frozen_leaf_deterministic(self):
        h1 = leaf_hash(1, "abc", "cfmo:v001")
        h2 = leaf_hash(1, "abc", "cfmo:v001")
        self.assertEqual(h1, h2)

    def test_mmr_commit_receipt(self):
        mmr = MMRAccumulator()
        mmr.append(1, "hash1", "cfmo:v001")
        mmr.append(2, "hash2", "cfmo:v002")
        receipt = mmr.verification_receipt()
        self.assertEqual(receipt["algorithm_id"], MMR_ALGORITHM_ID)
        self.assertTrue(receipt["committed"])
        self.assertEqual(receipt["leaf_count"], 2)
        self.assertRegex(receipt["root_sha256"], r"^[0-9a-f]{64}$")


class TestContextScore(unittest.TestCase):
    def test_never_authorizes(self):
        ctx = score_leaf("fco:test", event_hash="h", fcg_root="r", msm_state="AUTHENTICATED", actor_id="A")
        d = ctx.to_dict()
        self.assertFalse(d["authorizes_access"])
        self.assertTrue(d["routing_only"])


class TestSandbox(unittest.TestCase):
    def test_not_trust_root(self):
        b = SandboxBoundary()
        self.assertFalse(b.is_trust_root)
        ok, _ = b.check_operation("direct_canonical_write")
        self.assertFalse(ok)


class TestToyKey(unittest.TestCase):
    def test_claim_ceiling(self):
        meta = public_fcg_key_metadata("RESEARCH_AGENT")
        self.assertEqual(meta["claim_ceiling"], CLAIM_CEILING)
        self.assertEqual(meta["key_mode"], "TOY_DISTRIBUTED_PRIVATE_KEY")


class TestSelfSafe(unittest.TestCase):
    def test_requires_pop_not_score(self):
        kp = generate_ed25519_keypair()
        challenge = build_challenge("A", "n1")
        sig = sign_message(kp.private_key, challenge)
        v = evaluate_self_safe(
            actor_id="A", private_key=kp.private_key, public_key=kp.public_key,
            challenge=challenge, signature=sig, capability_valid=False,
            actor_revoked=False, context_score=99.0,
        )
        self.assertFalse(v.self_safe)
        self.assertTrue(v.context_score_assigned)


if __name__ == "__main__":
    unittest.main()
