#!/usr/bin/env bash
set -euo pipefail
# Run this ON magicPRObox. The private key stays there.
STUDIO="${STUDIO_HOST:-magicstudiobox}"
REMOTE_EVAL="${REMOTE_EVAL:-/Users/byron/.local/share/hydradg-best-use/eval/matrix-20260819}"
KEY="${FCO_SIGNING_KEY:-$HOME/.fco/keys/fcg_signing_ed25519.pem}"
PUB="${FCO_PUBLIC_KEY:-/Users/byron/projects/active/fractal-custody-objects/PUBLIC_KEY.ed25519.pub}"

[[ -f "$KEY" ]] || { echo "missing private key: $KEY"; exit 2; }
[[ -f "$PUB" ]] || { echo "missing public key: $PUB"; exit 2; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

scp "$STUDIO:$REMOTE_EVAL/MATRIX_COMPARISON.json" "$TMP/MATRIX_COMPARISON.json"

ROOT="$(python3 - "$TMP/MATRIX_COMPARISON.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1]))["comparison_root_sha256"])
PY
)"
printf '%s' "$ROOT" > "$TMP/matrix_root.txt"

openssl pkeyutl -sign -inkey "$KEY" -rawin -in "$TMP/matrix_root.txt" -out "$TMP/MATRIX_ROOT.sig"
openssl pkeyutl -verify -pubin -inkey "$PUB" -rawin -in "$TMP/matrix_root.txt" -sigfile "$TMP/MATRIX_ROOT.sig"

PUBFP="$(openssl pkey -pubin -in "$PUB" -outform DER 2>/dev/null | shasum -a 256 | awk '{print $1}')"
SIGHEX="$(xxd -p "$TMP/MATRIX_ROOT.sig" | tr -d '\n')"

python3 - "$ROOT" "$PUBFP" "$SIGHEX" "$TMP/SIGNATURE_RECEIPT.json" <<'PY'
import datetime,json,sys
root,pubfp,sighex,out=sys.argv[1:]
obj={
 "schema":"hydradg.matrix_signature_receipt.v1",
 "signed_root_sha256":root,
 "algorithm":"Ed25519",
 "public_key_fingerprint_sha256":pubfp,
 "signature_hex":sighex,
 "signature_state":"SIGNED_AND_LOCALLY_VERIFIED",
 "verification_state":"VERIFY_OK",
 "signed_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "merkle_state":"NOT_MERKLE_COMMITTED",
}
json.dump(obj,open(out,"w"),indent=2,sort_keys=True); open(out,"a").write("\n")
print(json.dumps(obj,indent=2,sort_keys=True))
PY

scp "$TMP/MATRIX_ROOT.sig" "$TMP/SIGNATURE_RECEIPT.json" "$STUDIO:$REMOTE_EVAL/"
echo "SIGN_AND_VERIFY_COMPLETE root=$ROOT"
