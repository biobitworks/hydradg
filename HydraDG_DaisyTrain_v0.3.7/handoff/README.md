# Antigravity handoff directory

Antigravity should maintain:
- `LAST_STATUS.md`
- `EVIDENCE_INDEX.json`
- `BACKEND_MATRIX.json`
- `NEXT_COMMAND.txt`
- `LAST_ERROR_FOR_CHAT.txt` only when there is a current failure.

These are intentionally small so they can be uploaded to ChatGPT or committed to a private Git branch without moving full logs/checkpoints.

Antigravity must also report:
- current Agent FCO IDs;
- current Model FCO IDs;
- live Turn count;
- live KnowledgeUpdate count;
- `custody/live/manifest.json` SHA-256;
- HydraDB ingestion state separately from local staging state.
