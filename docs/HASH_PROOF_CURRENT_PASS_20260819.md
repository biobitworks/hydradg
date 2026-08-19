# Hash proof for current FCG/website pass — 2026-08-19

The exact UTF-8 payloads sent to GitHub for two documentation artifacts were independently SHA-256 hashed in the active assistant runtime before this record was written.

```text
docs/WHY_FCG_UPDATED_20260819.md
bytes=959
sha256=7735f1198ac5834aca6312de719a9d0ca666bd60816d5560aeebd13968ffc05b

docs/PROJECT_FCG_CHANGELOG_20260819.json
bytes=1327
sha256=886731d5fb0ae6a05de307a102cef1207b032fc945d298c91fcebe8f4ab5a719
```

Evidence class:

```text
RECOMPUTED_SHA256_OF_EXACT_UTF8_WRITE_PAYLOAD
```

This establishes the digest of the exact payload supplied to the GitHub write operation. A repository re-fetch/local clone followed by `shasum -a 256` is the second check used to establish that the retained repository bytes are identical to the write payload.

It is not a signature and does not establish correctness.
