#!/usr/bin/env python3
"""Prove two deploy.py invocations cannot both enter the mutable section."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/Users/byron/projects/active/hydradg")
DEPLOY = REPO / "ops" / "studio-test" / "deploy.py"
PYTHON = "/opt/homebrew/bin/python3"
RUNTIME = Path("/Volumes/magicBLACKbox/hydradg/services/hydradg-test")
LOCK = RUNTIME / "state" / "deploy.lock"


def main() -> int:
    # Holder: acquire flock and sleep (simulate long deploy)
    holder = subprocess.Popen(
        [
            PYTHON,
            "-c",
            (
                "import fcntl, os, time, pathlib\n"
                f"lock = pathlib.Path({str(LOCK)!r})\n"
                "lock.parent.mkdir(parents=True, exist_ok=True)\n"
                "fh = open(lock, 'a+')\n"
                "fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)\n"
                "fh.seek(0); fh.truncate(); fh.write(str(os.getpid())+'\\n'); fh.flush()\n"
                "print('HOLDER_LOCKED', flush=True)\n"
                "time.sleep(8)\n"
            ),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    # Wait until holder reports lock
    deadline = time.time() + 5
    locked = False
    buf = ""
    while time.time() < deadline:
        line = holder.stdout.readline() if holder.stdout else ""
        if line:
            buf += line
            if "HOLDER_LOCKED" in line:
                locked = True
                break
        if holder.poll() is not None:
            break
        time.sleep(0.05)
    if not locked:
        holder.kill()
        print("FAIL holder did not acquire lock:", buf)
        return 1

    challenger = subprocess.run(
        [PYTHON, str(DEPLOY), "--repo", str(REPO), "--once"],
        text=True,
        capture_output=True,
        timeout=60,
    )
    out = (challenger.stdout or "") + (challenger.stderr or "")
    print("---CHALLENGER_RC---", challenger.returncode)
    print(out)
    holder.wait(timeout=15)

    if challenger.returncode != 0:
        print("SINGLE_WRITER_TEST=FAIL nonzero_exit")
        return 1
    if "LOCK_BUSY" not in out:
        print("SINGLE_WRITER_TEST=FAIL missing_LOCK_BUSY")
        return 1
    if "DEPLOY_START" in out or "DEPLOY_OK" in out:
        print("SINGLE_WRITER_TEST=FAIL challenger_mutated")
        return 1
    print("SINGLE_WRITER_TEST=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
