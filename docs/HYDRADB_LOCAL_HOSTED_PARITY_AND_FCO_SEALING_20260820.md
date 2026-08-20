# HydraDB local → hosted parity and FCO/FCG sealing

Date: 2026-08-20

## Scope

HydraDG treats the canonical FCO/FCG as the scientific/custody source of truth. Local self-hosted HydraDB and hosted HydraDB are queryable projections of that same canonical state.

Moving a canonical FCG from local HydraDB to hosted HydraDB must therefore be evaluated in two independent lanes:

1. **Projection parity** — the canonical object/edge identities and backend-independent context metrics should remain unchanged.
2. **Service behavior delta** — indexing, graph hydration, ranking, latency, retrieval and hosted query behavior may differ and must be measured rather than normalized away.

A backend move is not evidence of a scientific state change by itself.

## Canonical parity contract

Freeze the local source before migration:

- canonical FCO IDs
- canonical FCG edge tuples
- canonical FCG/source root(s)
- scorer/config root(s)
- reference context distribution
- G* and ΔG* inputs
- Cloud Drift/JSD inputs
- retrieval evaluation inputs

Project the same graph to hosted HydraDB using v2 `database` / `collection` scoping and deterministic BYOG where relations are already known.

Expected parity assertions for a pure projection:

- canonical FCO ID set delta = 0
- canonical FCG edge tuple delta = 0
- source/root delta = 0
- ΔG* local→hosted = 0 when computed from the same canonical state
- Cloud Drift local→hosted = 0 when computed from the same canonical state

Do not compare backend-generated chunk IDs, entity IDs, timestamps, ranking order or storage serialization as canonical identity. HydraDB may normalize names, create backend IDs, link relations to chunks and return ranked relation responses.

## Service delta contract

After projection parity passes, run the same preregistered query/evaluation packet against both backends.

Record separately:

- local vs hosted Hit@K
- local vs hosted Recall@K
- local vs hosted returned context/path membership
- latency delta
- abstention/error delta
- graph-context path delta
- indexing/readiness state

A non-zero service delta is retained as new evidence. It must not rewrite the canonical FCO/FCG or retroactively alter the local result.

## HydraDB v2 scoping

Use:

- `database` as the primary customer/environment boundary
- `collection` as the project/workspace/user partition inside that database

New hosted configuration uses:

- `HYDRA_DB_API_KEY`
- `HYDRADB_DATABASE`
- `HYDRADB_COLLECTION`
- `HYDRADB_API_URL=https://api.hydradb.com`

Legacy tenant/sub-tenant environment variables may be read only as compatibility aliases.

## Public/private FCO model

HydraDB tenancy and FCO confidentiality are independent layers.

A private FCO can expose a public/researchable envelope while sealing the sensitive payload.

### Public/researchable envelope

May include, according to policy:

- canonical FCO identifier
- object type
- parent/source identifiers
- coarse evidence class
- claim ceiling
- graph relation type or a coarsened relation class
- ciphertext hash
- sealing algorithm/version
- authorized-key-set identifier
- non-sensitive labels approved for research
- optional keyed/blinded feature tokens

The public envelope is sufficient for graph topology, custody, counts, drift calculations over approved distributions and some token-level classification without plaintext disclosure.

### Sealed private payload

Contains sensitive plaintext or high-risk metadata encrypted using envelope encryption.

Recommended pattern:

1. Generate a random symmetric content-encryption key per FCO (or per intentionally shared sealing group).
2. Encrypt the payload with an authenticated cipher such as AES-GCM or ChaCha20-Poly1305.
3. Wrap the content key separately to each authorized recipient/public key using an appropriate public-key encryption/KEM construction.
4. Store only ciphertext, nonce/algorithm metadata, wrapped keys and hashes in the portable FCO envelope.
5. Keep decryption private keys outside HydraDB and outside public FCO/FCG artifacts.

A whole FCG snapshot can also be sealed, but per-FCO sealing supports finer selective disclosure and key rotation.

## Classification and research on tokens

Hashing alone is not encryption. Raw hashes of low-entropy private values may be guessable.

For equality/grouping research on protected values, use a keyed token/blind index such as an HMAC over a canonical feature under a customer-controlled derivation key. This permits stable within-key comparisons without exposing the original value.

Important boundaries:

- HMAC/blind tokens support equality/grouping under the same key; they do not reveal plaintext semantics by themselves.
- Embeddings are derived data and must not automatically be treated as anonymous or safe to publish.
- Content-level classification that requires semantics should occur inside an authorized decrypting environment or use an explicitly approved privacy-preserving derived feature set.
- Cross-customer token comparability should be disabled by default by using distinct customer derivation keys.

## Signing vs sealing

These are different operations:

- **Hashing**: identifies bytes/canonical objects.
- **Signing**: authenticates a hash/object with a signing private key and is verifiable with the corresponding public key.
- **Sealing/encryption**: protects confidentiality; recipients decrypt with authorized private key material.

The project must never label a hash as a signature.

Recommended object state fields:

- `hash_state`
- `signature_state`
- `encryption_state`
- `key_scope_id`
- `payload_visibility`
- `token_visibility`
- `claim_ceiling`

## Judge-facing local → hosted demonstration

Show two panels for the same canonical FCG root:

### Custody parity

Local HydraDB → hosted HydraDB

- FCO set: SAME / DIFFERENT
- FCG edge set: SAME / DIFFERENT
- canonical root: SAME / DIFFERENT
- ΔG* projection delta: expected 0
- Cloud Drift projection delta: expected 0

### Service behavior

Local query → hosted query

- Hit@K delta
- Recall@K delta
- graph-context path delta
- latency delta
- indexing/backend state

This makes infrastructure drift visible without confusing infrastructure with scientific truth.

## Claim ceilings

Until executed:

- local→hosted projection parity = NOT_ESTABLISHED
- hosted query equivalence = NOT_ESTABLISHED
- encryption implementation = DESIGN_ONLY unless actual encrypt/decrypt tests execute
- signature = NOT_SIGNED unless an authorized signing key actually signs the canonical object/root
- Merkle/MMR = NOT_MERKLE_COMMITTED unless actually committed
