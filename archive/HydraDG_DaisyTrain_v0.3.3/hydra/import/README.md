# Hydra import staging

`build_fco_fcg_import.py` writes:
- `nodes.jsonl`
- `edges.jsonl`
- `manifest.json`

These are API-neutral staging objects. Pin the actual HydraDB repository/API in
`config/hydradb_pin.json` before implementing the live adapter.
