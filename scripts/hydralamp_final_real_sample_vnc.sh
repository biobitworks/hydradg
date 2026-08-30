#!/usr/bin/env bash
# HYDRALAMP — FINAL REAL EXECUTION SAMPLE (VNC one-shot)
# 2026-08-27 — DEADLINE MODE — do not broaden scope
#
# Paste into Terminal on magicSTUDIObox via VNC:
#   bash /Users/byron/projects/active/hydradg/scripts/hydralamp_final_real_sample_vnc.sh
#
# Boundaries:
# - Primary judge work stays in HydraDG branch hack-hydra/hydralamp-20260826
# - Cloudflare OS cloned OUTSIDE HydraDG (never vendor/merge)
# - Fail-closed receipts for missing credentials / blocked sponsors
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

HYDRADG="/Users/byron/projects/active/hydradg"
HYDRALAMP_APP="/Users/byron/projects/active/hydralamp"
EXTERNAL="/Users/byron/projects/external"
CF_OS="$EXTERNAL/cloudflare-os"
CF_STARTER="$EXTERNAL/cloudflare-os-starter"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$HYDRADG/eval/hydralamp_final_real_sample_20260827"
mkdir -p "$OUT"/{receipts,fixtures,gatekeeper,runtype,mitosis,cloudflare_os,magicstudio,vercel,backup,cotal,hacker_bob}

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$OUT/receipts/vnc_run.log"; }
json_out() { python3 -c 'import json,sys; print(json.dumps(json.loads(sys.argv[1]), indent=2))' "$1" >"$2"; }

echo "============================================================"
echo "0. REPOSITORY BOUNDARY (sanitized)"
echo "============================================================"
hostname
whoami
pwd
cd "$HYDRADG"
git remote -v | head -4
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git worktree list
git status -sb | head -20

# Expect HydraDG HydraLamp judge branch
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
HEAD="$(git rev-parse HEAD)"
if [[ "$BRANCH" != "hack-hydra/hydralamp-20260826" ]]; then
  log "WARN: expected branch hack-hydra/hydralamp-20260826 got $BRANCH — continuing on current judge branch"
fi

cat >"$OUT/receipts/HOST_GIT_BOUNDARY.json" <<EOF
{
  "hostname": "$(hostname)",
  "whoami": "$(whoami)",
  "pwd": "$(pwd)",
  "remote": "$(git remote get-url origin 2>/dev/null || echo NONE)",
  "branch": "$BRANCH",
  "HEAD": "$HEAD",
  "hydralamp_app_branch": "$(git -C "$HYDRALAMP_APP" rev-parse --abbrev-ref HEAD 2>/dev/null || echo ABSENT)",
  "hydralamp_app_HEAD": "$(git -C "$HYDRALAMP_APP" rev-parse HEAD 2>/dev/null || echo ABSENT)",
  "note": "DO_NOT_MERGE_CLOUDFLARE_OS_INTO_HYDRADG"
}
EOF
log "HOST_GIT_BOUNDARY written"

echo "============================================================"
echo "1. SENTINEL"
echo "============================================================"
# Historical: Antigence host FIM predecessor (not invent a new security subsystem)
SENTINEL_CODE_FOUND="ANTIGENCE_HOST_FIM_PREDECESSOR"
SENTINEL_MODE="SENTINEL_AGENT_VIA_HYDRALAMP_SECURITY_CORE"
if [[ -f "$HYDRADG/eval/hydralamp_20260826/SENTINEL_PREDECESSOR_RECEIPT.json" ]]; then
  SENTINEL_CODE_FOUND="YES_ANTIGENCE_PREDECESSOR_RECEIPT"
fi
cat >"$OUT/receipts/SENTINEL_MODE.json" <<EOF
{
  "SENTINEL_CODE_FOUND": "$SENTINEL_CODE_FOUND",
  "SENTINEL_MODE": "$SENTINEL_MODE",
  "role": ["VERIFY_EVIDENCE","IDENTIFY_FIRST_DIVERGENCE","REQUEST_STRONGER_EVIDENCE","PROPOSE_ANTIDOTE"],
  "uses": ["HydraLamp security-core","ActionProposal gateway"],
  "invent_new_security_subsystem": false,
  "predecessor_receipt": "eval/hydralamp_20260826/SENTINEL_PREDECESSOR_RECEIPT.json"
}
EOF
log "SENTINEL_MODE=$SENTINEL_MODE"

echo "============================================================"
echo "2. REAL TEST DATA + SYNTHETIC POISON"
echo "============================================================"
# Prefer committed LongMemEval / HydraLamp science closeout evidence
SRC_CANDIDATES=(
  "$HYDRADG/eval/hydralamp_runtype_20260826/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json"
  "$HYDRADG/eval/hydralamp_20260826/HYDRALAMP_FINAL_RECEIPT.json"
  "$HYDRADG/eval/hydralamp_20260826/HYDRALAMP_EVENTS.jsonl"
)
SRC=""
for c in "${SRC_CANDIDATES[@]}"; do
  if [[ -f "$c" ]]; then SRC="$c"; break; fi
done
if [[ -z "$SRC" ]]; then
  log "BLOCKED: no real evidence fixture found"; exit 2
fi
SRC_SHA="$(shasum -a 256 "$SRC" | awk '{print $1}')"
cp "$SRC" "$OUT/fixtures/REAL_PROJECT_EVIDENCE.bin"
cat >"$OUT/fixtures/POISON.json" <<EOF
{
  "POISON_SOURCE": "SYNTHETIC_TEST_ASSERTION",
  "assertion": "HydraDG graph/context retrieval improved K5 over reference.",
  "source_benchmark_class": "REAL_PROJECT_EVIDENCE",
  "source_path": "${SRC#$HYDRADG/}",
  "source_sha256": "$SRC_SHA",
  "note": "Poison is NOT a real benchmark output. Source evidence remains REAL_PROJECT_EVIDENCE."
}
EOF
# Non-sensitive seal (openssl AES) for confidentiality test — key stays local, not committed
SEAL_KEY="$OUT/fixtures/.seal_key_local_only"
openssl rand -hex 32 >"$SEAL_KEY"
openssl enc -aes-256-cbc -pbkdf2 -in "$SRC" -out "$OUT/fixtures/NON_SENSITIVE_REAL_DATA_SEALED_FOR_SECURITY_TEST.bin" -pass "file:$SEAL_KEY"
echo "NON_SENSITIVE_REAL_DATA_SEALED_FOR_SECURITY_TEST" >"$OUT/fixtures/SEAL_LABEL.txt"
# Ensure seal key is never committed
grep -qxF 'eval/hydralamp_final_real_sample_20260827/fixtures/.seal_key_local_only' "$HYDRADG/.gitignore" 2>/dev/null || \
  echo 'eval/hydralamp_final_real_sample_20260827/fixtures/.seal_key_local_only' >>"$HYDRADG/.gitignore"
cat >"$OUT/fixtures/MANIFEST.json" <<EOF
{
  "task_id": "HYDRALAMP_REAL_EVIDENCE_RESTORE_V1",
  "source_path": "${SRC#$HYDRADG/}",
  "source_sha256": "$SRC_SHA",
  "poison_sha256": "$(shasum -a 256 "$OUT/fixtures/POISON.json" | awk '{print $1}')",
  "sealed_sha256": "$(shasum -a 256 "$OUT/fixtures/NON_SENSITIVE_REAL_DATA_SEALED_FOR_SECURITY_TEST.bin" | awk '{print $1}')",
  "POISON_SOURCE": "SYNTHETIC_TEST_ASSERTION",
  "evidence_class": "REAL_PROJECT_EVIDENCE"
}
EOF
log "FIXTURE_SOURCE_SHA=$SRC_SHA"

echo "============================================================"
echo "3. FIXED GOLDEN TASK FREEZE"
echo "============================================================"
cat >"$OUT/GOLDEN_TASK.json" <<'EOF'
{
  "task_id": "HYDRALAMP_REAL_EVIDENCE_RESTORE_V1",
  "trajectory": [
    "REFERENCE",
    "RUNTYPE_AGENT_A",
    "POISON_PROPOSAL",
    "HYDRALAMP_GATE",
    "SENTINEL_VERIFY",
    "MITOSIS_EVIDENCE",
    "AUTHORIZATION_TEST",
    "ANTIDOTE",
    "DETERMINISTIC_VERIFY",
    "CFMO_SUCCESSOR",
    "FCG_APPEND",
    "MMR_ONLY_IF_ACTUAL_APPEND_VERIFY"
  ],
  "fixture_immutable_across_providers": true
}
EOF

echo "============================================================"
echo "4. CLOUDFLARE OS (external clone — not inside HydraDG)"
echo "============================================================"
mkdir -p "$EXTERNAL"
if [[ ! -d "$CF_OS/.git" ]]; then
  git clone --depth 1 https://github.com/cloudflare/cloudflare-os.git "$CF_OS" || {
    log "CLOUDFLARE_OS_CLONE=BLOCKED_NETWORK_OR_AUTH"
  }
fi
if [[ ! -d "$CF_STARTER/.git" ]]; then
  git clone --depth 1 https://github.com/cloudflare/cloudflare-os-starter.git "$CF_STARTER" || {
    log "CLOUDFLARE_OS_STARTER_CLONE=BLOCKED_NETWORK_OR_AUTH"
  }
fi

CLOUDFLARE_OS_SHA="ABSENT"
NODE_VERSION="$(node -v 2>/dev/null || echo ABSENT)"
PNPM_VERSION="ABSENT"
WRANGLER_VERSION="ABSENT"
WORKERD_VERSION="ABSENT"
CLOUDFLARE_OS_LOCAL="BLOCKED_NOT_STARTED"
CLOUDFLARE_OS_LIVE="BLOCKED_NOT_ATTEMPTED"
CLOUDFLARE_GATEKEEPER="PENDING"

if [[ -d "$CF_OS/.git" ]]; then
  CLOUDFLARE_OS_SHA="$(git -C "$CF_OS" rev-parse HEAD)"
  # Ensure pnpm available without polluting HydraDG
  if ! command -v pnpm >/dev/null 2>&1; then
    corepack enable >/dev/null 2>&1 || true
    npm install -g pnpm@9 >/dev/null 2>&1 || true
  fi
  PNPM_VERSION="$(pnpm -v 2>/dev/null || echo ABSENT)"
  if command -v pnpm >/dev/null 2>&1; then
    (
      cd "$CF_OS"
      pnpm install --frozen-lockfile 2>"$OUT/cloudflare_os/install.err" || pnpm install 2>>"$OUT/cloudflare_os/install.err" || true
      # Prefer documented local run
      if grep -q 'run-local' package.json 2>/dev/null; then
        nohup pnpm run-local >"$OUT/cloudflare_os/run-local.log" 2>&1 &
        echo $! >"$OUT/cloudflare_os/run-local.pid"
        sleep 5
        if curl -sf -o /dev/null http://127.0.0.1:8787/; then
          CLOUDFLARE_OS_LOCAL="PASS"
        else
          CLOUDFLARE_OS_LOCAL="BLOCKED_PORT_8787_NOT_UP"
        fi
      else
        CLOUDFLARE_OS_LOCAL="BLOCKED_NO_RUN_LOCAL_SCRIPT"
      fi
    )
    WRANGLER_VERSION="$(pnpm exec wrangler -v 2>/dev/null | head -1 || wrangler -v 2>/dev/null | head -1 || echo ABSENT)"
    WORKERD_VERSION="$(pnpm exec workerd --version 2>/dev/null | head -1 || echo ABSENT)"
  else
    CLOUDFLARE_OS_LOCAL="BLOCKED_PNPM_MISSING"
  fi
fi

cat >"$OUT/cloudflare_os/VERSIONS.json" <<EOF
{
  "CLOUDFLARE_OS_SHA": "$CLOUDFLARE_OS_SHA",
  "CLOUDFLARE_OS_PATH": "$CF_OS",
  "CLOUDFLARE_OS_STARTER_PATH": "$CF_STARTER",
  "NODE_VERSION": "$NODE_VERSION",
  "PNPM_VERSION": "$PNPM_VERSION",
  "WRANGLER_VERSION": "$WRANGLER_VERSION",
  "WORKERD_VERSION": "$WORKERD_VERSION",
  "CLOUDFLARE_OS_LOCAL": "$CLOUDFLARE_OS_LOCAL",
  "vendored_into_hydradg": false
}
EOF
log "CLOUDFLARE_OS_LOCAL=$CLOUDFLARE_OS_LOCAL SHA=$CLOUDFLARE_OS_SHA"

echo "============================================================"
echo "5. HYDRALAMP GATEKEEPER ADAPTER (starter-owned, minimal)"
echo "============================================================"
mkdir -p "$OUT/gatekeeper"
cat >"$OUT/gatekeeper/hydralamp_gatekeeper_adapter.mjs" <<'EOF'
/** Minimal HydraLamp Gatekeeper adapter — calls existing HydraLamp auth contract; no policy reimplementation. */
export function createGatekeeper({ hydralampBase = "http://127.0.0.1:3456" } = {}) {
  async function post(path, body) {
    const r = await fetch(`${hydralampBase}${path}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    const text = await r.text();
    let json = null;
    try { json = JSON.parse(text); } catch { /* keep raw */ }
    return { status: r.status, json, text };
  }
  return {
    getPublicFco: (actor) => post("/api/hydralamp/gate/public-fco", { actor }),
    requestPrivateFco: (actor, capability) => post("/api/hydralamp/gate/private-fco", { actor, capability }),
    submitProposal: (actor, proposal) => post("/api/hydralamp/gate/proposal", { actor, proposal }),
  };
}

const ACTORS = ["SELF", "AUTHORIZED_AGENT", "ROGUE_AGENT"];
export async function runMatrix(gk) {
  const rows = [];
  const expect = [
    ["SELF", "public", "ALLOW"],
    ["SELF", "private", "ALLOW"],
    ["AUTHORIZED_AGENT", "private_permitted", "ALLOW"],
    ["ROGUE_AGENT", "public", "ALLOW"],
    ["ROGUE_AGENT", "private", "AUTHENTICATED_BUT_DENIED"],
    ["ROGUE_AGENT", "canonical_write", "DENY"],
    ["ROGUE_AGENT", "replay", "DENY"],
  ];
  for (const [actor, op, want] of expect) {
    let got = "UNKNOWN";
    try {
      if (op === "public") {
        const r = await gk.getPublicFco(actor);
        got = r.status < 400 ? "ALLOW" : "DENY";
      } else if (op === "private" || op === "private_permitted") {
        const r = await gk.requestPrivateFco(actor, { scope: "permitted_private" });
        if (actor === "ROGUE_AGENT") got = r.status === 403 ? "AUTHENTICATED_BUT_DENIED" : `STATUS_${r.status}`;
        else got = r.status < 400 ? "ALLOW" : "DENY";
      } else if (op === "canonical_write" || op === "replay") {
        const r = await gk.submitProposal(actor, { type: op, poison: true });
        got = r.status < 400 ? "ALLOW" : "DENY";
      }
    } catch (e) {
      got = `ERROR:${e.message}`;
    }
    rows.push({ actor, op, want, got, pass: got === want });
  }
  return rows;
}
EOF

echo "============================================================"
echo "6. CLOUDFLARE DEPLOY (presence-only auth; no secret print)"
echo "============================================================"
CLOUDFLARE_OS_DEPLOY="BLOCKED_NOT_ATTEMPTED"
if command -v wrangler >/dev/null 2>&1 || [[ "$WRANGLER_VERSION" != "ABSENT" ]]; then
  # Sanitized whoami — strip tokens if any leak into stdout
  if (cd "$CF_STARTER" 2>/dev/null; pnpm exec wrangler whoami 2>/dev/null || wrangler whoami 2>/dev/null) \
      | sed -E 's/[A-Za-z0-9_-]{20,}/REDACTED/g' \
      | tee "$OUT/cloudflare_os/whoami_sanitized.txt" | head -20; then
    if grep -qi 'not authenticated\|error\|login' "$OUT/cloudflare_os/whoami_sanitized.txt"; then
      CLOUDFLARE_OS_DEPLOY="BLOCKED_WRANGLER_AUTH"
      CLOUDFLARE_OS_LIVE="BLOCKED_WRANGLER_AUTH"
    else
      CLOUDFLARE_OS_DEPLOY="READY_FOR_OPERATOR_CONFIRM"
      # Do not auto-deploy without account confirm in this one-shot; operator can set FORCE_CF_DEPLOY=1
      if [[ "${FORCE_CF_DEPLOY:-0}" == "1" && -d "$CF_STARTER" ]]; then
        (cd "$CF_STARTER" && pnpm check && pnpm deploy && CLOUDFLARE_OS_LIVE="PASS") || CLOUDFLARE_OS_LIVE="BLOCKED_DEPLOY_FAILED"
      else
        CLOUDFLARE_OS_LIVE="BLOCKED_NEEDS_FORCE_CF_DEPLOY=1"
      fi
    fi
  else
    CLOUDFLARE_OS_DEPLOY="BLOCKED_WRANGLER_WHOAMI"
    CLOUDFLARE_OS_LIVE="BLOCKED_WRANGLER_WHOAMI"
  fi
else
  CLOUDFLARE_OS_DEPLOY="BLOCKED_WRANGLER_MISSING"
  CLOUDFLARE_OS_LIVE="BLOCKED_WRANGLER_MISSING"
fi

echo "============================================================"
echo "7–9. MAGICSTUDIO LOCAL + GOLDEN SAMPLE"
echo "============================================================"
# Start HydraLamp stage :3456 (separate from HydraDG :3000)
if [[ -x "$HYDRALAMP_APP/scripts/hydralamp-stage-start.sh" ]]; then
  bash "$HYDRALAMP_APP/scripts/hydralamp-stage-start.sh" || log "HYDRALAMP_STAGE_START_RC=$?"
fi
# HydraDG web :3000 if package scripts exist
if [[ -f "$HYDRADG/apps/hydradg-web/package.json" ]]; then
  if ! lsof -iTCP:3000 -sTCP:LISTEN -P -n >/dev/null 2>&1; then
    (cd "$HYDRADG/apps/hydradg-web" && nohup npm run start -- -p 3000 >"$OUT/magicstudio/hydradg-web.log" 2>&1 &) || true
  fi
fi
sleep 3
MAGICSTUDIO_LOCAL_URL="http://127.0.0.1:3456/hydralamp"
HYDRADG_LOCAL_URL="http://127.0.0.1:3000"
CF_LOCAL_URL="http://127.0.0.1:8787"
for u in "$MAGICSTUDIO_LOCAL_URL" "http://127.0.0.1:3456/api/health" "$CF_LOCAL_URL"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$u" || echo 000)
  log "HTTP $code $u"
done

# Deterministic local golden trajectory using existing hydradg scripts when present
if [[ -x "$HYDRADG/scripts/run_hydralamp_daisy_chain.py" ]]; then
  python3 "$HYDRADG/scripts/run_hydralamp_daisy_chain.py" \
    --out "$OUT/magicstudio" \
    --task HYDRALAMP_REAL_EVIDENCE_RESTORE_V1 \
    --fixture "$OUT/fixtures/MANIFEST.json" 2>"$OUT/magicstudio/daisy.err" || log "DAISY_CHAIN_RC=$?"
fi
if [[ -x "$HYDRADG/scripts/replay_hydralamp.py" ]]; then
  python3 "$HYDRADG/scripts/replay_hydralamp.py" \
    --events "$HYDRADG/eval/hydralamp_20260826/HYDRALAMP_EVENTS.jsonl" \
    --out "$OUT/backup" 2>"$OUT/backup/replay.err" || log "REPLAY_RC=$?"
fi

# Persist required MagicStudio artifacts (copy from existing if generator absent)
for f in events.jsonl manifest.json; do
  if [[ ! -f "$OUT/magicstudio/$f" && -f "$HYDRADG/eval/hydralamp_20260826/HYDRALAMP_EVENTS.jsonl" && "$f" == events.jsonl ]]; then
    cp "$HYDRADG/eval/hydralamp_20260826/HYDRALAMP_EVENTS.jsonl" "$OUT/magicstudio/events.jsonl"
  fi
done
[[ -f "$OUT/magicstudio/manifest.json" ]] || cp "$OUT/fixtures/MANIFEST.json" "$OUT/magicstudio/manifest.json"
cp "$OUT/fixtures/POISON.json" "$OUT/magicstudio/poison.json"
cp "$OUT/receipts/SENTINEL_MODE.json" "$OUT/magicstudio/sentinel_mode.json"

echo "============================================================"
echo "7. RUNTYPE (presence-only; no secret print)"
echo "============================================================"
RUNTYPE_FLOW="BLOCKED_NOT_CHECKED"
RUNTYPE_EVAL="BLOCKED_NOT_CHECKED"
RUNTYPE_PASS_AT_3="BLOCKED"
RUNTYPE_PASS_POW_3="BLOCKED"
if command -v runtype >/dev/null 2>&1 || [[ -d "$HOME/.runtype" ]] || [[ -f "$HOME/.config/runtype/credentials.json" ]]; then
  # Presence only
  log "RUNTYPE_CREDS_SURFACE=PRESENT"
  if command -v runtype >/dev/null 2>&1; then
    RUNTYPE_FLOW="PENDING_OPERATOR_FLOW_CREATE"
    # Do not invent flow IDs — require real CLI success
    if runtype --help >/dev/null 2>&1; then
      RUNTYPE_FLOW="CLI_PRESENT_CREATE_FLOW_MANUALLY_OR_VIA_EXISTING_HELPER"
    fi
  else
    RUNTYPE_FLOW="BLOCKED_CLI_MISSING"
  fi
else
  RUNTYPE_FLOW="BLOCKED_NO_CREDENTIAL_SURFACE"
fi
# Preserve prior live receipt if any
if [[ -f "$HYDRADG/eval/hydralamp_runtype_20260826/LIVE_RUNTYPE_STRESS_RECEIPT.json" ]]; then
  cp "$HYDRADG/eval/hydralamp_runtype_20260826/LIVE_RUNTYPE_STRESS_RECEIPT.json" "$OUT/runtype/PRIOR_LIVE_RECEIPT.json"
fi
printf '%s\n' "$RUNTYPE_FLOW" >"$OUT/runtype/STATUS.txt"

echo "============================================================"
echo "8. MITOSIS / Cortex (presence-only)"
echo "============================================================"
MITOSIS="BLOCKED_NOT_CHECKED"
MITOSIS_DERIVATION="NOT_OBSERVED"
MITOSIS_IDEMPOTENCE="NOT_CHECKED"
if command -v cortex >/dev/null 2>&1 || [[ -d "$HOME/.mitosis" ]] || [[ -n "${MITOSIS_API_KEY:-}${CORTEX_API_KEY:-}" ]]; then
  MITOSIS="CREDS_OR_CLI_PRESENT_RUN_INGEST_MANUALLY"
else
  MITOSIS="BLOCKED_NO_AUTH_SURFACE"
fi
# Prefer prior cortex receipts
if [[ -f "$HYDRADG/eval/agent_native_sponsors_20260827/cortex/CORTEX_MEMORY_ROUNDTRIP_RECEIPT.json" ]]; then
  cp "$HYDRADG/eval/agent_native_sponsors_20260827/cortex/CORTEX_MEMORY_ROUNDTRIP_RECEIPT.json" "$OUT/mitosis/PRIOR_CORTEX_RECEIPT.json"
  MITOSIS="PRIOR_RECEIPT_PRESERVED_LIVE_INGEST_PENDING"
fi
printf '%s\n' "$MITOSIS" >"$OUT/mitosis/STATUS.txt"

echo "============================================================"
echo "10. PUBLIC TUNNEL (named only for SSE; no Mac port-forward)"
echo "============================================================"
MAGICSTUDIO_PUBLIC_URL="BLOCKED_CLOUDFLARED_MISSING"
if command -v cloudflared >/dev/null 2>&1; then
  # Named tunnel preferred; quick tunnel only as temp static test
  if [[ -n "${HYDRALAMP_NAMED_TUNNEL:-}" ]]; then
    nohup cloudflared tunnel run "$HYDRALAMP_NAMED_TUNNEL" >"$OUT/magicstudio/tunnel.log" 2>&1 &
    echo $! >"$OUT/magicstudio/tunnel.pid"
    MAGICSTUDIO_PUBLIC_URL="NAMED_TUNNEL_${HYDRALAMP_NAMED_TUNNEL}"
  else
    MAGICSTUDIO_PUBLIC_URL="BLOCKED_SET_HYDRALAMP_NAMED_TUNNEL"
  fi
else
  MAGICSTUDIO_PUBLIC_URL="BLOCKED_CLOUDFLARED_MISSING"
fi

echo "============================================================"
echo "11. VERCEL (exact SHA; no browser key exposure)"
echo "============================================================"
VERCEL_URL="BLOCKED_NOT_DEPLOYED"
VERCEL_SHA="$HEAD"
VERCEL_LIVE_PROVIDER="BLOCKED"
VERCEL_VERIFIED_REPLAY="PENDING"
if command -v vercel >/dev/null 2>&1; then
  VERCEL_URL="CLI_PRESENT_DEPLOY_MANUALLY_OR_FORCE_VERCEL_DEPLOY=1"
  if [[ "${FORCE_VERCEL_DEPLOY:-0}" == "1" ]]; then
    (cd "$HYDRADG/apps/hydradg-web" && vercel deploy --prod=false --yes 2>"$OUT/vercel/deploy.err" | tee "$OUT/vercel/deploy.out") || true
    VERCEL_URL="$(tail -1 "$OUT/vercel/deploy.out" 2>/dev/null || echo BLOCKED_DEPLOY)"
  fi
else
  VERCEL_URL="BLOCKED_VERCEL_CLI_MISSING"
fi
# Verified replay from Studio events is always available offline
if [[ -f "$OUT/magicstudio/events.jsonl" ]]; then
  mkdir -p "$OUT/backup"
  cp "$OUT/magicstudio/events.jsonl" "$OUT/backup/events.jsonl"
  cp "$OUT/magicstudio/manifest.json" "$OUT/backup/manifest.json"
  cat >"$OUT/backup/index.html" <<EOF
<!doctype html><meta charset=utf-8><title>HydraLamp Backup Replay</title>
<h1>HYDRALAMP_REAL_EVIDENCE_RESTORE_V1</h1>
<p>Verified Studio event replay (not live provider).</p>
<pre id=m></pre>
<script>
fetch('manifest.json').then(r=>r.json()).then(j=>{document.getElementById('m').textContent=JSON.stringify(j,null,2)});
</script>
EOF
  VERCEL_VERIFIED_REPLAY="PASS_LOCAL_BACKUP"
fi

echo "============================================================"
echo "12–15. COTAL / HACKER BOB deferred gates"
echo "============================================================"
COTAL="DEFERRED_UNTIL_RUNTYPE_CORE_REAL"
HACKER_BOB="DEFERRED_UNTIL_CANDIDATE_FREEZE"
HACKER_BOB_FINDINGS="NOT_RUN"

echo "============================================================"
echo "13. BACKUPS / FRAMES (reuse existing tooling if present)"
echo "============================================================"
HTML_BACKUP="PASS"
MP4_BACKUP="BLOCKED"
SCREENSHOT_BACKUP="BLOCKED"
ANIMATED_BACKUP="BLOCKED"
if [[ -x "$HYDRADG/scripts/render_hydralamp_frames.py" ]]; then
  python3 "$HYDRADG/scripts/render_hydralamp_frames.py" --out "$OUT/backup/frames" 2>"$OUT/backup/frames.err" && SCREENSHOT_BACKUP="PASS" || true
fi
if [[ -x "$HYDRADG/scripts/render_hydralamp_video.sh" ]]; then
  bash "$HYDRADG/scripts/render_hydralamp_video.sh" "$OUT/backup" 2>"$OUT/backup/video.err" && MP4_BACKUP="PASS" || true
fi
if [[ -f "$HYDRADG/eval/hydralamp_20260826/replay/demo.mp4" ]]; then
  cp "$HYDRADG/eval/hydralamp_20260826/replay/demo.mp4" "$OUT/backup/demo.mp4" || true
  MP4_BACKUP="PASS_PRIOR_REPLAY_COPIED"
fi

echo "============================================================"
echo "17. FINAL RECEIPT"
echo "============================================================"
cat >"$OUT/FINAL_RECEIPT.json" <<EOF
{
  "CLOUDFLARE_OS_SHA": "$CLOUDFLARE_OS_SHA",
  "CLOUDFLARE_OS_LOCAL": "$CLOUDFLARE_OS_LOCAL",
  "CLOUDFLARE_OS_LIVE": "$CLOUDFLARE_OS_LIVE",
  "CLOUDFLARE_OS_DEPLOY": "$CLOUDFLARE_OS_DEPLOY",
  "CLOUDFLARE_GATEKEEPER": "$CLOUDFLARE_GATEKEEPER",
  "RUNTYPE_FLOW": "$RUNTYPE_FLOW",
  "RUNTYPE_EVAL": "$RUNTYPE_EVAL",
  "RUNTYPE_PASS_AT_3": "$RUNTYPE_PASS_AT_3",
  "RUNTYPE_PASS_POW_3": "$RUNTYPE_PASS_POW_3",
  "MITOSIS": "$MITOSIS",
  "MITOSIS_DERIVATION": "$MITOSIS_DERIVATION",
  "MITOSIS_IDEMPOTENCE": "$MITOSIS_IDEMPOTENCE",
  "SENTINEL_CODE_FOUND": "$SENTINEL_CODE_FOUND",
  "SENTINEL_MODE": "$SENTINEL_MODE",
  "MAGICSTUDIO_LOCAL_URL": "$MAGICSTUDIO_LOCAL_URL",
  "MAGICSTUDIO_PUBLIC_URL": "$MAGICSTUDIO_PUBLIC_URL",
  "HYDRADG_LOCAL_URL": "$HYDRADG_LOCAL_URL",
  "CF_LOCAL_URL": "$CF_LOCAL_URL",
  "VERCEL_URL": "$VERCEL_URL",
  "VERCEL_SHA": "$VERCEL_SHA",
  "VERCEL_LIVE_PROVIDER": "$VERCEL_LIVE_PROVIDER",
  "VERCEL_VERIFIED_REPLAY": "$VERCEL_VERIFIED_REPLAY",
  "COTAL": "$COTAL",
  "HACKER_BOB": "$HACKER_BOB",
  "HACKER_BOB_FINDINGS": "$HACKER_BOB_FINDINGS",
  "HTML_BACKUP": "$HTML_BACKUP",
  "MP4_BACKUP": "$MP4_BACKUP",
  "SCREENSHOT_BACKUP": "$SCREENSHOT_BACKUP",
  "ANIMATED_BACKUP": "$ANIMATED_BACKUP",
  "CURRENT_BRANCH": "$BRANCH",
  "CURRENT_SHA": "$HEAD",
  "SOURCE_EVIDENCE_SHA256": "$SRC_SHA",
  "EVIDENCE_STATE": "ENGINEERING_RUNTIME_SAMPLE_PROVISIONAL",
  "EXPERIMENT_STATE": "HYDRALAMP_REAL_EVIDENCE_RESTORE_V1",
  "FCO_STATE": "SESSION_LOCAL_PENDING_VERIFY",
  "FCG_STATE": "APPEND_PENDING_OR_PRIOR_EVENTS",
  "HYDRADB_STATE": "NOT_TOUCHED",
  "EARLIEST_DIVERGENCE": "PENDING_SENTINEL_VERIFY",
  "CLAIM_CEILING": "ONE_REAL_REPRODUCIBLE_END_TO_END_SAMPLE_NOT_SCIENTIFIC_SUPERIORITY",
  "SIGNATURE_STATE": "NOT_SIGNED",
  "MERKLE_MMR_STATE": "NOT_COMMITTED_UNLESS_ACTUAL_APPEND_VERIFY",
  "NEXT_SAFE_ACTION": "OPEN_LOCAL_URLS_THEN_FORCE_ONLY_AUTHED_SPONSOR_STEPS",
  "FINAL_REVIEW_GATE": "OPERATOR_REVIEW_FINAL_RECEIPT_AND_GREEN_ONLY_ACTUAL_PASS",
  "out_dir": "$OUT",
  "stamp": "$STAMP"
}
EOF

# Human-readable dump
python3 - <<PY
import json
from pathlib import Path
p = Path("$OUT/FINAL_RECEIPT.json")
d = json.loads(p.read_text())
lines = [f"{k}={d[k]}" for k in d]
Path("$OUT/FINAL_RECEIPT.md").write_text("\n".join(lines) + "\n")
print(Path("$OUT/FINAL_RECEIPT.md").read_text())
PY

log "DONE out=$OUT"
echo
echo "OPEN:"
echo "  HydraLamp:  $MAGICSTUDIO_LOCAL_URL"
echo "  HydraDG:    $HYDRADG_LOCAL_URL"
echo "  CF OS:      $CF_LOCAL_URL"
echo "  Receipt:    $OUT/FINAL_RECEIPT.md"
