#!/usr/bin/env python3
"""Studio pull deployer for HydraDG hydradg-web (exact SHA only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

RUNTIME = Path("/Volumes/magicBLACKbox/hydradg/services/hydradg-test")
RELEASES = RUNTIME / "releases"
CURRENT = RUNTIME / "current"
PREVIOUS = RUNTIME / "previous"
STATE = RUNTIME / "state"
LOGS = RUNTIME / "logs"
RECEIPTS = RUNTIME / "receipts"
NPM_CACHE = RUNTIME / "cache" / "npm"
TMP = RUNTIME / "tmp"
LOCK = STATE / "deploy.lock"
DEPLOYED_SHA_FILE = STATE / "deployed_sha"
SERVICE = "com.biobitworks.hydradg-test"
WEB_REL = Path("apps/hydradg-web")
SOURCE_REPO_DEFAULT = Path("/Users/byron/projects/active/hydradg")
DEPLOY_REF = "origin/deploy/studio-test"
NODE = "/opt/homebrew/bin/node"
NPM = "/opt/homebrew/bin/npm"
PYTHON = "/opt/homebrew/bin/python3"
HEALTHCHECK = SOURCE_REPO_DEFAULT / "ops" / "studio-test" / "healthcheck.py"


def sh(cmd: list[str], cwd: Path | None = None, env: dict | None = None) -> str:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    merged.setdefault("npm_config_cache", str(NPM_CACHE))
    merged.setdefault("TMPDIR", str(TMP))
    merged.setdefault("TMP", str(TMP))
    merged.setdefault("TEMP", str(TMP))
    proc = subprocess.run(cmd, cwd=cwd, env=merged, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"cmd failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr}\n{proc.stdout}")
    return proc.stdout.strip()


def ensure_runtime() -> None:
    if not RUNTIME.exists():
        raise SystemExit(f"RUNTIME_MISSING {RUNTIME}")
    for p in (RELEASES, STATE, LOGS, RECEIPTS, NPM_CACHE, TMP):
        p.mkdir(parents=True, exist_ok=True)
    # free-space floors
    st = os.statvfs("/Volumes/magicBLACKbox")
    free_bb = st.f_bavail * st.f_frsize
    if free_bb < 20 * 1024**3:
        raise SystemExit(f"MAGICBLACKBOX_FREE_TOO_LOW bytes={free_bb}")
    st_root = os.statvfs("/")
    free_root = st_root.f_bavail * st_root.f_frsize
    if free_root < 1 * 1024**3:
        print(f"WARNING_ROOT_FREE_LOW bytes={free_root}", file=sys.stderr)


class DeployLock:
    def __enter__(self):
        STATE.mkdir(parents=True, exist_ok=True)
        if LOCK.exists():
            try:
                old = int(LOCK.read_text().strip() or "0")
                os.kill(old, 0)
                raise SystemExit(f"DEPLOY_LOCKED_BY_PID={old}")
            except (ProcessLookupError, ValueError, PermissionError):
                pass
        LOCK.write_text(str(os.getpid()))
        return self

    def __exit__(self, *exc):
        try:
            if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
                LOCK.unlink()
        except OSError:
            pass


def resolve_target_sha(repo: Path, sha: str | None) -> str:
    sh(["git", "fetch", "origin", "--prune"], cwd=repo)
    if sha:
        return sha.strip().lower()
    return sh(["git", "rev-parse", DEPLOY_REF], cwd=repo).lower()


def deployed_sha() -> str | None:
    if DEPLOYED_SHA_FILE.exists():
        return DEPLOYED_SHA_FILE.read_text().strip().lower() or None
    if CURRENT.is_symlink() or CURRENT.exists():
        try:
            return sh(["git", "rev-parse", "HEAD"], cwd=CURRENT).lower()
        except Exception:
            return None
    return None


def materialize_release(repo: Path, sha: str) -> Path:
    dest = RELEASES / sha
    if dest.exists():
        got = sh(["git", "rev-parse", "HEAD"], cwd=dest).lower()
        if got != sha:
            raise SystemExit(f"CORRUPT_RELEASE {dest} head={got} expected={sha}")
        return dest
    dest.mkdir(parents=True)
    # fresh clone from local source for speed, then fetch exact sha
    sh(["git", "clone", "--shared", str(repo), str(dest)])
    sh(["git", "fetch", "origin", sha], cwd=dest)
    sh(["git", "checkout", "--detach", sha], cwd=dest)
    got = sh(["git", "rev-parse", "HEAD"], cwd=dest).lower()
    if got != sha:
        raise SystemExit(f"CHECKOUT_MISMATCH got={got} expected={sha}")
    return dest


def build_web(release: Path) -> None:
    web = release / WEB_REL
    if not web.exists():
        raise SystemExit(f"WEB_MISSING {web}")
    env = {
        "npm_config_cache": str(NPM_CACHE),
        "TMPDIR": str(TMP),
        "TMP": str(TMP),
        "TEMP": str(TMP),
        "PATH": f"/opt/homebrew/bin:/usr/bin:/bin:{os.environ.get('PATH','')}",
    }
    sh([NPM, "ci"], cwd=web, env=env)
    sh([NPM, "run", "typecheck"], cwd=web, env=env)
    sh([NPM, "run", "build"], cwd=web, env=env)


def canary_smoke(release: Path, port: int = 3011) -> None:
    web = release / WEB_REL
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"/opt/homebrew/bin:/usr/bin:/bin:{os.environ.get('PATH','')}",
            "PORT": str(port),
            "TMPDIR": str(TMP),
            "npm_config_cache": str(NPM_CACHE),
        }
    )
    log = LOGS / f"canary-{port}.log"
    with log.open("ab") as fh:
        proc = subprocess.Popen(
            [NPM, "run", "start", "--", "-H", "127.0.0.1", "-p", str(port)],
            cwd=web,
            env=env,
            stdout=fh,
            stderr=fh,
            start_new_session=True,
        )
    try:
        base = f"http://127.0.0.1:{port}"
        for _ in range(60):
            try:
                with urllib.request.urlopen(base + "/", timeout=2) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError("canary failed to become healthy")
        sh([PYTHON, str(HEALTHCHECK), "--base", base, "--pages-only"])
    finally:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)


def activate(release: Path, sha: str) -> None:
    if CURRENT.exists() or CURRENT.is_symlink():
        if PREVIOUS.exists() or PREVIOUS.is_symlink():
            PREVIOUS.unlink()
        PREVIOUS.symlink_to(CURRENT.resolve() if CURRENT.is_symlink() else CURRENT)
        CURRENT.unlink()
    CURRENT.symlink_to(release)
    DEPLOYED_SHA_FILE.write_text(sha + "\n")


def restart_web_server() -> None:
    """Restart the studio-test web process after symlink activation.

    Preferred path is launchd KeepAlive for com.biobitworks.hydradg-test.
    On magicSTUDIObox, launchd-managed next start has been observed to hang
    without binding :3000, so fall back to the nohup supervise loop in
    ops/studio-test/bin/hydradg-test-supervise-loop.sh.
    """
    uid = os.getuid()
    supervise = SOURCE_REPO_DEFAULT / "ops" / "studio-test" / "bin" / "hydradg-test-supervise-loop.sh"
    # Always clear stale listeners before restart
    subprocess.run(["pkill", "-f", "next start -H 127.0.0.1 -p 3000"], check=False)
    time.sleep(1)
    try:
        sh(["launchctl", "kickstart", "-k", f"gui/{uid}/{SERVICE}"])
        # If launchd is the hanging path, detect and fall through
        time.sleep(3)
        try:
            with urllib.request.urlopen("http://127.0.0.1:3000/", timeout=2) as resp:
                if resp.status == 200:
                    return
        except Exception:
            pass
    except RuntimeError:
        pass

    # Stop prior supervise loop if recorded
    pid_file = STATE / "supervise.pid"
    if pid_file.exists():
        try:
            os.kill(int(pid_file.read_text().strip()), signal.SIGTERM)
        except (ProcessLookupError, ValueError, OSError):
            pass
    subprocess.run(["pkill", "-f", "hydradg-test-supervise-loop"], check=False)
    time.sleep(1)
    if not supervise.exists():
        raise RuntimeError(f"missing supervise wrapper {supervise}")
    proc = subprocess.Popen(
        ["/bin/bash", str(supervise)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        env={
            **os.environ,
            "HOME": str(Path.home()),
            "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
            "npm_config_cache": str(NPM_CACHE),
            "TMPDIR": str(TMP),
        },
    )
    pid_file.write_text(str(proc.pid) + "\n")


def launchctl_kick() -> None:
    restart_web_server()


def wait_local(timeout: int = 60) -> None:
    for _ in range(timeout):
        try:
            with urllib.request.urlopen("http://127.0.0.1:3000/", timeout=2) as resp:
                if resp.status == 200:
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError("localhost:3000 failed health after activation")


def verify_tailscale() -> str:
    url = "https://magicstudiobox.tail0cf9bb.ts.net/"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return str(resp.status)
    except Exception as exc:
        return f"FAIL:{exc}"


def write_receipt(payload: dict) -> Path:
    raw = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    digest = hashlib.sha256(raw.encode()).hexdigest()
    payload = dict(payload)
    payload["receipt_sha256"] = digest
    raw = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path = RECEIPTS / f"deploy_{payload['deployed_sha'][:12]}_{int(time.time())}.json"
    path.write_text(raw)
    return path


def rollback() -> None:
    if not PREVIOUS.exists() and not PREVIOUS.is_symlink():
        raise SystemExit("NO_PREVIOUS_RELEASE")
    target = PREVIOUS.resolve()
    sha = sh(["git", "rev-parse", "HEAD"], cwd=target).lower()
    if CURRENT.exists() or CURRENT.is_symlink():
        CURRENT.unlink()
    CURRENT.symlink_to(target)
    DEPLOYED_SHA_FILE.write_text(sha + "\n")
    launchctl_kick()
    wait_local()
    print("ROLLBACK_OK", sha)


def cmd_check(repo: Path) -> int:
    ensure_runtime()
    sh(["git", "fetch", "origin", "--prune"], cwd=repo)
    target = resolve_target_sha(repo, None)
    current = deployed_sha()
    print(f"DEPLOY_REF={DEPLOY_REF}")
    print(f"DEPLOY_REF_SHA={target}")
    print(f"DEPLOYED_SHA={current or 'NONE'}")
    print(f"DEPLOY_PARITY={'PASS' if current == target else 'DRIFT'}")
    print(f"CURRENT_LINK={CURRENT}")
    return 0 if current == target else 2


def cmd_once(repo: Path, sha: str | None, force: bool) -> int:
    ensure_runtime()
    with DeployLock():
        target = resolve_target_sha(repo, sha)
        current = deployed_sha()
        if current == target and not force:
            print(f"NOOP deployed={current}")
            return 0
        print(f"DEPLOY_START target={target} previous={current}")
        release = materialize_release(repo, target)
        build_web(release)
        canary_smoke(release)
        activate(release, target)
        try:
            launchctl_kick()
            wait_local()
            sh([PYTHON, str(HEALTHCHECK), "--base", "http://127.0.0.1:3000", "--pages-only"])
            ts = verify_tailscale()
            if ts != "200":
                raise RuntimeError(f"tailscale health {ts}")
        except Exception as exc:
            print(f"ACTIVATION_FAIL {exc}; rolling back")
            try:
                rollback()
            except Exception as rb:
                print(f"ROLLBACK_FAIL {rb}")
            raise
        receipt = write_receipt(
            {
                "schema": "hydradg.studio_test_deploy_receipt.v1",
                "deployed_sha": target,
                "previous_sha": current,
                "release_path": str(release),
                "service": SERVICE,
                "localhost_health": "200",
                "tailscale_health": "200",
                "signature_state": "NOT_SIGNED",
                "merkle_mmr_state": "NOT_COMMITTED",
                "hashes_are_signatures": False,
            }
        )
        print("DEPLOY_OK", target, receipt)
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=SOURCE_REPO_DEFAULT)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sha")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--rollback", action="store_true")
    args = ap.parse_args()
    if args.rollback:
        rollback()
        return 0
    if args.check:
        return cmd_check(args.repo)
    if args.once:
        return cmd_once(args.repo, args.sha, args.force)
    ap.error("specify --once, --check, or --rollback")
    return 2


if __name__ == "__main__":
    sys.exit(main())
