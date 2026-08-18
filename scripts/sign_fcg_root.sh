#!/usr/bin/env bash
set -euo pipefail

CUSTODY_DIR="${CUSTODY_DIR:-custody/live}"
PRIVATE_KEY="${FCO_SIGNING_KEY:-${1:-}}"
PUBLIC_KEY="${FCO_PUBLIC_KEY:-$CUSTODY_DIR/PUBLIC_KEY.ed25519.pub}"
EXPECTED_FP="f496a067808026d45fbbad785bf83c6acd66429c2d257d246cc103c6d7ff460d"

if [[ -z "$PRIVATE_KEY" ]]; then
  echo "usage: FCO_SIGNING_KEY=/private/path/ed25519.pem $0" >&2
  exit 2
fi
if [[ ! -f "$PRIVATE_KEY" ]]; then
  echo "private key not found: $PRIVATE_KEY" >&2
  exit 2
fi
if [[ ! -f "$PUBLIC_KEY" ]]; then
  echo "public key leaf not found: $PUBLIC_KEY" >&2
  echo "Copy PUBLIC_KEY.ed25519.pub into custody/live, rebuild the root, then sign." >&2
  exit 2
fi

actual_fp="$({ openssl pkey -pubin -in "$PUBLIC_KEY" -outform DER 2>/dev/null || exit 1; } | openssl dgst -sha256 -r | awk '{print $1}')"
if [[ "$actual_fp" != "$EXPECTED_FP" ]]; then
  echo "public key fingerprint mismatch" >&2
  echo "expected: $EXPECTED_FP" >&2
  echo "actual:   $actual_fp" >&2
  exit 3
fi

python3 scripts/build_fcg_root.py --custody-dir "$CUSTODY_DIR"
root="$(python3 - "$CUSTODY_DIR/manifest.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1]))['fcg_root'], end='')
PY
)"
printf '%s' "$root" > /tmp/hydradg_fcg_root.txt

openssl pkeyutl -sign \
  -inkey "$PRIVATE_KEY" \
  -rawin \
  -in /tmp/hydradg_fcg_root.txt \
  -out "$CUSTODY_DIR/FCG_ROOT.sig"

openssl pkeyutl -verify \
  -pubin \
  -inkey "$PUBLIC_KEY" \
  -rawin \
  -in /tmp/hydradg_fcg_root.txt \
  -sigfile "$CUSTODY_DIR/FCG_ROOT.sig"

python3 - "$CUSTODY_DIR/manifest.json" "$actual_fp" <<'PY'
import json,sys
from pathlib import Path
path=Path(sys.argv[1])
manifest=json.loads(path.read_text())
manifest['author_signature_state']='AUTHOR_SIGNATURE_VERIFIED'
manifest['verified_public_key_der_sha256']=sys.argv[2]
manifest['signature_file']='FCG_ROOT.sig'
manifest['signature_algorithm']='Ed25519'
manifest['signature_claim_ceiling']='ROOT_SIGNED_BY_HOLDER_OF_OUT_OF_BAND_ANCHORED_KEY; DOES_NOT PROVE CONTENT CORRECTNESS'
path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
PY

rm -f /tmp/hydradg_fcg_root.txt
printf 'AUTHOR_SIGNATURE_VERIFIED root=%s public_key_der_sha256=%s\n' "$root" "$actual_fp"
