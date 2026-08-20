HydraDG Antigravity Low-Token Package
======================================

Files
-----
FINAL_ANTIGRAVITY_PROMPT.txt
  Paste this into Antigravity as the controlling prompt.

LOW_TOKEN_POLICY.json
  Machine-readable routing and custody policy.

prepare_antigravity_packet.py
  Optional deterministic helper. Run on magicstudiobox or on a machine
  with the HydraDG package mounted. It creates one compact JSON packet
  from the bounded Vithia artifacts and computes SHA-256 locally.

Recommended use
---------------
1. Copy prepare_antigravity_packet.py into:
   /Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7/scripts/

2. On magicstudiobox:
   cd /Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7
   python3 scripts/prepare_antigravity_packet.py

3. Give Antigravity FINAL_ANTIGRAVITY_PROMPT.txt.

4. Let Antigravity read the resulting:
   eval/vithia_overnight/VITHIA-OVERNIGHT-01/ANTIGRAVITY_PACKET.json
   plus only the representative receipts explicitly referenced by the
   EVIDENCE_INDEX.

5. Keep private signing keys out of Antigravity prompts and logs.
   Use the approved local signer only.

Important
---------
This package contains no private keys and performs no signing itself.
It does not create a Merkle/MMR commitment. Those operations must use
the project's approved local custody implementation and be evidenced
before SIGNED / MERKLE_COMMITTED claims are made.
