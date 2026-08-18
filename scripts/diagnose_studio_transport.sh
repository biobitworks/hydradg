#!/usr/bin/env bash
set -euo pipefail

# Run on magicPRObox. Diagnoses the transport gate without printing keys,
# tokens, full SSH config, or Tailscale peer/IP listings.

ROOT="/Users/byron/projects/active/hydradg"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"
RUN_ID="STUDIO-TRANSPORT-DIAG-$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"

fail(){ echo "FAIL=$1"; exit "${2:-1}"; }

cd "$ROOT"
test "$(git rev-parse --show-toplevel)" = "$ROOT" || fail WRONG_HYDRADG_ROOT 10
test -z "$(git status --porcelain)" || { git status --short; fail DIRTY_HYDRADG 11; }
git fetch origin "$BRANCH" --quiet
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
git pull --ff-only origin "$BRANCH" >/dev/null
test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")" || fail BRANCH_DIVERGED 12
mkdir -p "$OUT"

LOCAL_TS="MISSING"
if command -v tailscale >/dev/null 2>&1; then
  if tailscale status >/dev/null 2>&1; then LOCAL_TS="PASS"; else LOCAL_TS="COMMAND_PRESENT_STATUS_FAILED"; fi
fi
printf 'MAGICPRO_TAILSCALE=%s\n' "$LOCAL_TS" | tee "$OUT/diagnosis.txt"

CANDIDATES=()
if [ -n "${STUDIO_SSH:-}" ]; then
  CANDIDATES+=("$STUDIO_SSH")
else
  CANDIDATES+=("magicstudiobox" "magicstudio")
fi

SELECTED=""
for C in "${CANDIDATES[@]}"; do
  printf 'SSH_ALIAS:%s=TESTING\n' "$C" | tee -a "$OUT/diagnosis.txt"
  set +e
  RESULT="$(ssh -o BatchMode=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 "$C" 'printf "SSH=PASS\\n"; if command -v tailscale >/dev/null 2>&1; then if tailscale status >/dev/null 2>&1; then printf "STUDIO_TAILSCALE=PASS\\n"; else printf "STUDIO_TAILSCALE=STATUS_FAILED\\n"; fi; else printf "STUDIO_TAILSCALE=MISSING\\n"; fi; printf "HOSTNAME=%s\\n" "$(hostname)"' 2>/dev/null)"
  RC=$?
  set -e
  if [ "$RC" -eq 0 ]; then
    printf '%s\n' "$RESULT" | tee -a "$OUT/diagnosis.txt"
    if printf '%s\n' "$RESULT" | grep -q '^SSH=PASS$' && printf '%s\n' "$RESULT" | grep -q '^STUDIO_TAILSCALE=PASS$'; then
      SELECTED="$C"
      printf 'SSH_ALIAS:%s=PASS\n' "$C" | tee -a "$OUT/diagnosis.txt"
      break
    else
      printf 'SSH_ALIAS:%s=SSH_REACHED_BUT_TAILSCALE_CHECK_FAILED\n' "$C" | tee -a "$OUT/diagnosis.txt"
    fi
  else
    printf 'SSH_ALIAS:%s=SSH_FAILED:rc=%s\n' "$C" "$RC" | tee -a "$OUT/diagnosis.txt"
  fi
done

if [ -n "$SELECTED" ]; then
  STATE="PASS"
else
  STATE="FAIL"
fi

echo "SELECTED_STUDIO_SSH=${SELECTED:-NONE}" | tee -a "$OUT/diagnosis.txt"
echo "TRANSPORT_GATE=$STATE" | tee -a "$OUT/diagnosis.txt"
DIAG_SHA="$(shasum -a 256 "$OUT/diagnosis.txt" | awk '{print $1}')"

jq -n --arg run "$RUN_ID" --arg state "$STATE" --arg alias "${SELECTED:-NONE}" --arg sha "$DIAG_SHA" '{schema:"hydradg.studio_transport_diagnosis.v1",run_id:$run,execution_class:"LOCAL_CONTROL_PLANE_RECOMPUTED",transport_gate:$state,selected_ssh_alias:$alias,evidence_sha256:{diagnosis:$sha},secret_policy:"NO_KEYS_TOKENS_OR_PEER_IP_LISTINGS_EMITTED",claim_ceiling:"MAGICPRO_TO_MAGICSTUDIO_TRANSPORT_DIAGNOSIS_ONLY",signature_state:"NOT_SIGNED_BY_THIS_SCRIPT",mmr_state:"APPEND_PENDING"}' > "$OUT/TRANSPORT_DIAG_RECEIPT.json"

echo "$STATE" > "$OUT/final_status.txt"
RECEIPT_SHA="$(shasum -a 256 "$OUT/TRANSPORT_DIAG_RECEIPT.json" | awk '{print $1}')"

git add "HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"
if command -v gitleaks >/dev/null 2>&1; then gitleaks git --staged --redact=100 --no-banner .; fi
git commit -m "Diagnose MagicStudio transport $RUN_ID"
git push origin "$BRANCH"
git fetch origin "$BRANCH" --quiet
git pull --ff-only origin "$BRANCH" >/dev/null
LOCAL="$(git rev-parse HEAD)"; REMOTE="$(git rev-parse "origin/$BRANCH")"
test "$LOCAL" = "$REMOTE" || fail POST_PUSH_DIVERGENCE 20

echo "TRANSPORT_DIAG_COMPLETE=YES"
echo "TRANSPORT_GATE=$STATE"
echo "SELECTED_STUDIO_SSH=${SELECTED:-NONE}"
echo "CHECKPOINT_COMMIT=$LOCAL"
echo "RECEIPT_SHA256=$RECEIPT_SHA"

if [ "$STATE" != "PASS" ]; then exit 30; fi
