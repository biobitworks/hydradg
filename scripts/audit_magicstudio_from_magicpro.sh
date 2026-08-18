#!/usr/bin/env bash
set -euo pipefail

# Run ONLY on magicPRObox. Audits magicSTUDIObox over ordinary SSH carried by
# Tailscale. It does not install anything. It writes a bounded receipt locally
# in HydraDG, commits/pushes it on the setup branch, then verifies local == remote.

ROOT="/Users/byron/projects/active/hydradg"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"
STUDIO_SSH="${STUDIO_SSH:-magicstudiobox}"
RUN_ID="MAGICSTUDIO-DEPS-$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"

log(){ printf '[%3s%%] %s\n' "$1" "$2"; }
fail(){
  local msg="FAIL=$1"
  echo "$msg"
  if [ -d "${OUT:-}" ]; then printf '%s\n' "$msg" >> "$OUT/final_status.txt"; fi
  exit "${2:-1}"
}

log 5 "pull/verify MagicPro control-plane branch"
cd "$ROOT"
test "$(git rev-parse --show-toplevel)" = "$ROOT" || fail WRONG_HYDRADG_ROOT 10
# Critical ordering: the run directory is not created until after this clean gate.
test -z "$(git status --porcelain)" || { git status --short; fail DIRTY_MAGICPRO_HYDRADG 11; }
git fetch origin "$BRANCH" --quiet
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
git pull --ff-only origin "$BRANCH" >/dev/null
test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")" || fail MAGICPRO_BRANCH_DIVERGED 12
test -z "$(git status --porcelain)" || fail DIRTY_MAGICPRO_AFTER_PULL 13

mkdir -p "$OUT"

log 15 "verify Tailscale/SSH transport"
command -v tailscale >/dev/null || fail TAILSCALE_MISSING_MAGICPRO 20
tailscale status > "$OUT/tailscale_magicpro.txt"
ssh -o BatchMode=yes -o ConnectTimeout=10 "$STUDIO_SSH" 'hostname; whoami; command -v tailscale >/dev/null && tailscale status >/dev/null && echo STUDIO_TRANSPORT=PASS' > "$OUT/studio_transport.txt" || fail STUDIO_SSH_OR_TAILSCALE_FAILED 21

log 25 "audit Homebrew/runtime dependencies on MagicStudio"
ssh -o BatchMode=yes "$STUDIO_SSH" 'bash -s' <<'REMOTE' > "$OUT/studio_dependency_audit.txt"
set -euo pipefail

if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif command -v brew >/dev/null 2>&1; then
  eval "$(brew shellenv)"
else
  echo "HOMEBREW=MISS"
  exit 0
fi

echo "HOMEBREW=PASS"
echo "BREW_PREFIX=$(brew --prefix)"
echo "BREW_VERSION=$(brew --version | head -n1)"

if brew tap | grep -qx 'cleishm/neo4j'; then
  echo "BREW_TAP:cleishm/neo4j=PASS"
else
  echo "BREW_TAP:cleishm/neo4j=MISS"
fi

# HydraDB source-build dependencies + our remote operator/runtime dependencies.
for F in just cmake pkgconf llvm suite-sparse tmux uv gh jq git-lfs gitleaks; do
  if brew list --versions "$F" >/dev/null 2>&1; then
    echo "BREW_FORMULA:$F=PASS:$(brew list --versions "$F" | head -n1)"
  else
    echo "BREW_FORMULA:$F=MISS"
  fi
done

# libcypher-parser comes from cleishm/neo4j; pkg-config package is cypher-parser.
if brew list --versions libcypher-parser >/dev/null 2>&1; then
  echo "BREW_FORMULA:libcypher-parser=PASS:$(brew list --versions libcypher-parser | head -n1)"
else
  echo "BREW_FORMULA:libcypher-parser=MISS"
fi

if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists cypher-parser; then
  echo "PKGCONFIG:cypher-parser=PASS:$(pkg-config --modversion cypher-parser)"
else
  echo "PKGCONFIG:cypher-parser=MISS"
fi

if xcode-select -p >/dev/null 2>&1 && command -v clang >/dev/null 2>&1; then
  echo "XCODE_CLT=PASS:$(xcode-select -p)"
  echo "CLANG=PASS:$(clang --version | head -n1)"
else
  echo "XCODE_CLT=MISS"
fi

source "$HOME/.cargo/env" 2>/dev/null || true
for C in rustc cargo git curl python3 openssl; do
  if command -v "$C" >/dev/null 2>&1; then
    echo "COMMAND:$C=PASS:$($C --version 2>/dev/null | head -n1 || true)"
  else
    echo "COMMAND:$C=MISS"
  fi
done

if command -v tailscale >/dev/null 2>&1; then echo "COMMAND:tailscale=PASS"; else echo "COMMAND:tailscale=MISS"; fi
if command -v ollama >/dev/null 2>&1; then echo "COMMAND:ollama=PASS"; else echo "COMMAND:ollama=MISS"; fi

for P in hydradg hydradb ollarma watchtower; do
  if [ -d "/Users/byron/projects/active/$P/.git" ]; then
    echo "REPO:$P=PASS:$(git -C "/Users/byron/projects/active/$P" rev-parse HEAD 2>/dev/null || true)"
  else
    echo "REPO:$P=MISS"
  fi
done

if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then echo "OLLAMA_API=PASS"; else echo "OLLAMA_API=MISS"; fi
if curl -fsS http://127.0.0.1:8484/health >/dev/null 2>&1; then echo "OLLARMA_HEALTH=PASS"; else echo "OLLARMA_HEALTH=MISS"; fi
if curl -fsS http://127.0.0.1:8000/ >/dev/null 2>&1; then echo "WATCHTOWER_HEALTH=PASS"; else echo "WATCHTOWER_HEALTH=MISS"; fi
if curl -fsS http://127.0.0.1:9090/readyz >/dev/null 2>&1; then echo "HYDRADB_READYZ=PASS"; else echo "HYDRADB_READYZ=MISS"; fi
REMOTE

log 55 "summarize exact missing dependencies"
{
  grep -E '^(HOMEBREW|XCODE_CLT|OLLAMA_API|OLLARMA_HEALTH|WATCHTOWER_HEALTH|HYDRADB_READYZ)=' "$OUT/studio_dependency_audit.txt" || true
  grep -E '^(BREW_TAP:|BREW_FORMULA:|PKGCONFIG:|COMMAND:|REPO:)' "$OUT/studio_dependency_audit.txt" || true
} | sort -u > "$OUT/studio_dependency_summary.txt"
grep -E '=MISS($|:)' "$OUT/studio_dependency_summary.txt" > "$OUT/studio_missing.txt" || true

# Produce a bounded operator hint without executing it.
{
  echo '# Suggested remediation; review audit first.'
  echo 'brew formula baseline: just cmake pkgconf llvm suite-sparse tmux uv gh jq git-lfs gitleaks'
  echo 'external tap formula: cleishm/neo4j/libcypher-parser'
  echo 'Rust: rustup stable (not Homebrew)'
  echo 'Xcode CLT: required if XCODE_CLT=MISS; not installed by this script'
} > "$OUT/remediation_hint.txt"

AUDIT_SHA="$(shasum -a 256 "$OUT/studio_dependency_audit.txt" | awk '{print $1}')"
MISSING_SHA="$(shasum -a 256 "$OUT/studio_missing.txt" | awk '{print $1}')"

jq -n \
  --arg run_id "$RUN_ID" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg ssh_alias "$STUDIO_SSH" \
  --arg audit_sha "$AUDIT_SHA" \
  --arg missing_sha "$MISSING_SHA" \
  '{schema:"hydradg.magicstudio_dependency_audit.v1",run_id:$run_id,timestamp_utc:$timestamp,execution_class:"REMOTE_RECOMPUTED_FROM_MAGICPRO",transport:{ssh_alias:$ssh_alias,tailscale:"PASS"},evidence_sha256:{audit:$audit_sha,missing:$missing_sha},claim_ceiling:"MAGICSTUDIO_DEPENDENCY_AND_SERVICE_AUDIT_ONLY",signature_state:"NOT_SIGNED_BY_THIS_SCRIPT",mmr_state:"APPEND_PENDING"}' > "$OUT/AUDIT_RECEIPT.json"
RECEIPT_SHA="$(shasum -a 256 "$OUT/AUDIT_RECEIPT.json" | awk '{print $1}')"
echo PASS > "$OUT/final_status.txt"

log 75 "commit/push audit receipt"
cd "$ROOT"
git add "HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"
if command -v gitleaks >/dev/null 2>&1; then gitleaks git --staged --redact=100 --no-banner .; fi
git commit -m "Audit MagicStudio remote dependencies $RUN_ID"
git push origin "$BRANCH"
git fetch origin "$BRANCH" --quiet
git pull --ff-only origin "$BRANCH" >/dev/null
LOCAL="$(git rev-parse HEAD)"; REMOTE_SHA="$(git rev-parse "origin/$BRANCH")"
test "$LOCAL" = "$REMOTE_SHA" || fail POST_PUSH_DIVERGENCE 30

log 100 "complete"
echo "MAGICSTUDIO_DEPENDENCY_AUDIT=PASS"
echo "CHECKPOINT_COMMIT=$LOCAL"
echo "RECEIPT_SHA256=$RECEIPT_SHA"
echo "=== MISSING ==="
cat "$OUT/studio_missing.txt"
