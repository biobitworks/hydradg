# Pro ↔ Studio Full Rebuild Sync

**Purpose:** Keep `magicPRObox` able to rebuild and review all citations, experiments, lab notebooks, and atom sources **without Studio running**, using GitHub + local JSON/JSONL mirrors.

**Bundle root:** `.pro-local-rebuild/` (gitignored; local-only)  
**Refresh:** `bash scripts/sync_pro_studio_full_rebuild.sh`

---

## Architecture (three layers)

| Layer | Authority | Pro-local access |
| --- | --- | --- |
| **Git / GitHub** | Code, prereg manifests, compact eval JSON, `publication.atomic.json`, FCG snapshots | `git pull origin main` per repo |
| **JSON rebuild bundle** | Citations ingest, experiment receipts, atom store, datasets | `.pro-local-rebuild/` via rsync from Studio |
| **Live DBs** | Studio OrbStack (Overwatch Arango, SeedGraph Neo4j) | SSH/tunnel only — **not copied to Pro** |

GitHub rebuilds the **governed skeleton**. The bundle rebuilds **bytes**. Live DBs are **query surfaces**, not sync targets.

---

## What is synced into `.pro-local-rebuild/`

| Tier | Contents | Source on Studio |
| --- | --- | --- |
| 1 Citations | Overwatch `data/ingest/`, `data/references/`; SeedGraph `data/intake/` | Repo + ingest JSONL |
| 2 Experiments | `gettingsciencedone/experiments/`; `hydradg/eval/`; Overwatch `experiments/` | Repo trees |
| 3 Lab notebooks | Watchtower `LAB_NOTEBOOK.md`; Overwatch `docs/notebooks/` | Repo |
| 4 Atom sources | HydraDG `custody/graph/live/*.jsonl`; SeedGraph `~/.config/seedgraph/store/`; `magicLABbox/.../seedgraph/sources/` | FCG + content-addressed store |
| 5 Runtime eval | `~/.local/share/hydradg-best-use/{eval,receipts,data}/` | Local-only receipts |
| 6 Datasets | `~/.local/share/hydradg-datasets/` (~2.8 GB) | Replay inputs for Track 01/03 |
| 7 Research hub | `research_hub/literature/papers/**/metadata.json` (+ JSON/BIB sidecars) | Citation corpus metadata |

**Never synced:** `hydradb-auth-token`, `FLOOR10_AGENT_TOKEN`, `.env`, private keys, live Arango/Neo4j volumes.

---

## Git sync status (run after every Studio block)

```bash
for r in hydradg overwatch watchtower gettingsciencedone; do
  git -C ~/projects/active/$r fetch origin && git -C ~/projects/active/$r pull --ff-only origin main
done
git -C ~/projects/active/seedgraph fetch origin   # may diverge — merge manually
```

| Repo | Role |
| --- | --- |
| `hydradg` | Judge eval, FCG JSONL, prereg, custody |
| `overwatch` | Publications ingest sidecars (also in bundle) |
| `seedgraph` | `publication.atomic.json` proofs (~1.5k in git) |
| `gettingsciencedone` | `EXP_*/runs/*/PREREGISTRATION.json` |
| `watchtower` | `LAB_NOTEBOOK.md`, portfolio graph |

---

## Pro-local review without Studio

### Offline (JSON only)

```bash
# HydraDG graph → local HydraDB (needs token outside git)
python3 scripts/project_fcg_snapshot_to_hydradb.py ...

# Overwatch control-plane dry-run
python3 ~/projects/active/overwatch/scripts/ingest_control_plane_to_arango.py --dry-run

# Inspect bundle manifest
cat .pro-local-rebuild/SYNC_RECEIPT.json | python3 -m json.tool | head -40
```

### OrbStack on Pro (limited)

- Pro `seedgraph-neo4j-local` may exist (~14k nodes) — **demo/navigation only**, not canonical.
- **Do not** start Overwatch/ProTHub Arango without `/Volumes/magicLABbox` mounted.

### Live (Studio up)

```bash
curl -fsS http://127.0.0.1:18000/       # Watchtower via tunnel
curl -fsS http://127.0.0.1:18484/health # Ollarma via tunnel
ssh magicSTUDIObox.local 'curl -fsS http://127.0.0.1:8531/_api/version'
```

---

## Gitleaks review

Run before promoting bundle contents or committing any exported JSON:

```bash
gitleaks detect --config .gitleaks.toml --no-git -v --source .pro-local-rebuild/
gitleaks detect --config .gitleaks.toml -v   # full repo
```

Policy: `.gitleaks.toml` (reviewed false-positive allowlists for SeedGraph cache SHAs and toy seal objects).

**Latest scan (main tree):** no leaks on recent commits. Re-scan after each sync.

Manual grep gate (bundle must not contain):

```bash
rg -l 'FLOOR10_AGENT_TOKEN|sk-[A-Za-z0-9]{20,}|hydradb-auth-token' .pro-local-rebuild/ || echo PASS
```

---

## Cold-rebuild checklist

- [ ] `git pull` all five repos; confirm `HEAD == origin/main` (except seedgraph if diverged)
- [ ] Run `scripts/sync_pro_studio_full_rebuild.sh`
- [ ] Verify `.pro-local-rebuild/SYNC_RECEIPT.json` + `SHA256SUMS`
- [ ] Gitleaks + secret grep pass
- [ ] HydraDG: `custody/graph/live/{nodes,edges}.jsonl` hashes match receipt
- [ ] Citations: ingest JSONL present under `overwatch/data/ingest/`
- [ ] Experiments: `gettingsciencedone/experiments/EXP_*/` present
- [ ] Atoms: `atoms/seedgraph-store/` + `atoms/seedgraph-sources/` non-empty
- [ ] Datasets: `hydradg-runtime/datasets/` complete (check `SYNC.log` for `DATASETS_SYNC_DONE`)
- [ ] Optional: copy bundle subsets into live repo paths for tooling that expects canonical locations

---

## Optional: promote bundle → live paths

Only when operator intends Pro to run replay tooling in-place:

```bash
B=.pro-local-rebuild
cp -R $B/hydradg-runtime/datasets/* ~/.local/share/hydradg-datasets/ 2>/dev/null || true
cp -R $B/atoms/seedgraph-store/* ~/.config/seedgraph/store/ 2>/dev/null || true
```

Do not overwrite git-tracked files without review.

---

## Known gaps

| Gap | Mitigation |
| --- | --- |
| Pro lacks `magicDATAbox` / `magicLABbox` mounts | rsync via Studio SSH |
| Overwatch/ProTHub Arango not on Pro | JSON ingest sidecars + Studio query |
| SeedGraph Neo4j live graph | `publication.atomic.json` in git + store rsync |
| `seedgraph` main diverged on Pro | fetch + manual merge |
| Research PDFs (~4 GB) | metadata-only by default; set `SYNC_RESEARCH_PDFS=1` for full |

---

## Related docs

- `HYDRADB_DATA.md` — JSONL → HydraDB rebuild
- `docs/JUDGE_REPRODUCE_FROM_SCRATCH.md` — public repro path
- `gettingsciencedone/docs/TWO_HOST_RUNTIME_INVENTORY.md` — live service map
- `watchtower/.planning/failsafe/magicprobox-kg-failsafe-20260813/FAILSAFE_README.md` — Pro KG limits
