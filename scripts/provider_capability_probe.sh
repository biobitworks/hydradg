#!/usr/bin/env bash
set -euo pipefail

# Secret-safe capability probe for HydraDG burst/evaluation providers.
# Run on magicPRObox. It reports only PRESENT/MISSING or CLI availability.
# It never prints credential values and does not modify provider accounts.

ROOT="/Users/byron/projects/active/hydradg"
OLLARMA="/Users/byron/projects/active/ollarma"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"
RUN_ID="PROVIDER-CAPABILITY-$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/HydraDG_DaisyTrain_v0.3.7/eval/provider_capability/$RUN_ID"

fail(){ echo "FAIL=$1"; exit "${2:-1}"; }

cd "$ROOT"
test "$(git rev-parse --show-toplevel)" = "$ROOT" || fail WRONG_HYDRADG_ROOT 10
test -z "$(git status --porcelain)" || { git status --short; fail DIRTY_HYDRADG 11; }
git fetch origin "$BRANCH" --quiet
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
git pull --ff-only origin "$BRANCH" >/dev/null
test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")" || fail BRANCH_DIVERGED 12

mkdir -p "$OUT"

command_state(){
  local c="$1"
  if command -v "$c" >/dev/null 2>&1; then
    printf 'COMMAND:%s=PRESENT\n' "$c"
  else
    printf 'COMMAND:%s=MISSING\n' "$c"
  fi
}

env_state(){
  local k="$1"
  if [ -n "${!k:-}" ]; then
    printf 'ENV:%s=PRESENT\n' "$k"
  else
    printf 'ENV:%s=MISSING\n' "$k"
  fi
}

file_key_state(){
  local file="$1" key="$2"
  if [ -f "$file" ] && grep -Eq "^[[:space:]]*(export[[:space:]]+)?${key}=" "$file"; then
    printf 'LOCAL_ENV_FILE_KEY:%s:%s=PRESENT\n' "$(basename "$file")" "$key"
  else
    printf 'LOCAL_ENV_FILE_KEY:%s:%s=MISSING\n' "$(basename "$file")" "$key"
  fi
}

{
  echo "schema=hydradg.provider_capability_probe.v1"
  echo "timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"

  for c in modal kaggle daytona gh git uv python3 curl jq tailscale ssh; do
    command_state "$c"
  done

  # Common provider variable names. Presence only; values are never emitted.
  for k in \
    MODAL_TOKEN_ID MODAL_TOKEN_SECRET MODAL_PROFILE \
    KAGGLE_USERNAME KAGGLE_KEY \
    EXA_API_KEY \
    APIFY_API_TOKEN APIFY_TOKEN \
    DAYTONA_API_KEY \
    RUNPOD_API_KEY; do
    env_state "$k"
  done

  if [ -d "$OLLARMA/.git" ]; then
    echo "OLLARMA_REPO=PRESENT"
    echo "OLLARMA_HEAD=$(git -C "$OLLARMA" rev-parse HEAD)"
  else
    echo "OLLARMA_REPO=MISSING"
  fi

  # Probe only key names in local ignored env files. Never print any line/value.
  for f in "$OLLARMA/.env" "$OLLARMA/.env.local"; do
    [ -f "$f" ] || continue
    echo "LOCAL_ENV_FILE=$(basename "$f")=PRESENT"
    for k in \
      MODAL_TOKEN_ID MODAL_TOKEN_SECRET MODAL_PROFILE \
      KAGGLE_USERNAME KAGGLE_KEY \
      EXA_API_KEY \
      APIFY_API_TOKEN APIFY_TOKEN \
      DAYTONA_API_KEY \
      RUNPOD_API_KEY; do
      file_key_state "$f" "$k"
    done
  done
} > "$OUT/capabilities.txt"

CAP_SHA="$(shasum -a 256 "$OUT/capabilities.txt" | awk '{print $1}')"

jq -n \
  --arg run_id "$RUN_ID" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg host "$(hostname)" \
  --arg capabilities_sha "$CAP_SHA" \
  '{
    schema:"hydradg.provider_capability_receipt.v1",
    run_id:$run_id,
    timestamp_utc:$timestamp,
    host:$host,
    execution_class:"LOCAL_RECOMPUTED_SECRET_SAFE_CAPABILITY_PROBE",
    evidence_sha256:{capabilities:$capabilities_sha},
    secret_policy:"PRESENCE_ONLY_NO_VALUES_EMITTED",
    claim_ceiling:"LOCAL_PROVIDER_TOOL_AND_CREDENTIAL_PRESENCE_ONLY",
    signature_state:"NOT_SIGNED_BY_THIS_SCRIPT",
    mmr_state:"APPEND_PENDING"
  }' > "$OUT/PROVIDER_CAPABILITY_RECEIPT.json"

RECEIPT_SHA="$(shasum -a 256 "$OUT/PROVIDER_CAPABILITY_RECEIPT.json" | awk '{print $1}')"

echo "PASS" > "$OUT/final_status.txt"

# Scan staged evidence before commit; report contains no secret values by design.
git add "HydraDG_DaisyTrain_v0.3.7/eval/provider_capability/$RUN_ID"
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks git --staged --redact=100 --no-banner .
fi

git commit -m "Record provider capability probe $RUN_ID"
git push origin "$BRANCH"
git fetch origin "$BRANCH" --quiet
git pull --ff-only origin "$BRANCH" >/dev/null
LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse "origin/$BRANCH")"
test "$LOCAL" = "$REMOTE" || fail POST_PUSH_DIVERGENCE 20

echo "PROVIDER_CAPABILITY_PROBE=PASS"
echo "CHECKPOINT_COMMIT=$LOCAL"
echo "RECEIPT_SHA256=$RECEIPT_SHA"
echo "=== CAPABILITY SUMMARY ==="
cat "$OUT/capabilities.txt"
