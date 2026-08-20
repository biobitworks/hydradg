from pathlib import Path
import hashlib, sys

root = Path(__file__).resolve().parents[1]
manifest = root / "SHA256SUMS.txt"
bad = []
for line in manifest.read_text().splitlines():
    if not line.strip():
        continue
    expected, rel = line.split("  ", 1)
    p = root / rel
    if not p.is_file():
        bad.append((rel, "MISSING", expected))
        continue
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    if got != expected:
        bad.append((rel, got, expected))
if bad:
    for x in bad:
        print("FAIL", x)
    raise SystemExit(1)
print("PASS: package SHA256SUMS verified")
