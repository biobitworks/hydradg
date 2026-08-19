# Toy DRM-Free Package Seal v1

## Purpose

This package contains a deliberately non-secret Ed25519 demonstration key pair.

The private key is intentionally distributed in the FCO/FCG demo objects. This is the
DRM-free/reproducible demonstration lane requested for the HydraDG package.

## Critical security semantics

Because the private key is public:
- anyone can reproduce or forge a signature made by this toy key;
- the toy signature establishes reproducible mechanics only;
- it does NOT establish author identity, authenticity, exclusivity, authorization, DRM,
  tamper resistance against an attacker, or production cryptographic trust.

Claim ceiling:

`TOY_DRM_FREE_SIGNATURE_MECHANISM_ONLY_NO_AUTHENTICITY`

The real HydraDG project Ed25519 private key remains external and secret. Its state is
separate:

`PENDING_EXTERNAL_PRIVATE_KEY_OPERATION`

## Distribution model

The toy key is:
1. stored in `ToyKeyDisclosureFCO`;
2. referenced by every sealed ArtifactFCO;
3. repeated in the demo ArtifactFCO payloads as `toy_private_key_b64` to make the
   deliberately public/private-key design mechanically explicit;
4. connected by FCG edges to the package seal and artifact identities.

Do NOT use this toy private key for any production release, account, credential, or real
trust decision.
