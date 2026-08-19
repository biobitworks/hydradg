# Status label rule — 2026-08-19

Public status labels use these semantics:

- `PASS` — corresponding execution gate actually ran and passed, with evidence available.
- `EXECUTED · NEGATIVE/NEUTRAL` — execution completed but did not support the directional alternative.
- `IMPLEMENTED` — code exists; execution state is separate.
- `DOWNLOADED · HASHED` — source bytes/revision identity retained; benchmark result not implied.
- `PENDING` — required evidence operation not completed.
- `BLOCKED` — execution attempted or external gate prevents completion; cause and evidence retained.

Do not collapse these states into generic green/red UI.
