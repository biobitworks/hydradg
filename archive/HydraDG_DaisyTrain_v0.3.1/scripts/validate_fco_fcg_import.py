from pathlib import Path
import argparse,json,hashlib
ap=argparse.ArgumentParser(); ap.add_argument("dir"); args=ap.parse_args()
d=Path(args.dir)
nodes=[json.loads(x) for x in (d/"nodes.jsonl").read_text().splitlines() if x.strip()]
edges=[json.loads(x) for x in (d/"edges.jsonl").read_text().splitlines() if x.strip()]
ids={n["id"] for n in nodes}
bad=[e for e in edges if e["src"] not in ids or e["dst"] not in ids]
if bad:
    print(f"FAIL {len(bad)} dangling edges"); raise SystemExit(1)
print(f"PASS nodes={len(nodes)} edges={len(edges)}")
