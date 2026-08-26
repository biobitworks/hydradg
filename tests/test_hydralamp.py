"""HydraLamp unit and invariant tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hydralamp.access import AccessLevel, Capability, evaluate_access
from hydralamp.crypto import (
    SECURITY_CLAIM_ELIGIBILITY_TEST,
    canonical_json,
    decrypt_payload,
    encrypt_payload,
    generate_ed25519_keypair,
    generate_x25519_keypair,
    sign_message,
    verify_signature,
)
from hydralamp.gateway import HydraLampGateway


class TestCrypto(unittest.TestCase):
    def test_ed25519_sign_verify(self):
        kp = generate_ed25519_keypair()
        msg = b"test message"
        sig = sign_message(kp.private_key, msg)
        self.assertTrue(verify_signature(kp.public_key, msg, sig))

    def test_aes_gcm_roundtrip(self):
        sender = generate_x25519_keypair()
        recipient = generate_x25519_keypair()
        plaintext = b"secret fixture"
        aad = b"obj:test"
        env = encrypt_payload(recipient.public_key, sender.private_key, plaintext, aad)
        pt = decrypt_payload(recipient.private_key, sender.public_key, env, aad)
        self.assertEqual(pt, plaintext)

    def test_test_vector_deterministic(self):
        kp1 = generate_ed25519_keypair(b"TEST-ONLY-HUMAN-CONTROLLER-KEY!!")
        kp2 = generate_ed25519_keypair(b"TEST-ONLY-HUMAN-CONTROLLER-KEY!!")
        self.assertEqual(kp1.public_key_b64, kp2.public_key_b64)


class TestAccess(unittest.TestCase):
    def test_no_capability_denies_private(self):
        d = evaluate_access(None, AccessLevel.PRIVATE_PAYLOAD, "POISON_AGENT", False, 1, "root")
        self.assertFalse(d.allowed)
        self.assertTrue(d.connect)

    def test_expired_capability(self):
        cap = Capability("c1", "A", "*", (AccessLevel.PROMOTE,), "root", "n1", 5)
        d = evaluate_access(cap, AccessLevel.PROMOTE, "A", False, 10, "root")
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "CAPABILITY_EXPIRED")


class TestGateway(unittest.TestCase):
    def test_world_leak_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gw = HydraLampGateway.bootstrap(root, mode="TEST_VECTOR_REPLAY")
            msg = b"handshake:POISON_AGENT"
            sig = sign_message(gw.broker.ed25519("POISON_AGENT").private_key, msg)
            gw.signed_handshake("POISON_AGENT", sig, msg)
            gw.read_object("POISON_AGENT", "obj:private:payload", AccessLevel.PRIVATE_PAYLOAD)
            gw.poison_attempt_direct_write("POISON_AGENT")
            self.assertEqual(gw.unauthorized_plaintext_disclosures, 0)
            self.assertEqual(gw.unauthorized_canonical_writes, 0)

    def test_test_vector_mode_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            gw = HydraLampGateway.bootstrap(Path(tmp), mode="TEST_VECTOR_REPLAY")
            gw.save()
            import json
            runtime = json.loads((Path(tmp) / "HYDRALAMP_RUNTIME.json").read_text())
            self.assertEqual(runtime["security_claim_eligibility"], SECURITY_CLAIM_ELIGIBILITY_TEST)


if __name__ == "__main__":
    unittest.main()
