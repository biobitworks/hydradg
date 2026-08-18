# HydraDG custody resume and signing protocol

## 1. Declared discontinuity

A conversation fork occurred during Hack Hydra development and the intended per-turn hash chain was not continuously appended for several substantive turns. HydraDG records that as a `CustodyGap` FCO.

Policy:

- do not invent missing historical turn hashes;
- do not claim an unbroken chain across the gap;
- preserve the last recoverable pre-gap state when available;
- resume with a new explicit anchor;
- bind later source, transformation, code, execution, and submission objects to the resumed graph;
- a later signature does not retroactively make the missing interval contemporaneously signed.

## 2. Turn custody moving forward

For each substantive human/AI development turn, record independently:

- exact human-visible input bytes when available;
- human input SHA-256;
- assistant/output artifact SHA-256 when the exact bytes are available to the recorder;
- model/agent/tool identity and version where known;
- parent/resume anchor;
- evidence class;
- claim ceiling;
- created artifact ids/hashes;
- execution receipts and test results;
- an explicit signature state.

If exact message bytes are unavailable to the execution environment, record the limitation rather than reconstructing them from memory.

## 3. FCO identity

FCO identity is the SHA-256 of canonical JSON for:

```json
{"type":"<TYPE>","payload":{}}
```

with recursively sorted object keys and array order preserved.

HydraDB uses a deterministic numeric address derived from the FCO id for native traversal. That address is not the cryptographic identity. The full `fco_id` and `object_sha256` remain graph properties.

## 4. FCG edges

A custody edge id is SHA-256 over canonical JSON:

```json
{"src":"fco:...","rel":"RELATION","dst":"fco:...","payload":{}}
```

The live files are:

- `custody/live/nodes.jsonl`
- `custody/live/edges.jsonl`

Every edge endpoint must resolve to a known FCO when the root is built.

## 5. Root convention for HydraDG hackathon resume

The resumed Hack Hydra project uses a versioned convention named:

`HYDRADG-FCG-RFC6962-v1`

The builder:

1. validates every FCO and FCG object hash;
2. sorts objects by canonical object id;
3. represents each complete canonical JSON object as a leaf;
4. hashes leaves as `SHA256(0x00 || leaf_bytes)`;
5. hashes internal nodes as `SHA256(0x01 || left || right)`;
6. uses RFC-6962-style recursive tree splitting;
7. includes the author public-key file as a separate leaf when that file is present;
8. writes the computed root and manifest.

This convention is explicitly versioned. It is not asserted to be byte-identical to every earlier FCO publication root convention.

## 6. Signing convention recovered from the prior FCO/FCG package

The keyed pathway remains parallel to the content-address pathway:

1. `PUBLIC_KEY.ed25519.pub` is included as a hashed leaf before the final root is computed.
2. Write the lowercase hexadecimal FCG root with no newline to the signing input.
3. Sign those bytes with the author's Ed25519 private key.
4. Store the signature as `FCG_ROOT.sig`.
5. `FCG_ROOT.sig` is not a root leaf, so signing does not recursively change the object being signed.
6. Verify the signature with `PUBLIC_KEY.ed25519.pub`.
7. Verify the public-key DER SHA-256 fingerprint against a trusted out-of-band anchor before attributing the signature to a named person.

Expected recovered author-key DER fingerprint:

`f496a067808026d45fbbad785bf83c6acd66429c2d257d246cc103c6d7ff460d`

Recovered author private-key location from earlier execution records:

`~/.fco/keys/fcg_signing_ed25519.pem`

That path is documentation only. The private key must never enter Git, the public submission, CI secrets, or an FCO payload.

## 7. Current signing state

Current state in this environment:

- custody gap: `DECLARED_GAP`;
- resumed FCO/FCG nodes/edges: `HASHED`;
- public-key fingerprint reference: present;
- actual author public-key bytes in this execution environment: absent;
- author FCG root signature: `PENDING_PUBLIC_KEY_LEAF_AND_AUTHOR_KEY`;
- ephemeral CI signing test: allowed as a mechanism test only.

An ephemeral CI signature must be labeled:

`EPHEMERAL_CI_KEY_NOT_AUTHOR_IDENTITY`

It proves that the build/sign/verify path executes; it does not authenticate the author.

## 8. Author-host signing command

After the public key is copied into `custody/live/PUBLIC_KEY.ed25519.pub` and the root is rebuilt:

```bash
python3 scripts/build_fcg_root.py
printf '%s' "$(python3 -c 'import json; print(json.load(open("custody/live/manifest.json"))["fcg_root"])')" > /tmp/hydradg_fcg_root.txt
openssl pkeyutl -sign \
  -inkey ~/.fco/keys/fcg_signing_ed25519.pem \
  -rawin \
  -in /tmp/hydradg_fcg_root.txt \
  -out custody/live/FCG_ROOT.sig
openssl pkeyutl -verify \
  -pubin \
  -inkey custody/live/PUBLIC_KEY.ed25519.pub \
  -rawin \
  -in /tmp/hydradg_fcg_root.txt \
  -sigfile custody/live/FCG_ROOT.sig
```

Only after successful verification and fingerprint matching may the manifest signature state be promoted to `AUTHOR_SIGNATURE_VERIFIED`.
