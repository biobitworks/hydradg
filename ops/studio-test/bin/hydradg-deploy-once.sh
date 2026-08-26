#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/bin:/bin"
export HOME="/Users/byron"
RUNTIME="/Volumes/magicBLACKbox/hydradg/services/hydradg-test"
export npm_config_cache="$RUNTIME/cache/npm"
export TMPDIR="$RUNTIME/tmp"
exec /opt/homebrew/bin/python3 - <<'PY'
import os, signal, subprocess, sys
os.environ.setdefault("HOME", "/Users/byron")
os.environ["npm_config_cache"] = "/Volumes/magicBLACKbox/hydradg/services/hydradg-test/cache/npm"
os.environ["TMPDIR"] = "/Volumes/magicBLACKbox/hydradg/services/hydradg-test/tmp"

def _alarm(signum, frame):
    raise SystemExit("DEPLOY_ONCE_TIMEOUT")

signal.signal(signal.SIGALRM, _alarm)
signal.alarm(120)
cmd = [
    "/opt/homebrew/bin/python3",
    "/Users/byron/projects/active/hydradg/ops/studio-test/deploy.py",
    "--repo",
    "/Users/byron/projects/active/hydradg",
    "--once",
]
raise SystemExit(subprocess.call(cmd))
PY
