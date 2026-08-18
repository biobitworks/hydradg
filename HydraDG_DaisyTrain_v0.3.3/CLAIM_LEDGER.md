# Evidence / claim ledger

| Object / result | Evidence class | Current ceiling |
|---|---|---|
| ECA-EXT80 design in this package | generated method/code | PROPOSED_UNTIL_EXECUTED |
| ECA-EXT80 Modal result | none at package creation | NOT_YET_EXECUTED |
| Historical FCO ECA prereg/results | prior project artifact | SOURCE_RECOVERY_REQUIRED_FOR_BYTE_REPLAY |
| Xeno evaluator local->Modal wrapper | generated method/code | PROPOSED_UNTIL_EXECUTED |
| Xeno historical reproduction | dependency gate not yet passed in this package | NOT_ESTABLISHED |
| Existing Vithia/Pythia Modal evidence | prior executed user evidence | IMPORT_REQUIRED; DO_NOT_RERUN_FOR_PACKAGING |
| FCO/FCG JSONL normalizer | generated deterministic transform | IMPLEMENTED; OUTPUT_PENDING_INPUTS |
| HydraDB integrated app | adapter intentionally absent until API pin | NOT_YET_IMPLEMENTED_IN_THIS_PACKAGE |
| LongMemEval smoke80 | selection code present | NOT_YET_EXECUTED |
| LongMemEval full500 | official benchmark planned | NOT_YET_EXECUTED |
| MMR root | no operation in package | NOT_MERKLE_COMMITTED |
| cryptographic signature | no signing in package | NOT_SIGNED |
| independent verification | no independent route in package | NOT_INDEPENDENTLY_VERIFIED |

## Promotion rule

A downstream claim may not exceed the weakest load-bearing dependency.
If a historical byte/object cannot be recovered, downgrade to a new same-assets replay or new extension;
do not silently substitute and retain the historical-reproduction label.
