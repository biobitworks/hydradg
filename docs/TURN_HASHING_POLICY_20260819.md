# HydraDG in-turn hashing policy — 2026-08-19

For each substantive project turn, retain separate custody identities for:

```text
human/user input
AI commentary/update messages when substantive
AI final response body
turn custody record
```

## Non-self-referential hashing

The final response body is hashed **without** the appended custody receipt. The custody record then includes that body hash and receives its own SHA-256 identity.

This avoids attempting to hash a string containing its own final digest.

## Suggested canonical record

```json
{
  "schema": "hydradg.turn_custody.v1",
  "user_turn_sha256": "...",
  "commentary_sha256": "...",
  "assistant_body_sha256": "...",
  "parent_turn_record_sha256": "... or null/gap",
  "evidence_class": "...",
  "claim_ceiling": "...",
  "signature_state": "NOT_SIGNED",
  "merkle_state": "NOT_PROJECT_COMMITTED"
}
```

Canonical JSON for the turn record uses sorted keys and separators `(',', ':')` before SHA-256.

## Signature boundary

A turn is `SIGNED` only when an authorized project private key signs the declared turn-record digest and a corresponding signature/public-key verification path exists.

An SHA-256 digest is not a signature.

## Chain gaps

If prior exact turn bytes were not preserved or hashed at emission, record:

```text
PARENT_STATE=CHAIN_GAP
```

Do not invent a predecessor digest.
