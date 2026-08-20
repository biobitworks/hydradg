# First executed Modal result — quick T4/T4 pair

Source log SHA-256: `f0ba7483223cb2e6d4152c183eb97338ea5931f00bbe5c82ba611296a2e1d49e`

Two completed quick runs are visible in the supplied log: `t4_a` and `t4_b`.
They report different Tesla T4 GPU UUIDs but the same canonical final model-state hash:

`d6c01a3315276a0869e88552c192954b1bdb17cd23a0882845a32b28c12c86f7`

Their raw checkpoint-file SHA-256 values differ.

**Bounded interpretation:** under the observed quick fixture, two fresh Modal T4 executions
on different reported physical GPU UUIDs reproduced the same canonical final model state.
This does not yet establish cross-SKU, cross-platform, full-run, or all-step equality.

The differing raw checkpoint hashes with matching canonical state hashes demonstrate why
FCO/FCG separates file/artifact identity from canonical model-state identity.

After the active quick matrix completes, download the receipts and run:

```bash
python scripts/analyze_modal_receipts.py modal_runs_v3/runs/*.receipt.json \
  --out eval/modal_quick_full_analysis.json \
  --seedgraph-out seedgraph/modal_quick
```
