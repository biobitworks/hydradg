#!/usr/bin/env bash
set -euo pipefail
# Run on magicPRObox. Signs the latest turn_root from magicstudiobox.
STUDIO="${STUDIO_HOST:-magicstudiobox}"
REMOTE_LOG="${REMOTE_TURN_LOG:-/Users/byron/projects/active/hydradg-knowledge-graph/turn_custody.jsonl}"
REMOTE_SIGDIR="${REMOTE_TURN_SIGDIR:-/Users/byron/projects/active/hydradg-knowledge-graph/turn_signatures}"
KEY="${FCO_SIGNING_KEY:-$HOME/.fco/keys/fcg_signing_ed25519.pem}"
PUB="${FCO_PUBLIC_KEY:-/Users/byron/projects/active/fractal-custody-objects/PUBLIC_KEY.ed25519.pub}"

[[ -f "$KEY" ]] || { echo "missing private key: $KEY"; exit 2; }
[[ -f "$PUB" ]] || { echo "missing public key: $PUB"; exit 2; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
scp "$STUDIO:$REMOTE_LOG" "$TMP/turn_custody.jsonl"
ROOT="$(tail -n 1 "$TMP/turn_custody.jsonl" | python3 -c 'import json,sys; print(json.load(sys.stdin)["turn_root_sha256"])')"
printf '%s' "$ROOT" > "$TMP/turn_root.txt"
openssl pkeyutl -sign -inkey "$KEY" -rawin -in "$TMP/turn_root.txt" -out "$TMP/TURN_ROOT.sig"
openssl pkeyutl -verify -pubin -inkey "$PUB" -rawin -in "$TMP/turn_root.txt" -sigfile "$TMP/TURN_ROOT.sig"
PUBFP="$(openssl pkey -pubin -in "$PUB" -outform DER 2>/dev/null | shasum -a 256 | awk '{print $1}')"
SIGHEX="$(xxd -p "$TMP/TURN_ROOT.sig" | tr -d '\n')"
python3 - "$ROOT" "$PUBFP" "$SIGHEX" "$TMP/TURN_SIGNATURE_RECEIPT.json" <<'PY'
import datetime,json,sys
root,pubfp,sighex,out=sys.argv[1:]
obj={"schema":"hydradg.turn_signature_receipt.v1","signed_turn_root_sha256":root,
     "algorithm":"Ed25519","public_key_fingerprint_sha256":pubfp,
     "signature_hex":sighex,"signature_state":"SIGNED_AND_LOCALLY_VERIFIED",
     "verification_state":"VERIFY_OK",
     "signed_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
json.dump(obj,open(out,"w"),indent=2,sort_keys=True); open(out,"a").write("\n")
print(json.dumps(obj,indent=2,sort_keys=True))
PY
ssh "$STUDIO" "mkdir -p '$REMOTE_SIGDIR'"
scp "$TMP/TURN_ROOT.sig" "$TMP/TURN_SIGNATURE_RECEIPT.json" "$STUDIO:$REMOTE_SIGDIR/"
echo "TURN_SIGN_AND_VERIFY_COMPLETE root=$ROOT"
