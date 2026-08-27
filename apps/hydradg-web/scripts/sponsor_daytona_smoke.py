#!/usr/bin/env python3
"""Bounded Daytona ephemeral sandbox smoke.

Never prints secret values. Classifies output as DETERMINISTIC_TOOL_OUTPUT.
Does not run scientific/model experiments. magicSTUDIObox remains scientific authority.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

SMOKE_CMD = (
    'python -c "import platform,hashlib; print(platform.python_version()); '
    "print(hashlib.sha256(b'hydradg-daytona-smoke').hexdigest())\""
)
EXPECTED_PAYLOAD_HASH = hashlib.sha256(b"hydradg-daytona-smoke").hexdigest()
SECRET_KEY_RE = ("api_key", "apikey", "token", "authorization", "secret", "password", "bearer")


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def key_status() -> str:
    v = (os.environ.get("DAYTONA_API_KEY") or "").strip()
    if not v:
        return "MISSING"
    low = v.lower()
    if low in {"", "your_actual_key_here", "changeme", "replace_me", "xxx", "insert_key_here"}:
        return "INVALID_PLACEHOLDER"
    if low.startswith("your_") and low.endswith("_here"):
        return "INVALID_PLACEHOLDER"
    if v.startswith("<") and v.endswith(">"):
        return "INVALID_PLACEHOLDER"
    return "PRESENT"


def redact(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if any(s in str(k).lower() for s in SECRET_KEY_RE):
                out[k] = "REDACTED"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str) and os.environ.get("DAYTONA_API_KEY") and obj == os.environ.get("DAYTONA_API_KEY"):
        return "REDACTED"
    return obj


def public_attr(obj, name, default=None):
    try:
        v = getattr(obj, name, default)
        if callable(v):
            return default
        return v
    except Exception:
        return default


def to_public_dict(obj) -> dict:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return redact(obj)
    data = {}
    for name in (
        "id",
        "name",
        "state",
        "snapshot",
        "snapshot_id",
        "image",
        "language",
        "target",
        "created_at",
        "updated_at",
        "cpu",
        "memory",
        "disk",
        "os",
        "result",
        "exit_code",
        "stdout",
        "stderr",
        "artifacts",
        "cwd",
        "cmd",
        "command",
        "session_id",
        "execution_id",
    ):
        v = public_attr(obj, name)
        if v is not None:
            data[name] = v
    if hasattr(obj, "model_dump"):
        try:
            data.update(obj.model_dump())
        except Exception:
            pass
    elif hasattr(obj, "to_dict"):
        try:
            data.update(obj.to_dict())
        except Exception:
            pass
    return redact(data)


def write_receipt(path: Path, receipt: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(receipt, indent=2, default=str) + "\n"
    path.write_text(body, encoding="utf-8")
    path.with_suffix(".sha256").write_text(sha256_bytes(body.encode("utf-8")) + "\n", encoding="utf-8")


def main() -> int:
    repo = Path(__file__).resolve().parents[3]
    out_dir = repo / "eval" / "agent_native_sponsors_20260827" / "daytona"
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = out_dir / "DAYTONA_SMOKE_RECEIPT.json"
    started = utcnow()
    secret = key_status()
    api_url = (os.environ.get("DAYTONA_API_URL") or "https://app.daytona.io/api").strip()

    print(f"DAYTONA_API_KEY={secret}")
    print(f"DAYTONA_API_URL={api_url}")

    base = {
        "schema": "infrastructure.daytona.smoke_receipt.v1",
        "mission_id": "ANB-INFRA-DAYTONA-SMOKE-001",
        "provider": "Daytona",
        "lane": "INFRASTRUCTURE",
        "anb_sponsor": False,
        "operation": "ephemeral_sandbox_exec",
        "started_at": started,
        "completed_at": None,
        "DAYTONA_STATE": "CONFIGURED" if secret == "PRESENT" else "BLOCKED",
        "secret_state": secret,
        "required_env_names": ["DAYTONA_API_KEY"],
        "api_url": api_url,
        "official_docs": "https://www.daytona.io/docs/en/python-sdk/",
        "smoke_command": SMOKE_CMD,
        "scientific_execution_authority": "magicSTUDIObox.local",
        "scientific_experiments_on_daytona": False,
        "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
        "claim_ceiling": "DETERMINISTIC_TOOL_OUTPUT",
        "promoted_to_verified_empirical_result": False,
        "hydradg_independent_recompute": {
            "payload": "hydradg-daytona-smoke",
            "expected_sha256": EXPECTED_PAYLOAD_HASH,
            "match": None,
        },
        "workspace_id": None,
        "execution_id": None,
        "image_or_runtime": None,
        "exit_code": None,
        "stdout_sha256": None,
        "raw_response_sha256": None,
        "destroyed": False,
        "status": "BLOCKED",
        "error_code": None,
        "error_summary": None,
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED",
    }

    if secret != "PRESENT":
        base["completed_at"] = utcnow()
        base["DAYTONA_STATE"] = "BLOCKED"
        base["status"] = "BLOCKED"
        base["error_code"] = "DAYTONA_API_KEY_" + secret
        base["error_summary"] = "Daytona API key not usable; no sandbox created."
        write_receipt(receipt_path, base)
        print("DAYTONA_STATE=BLOCKED")
        print("DAYTONA_MISSION=BLOCKED")
        return 2

    sandbox = None
    daytona = None
    try:
        from daytona import Daytona, DaytonaConfig
    except Exception as e:
        base["completed_at"] = utcnow()
        base["status"] = "ERROR"
        base["DAYTONA_STATE"] = "ERROR"
        base["error_code"] = "DAYTONA_SDK_IMPORT_FAILED"
        base["error_summary"] = str(e)[:200]
        write_receipt(receipt_path, base)
        print("DAYTONA_STATE=ERROR")
        print("DAYTONA_MISSION=ERROR")
        return 1

    try:
        os.environ.setdefault("DAYTONA_USE_DEPRECATED_POLLING", "true")
        config = DaytonaConfig(api_url=api_url)
        daytona = Daytona(config)

        listed = None
        try:
            listed = daytona.list()
            base["connectivity_state"] = "PASS"
            base["list_probe"] = {
                "type": type(listed).__name__,
                "count": len(listed) if hasattr(listed, "__len__") else None,
            }
        except Exception as e:
            base["connectivity_state"] = "ERROR"
            base["completed_at"] = utcnow()
            base["status"] = "ERROR"
            base["DAYTONA_STATE"] = "ERROR"
            base["error_code"] = "DAYTONA_CONNECTIVITY_FAILED"
            base["error_summary"] = str(e)[:200]
            write_receipt(receipt_path, base)
            print("DAYTONA_STATE=ERROR")
            print("DAYTONA_MISSION=ERROR")
            return 1

        create_kwargs = {}
        try:
            from daytona import CreateSandboxFromSnapshotParams

            params = CreateSandboxFromSnapshotParams(
                language="python",
                auto_delete_interval=10,
            )
            sandbox = daytona.create(params, timeout=90)
        except TypeError:
            sandbox = daytona.create()
        except Exception:
            sandbox = daytona.create()

        sandbox_pub = to_public_dict(sandbox)
        workspace_id = sandbox_pub.get("id") or public_attr(sandbox, "id")
        base["workspace_id"] = workspace_id
        base["image_or_runtime"] = (
            sandbox_pub.get("snapshot")
            or sandbox_pub.get("image")
            or sandbox_pub.get("language")
            or sandbox_pub.get("os")
        )
        base["sandbox_public"] = {
            k: sandbox_pub[k]
            for k in ("id", "state", "snapshot", "image", "language", "target", "created_at")
            if k in sandbox_pub
        }

        started_exec = utcnow()
        response = sandbox.process.exec(SMOKE_CMD, timeout=60)
        ended_exec = utcnow()
        resp_pub = to_public_dict(response)
        raw_json = json.dumps(resp_pub, default=str, sort_keys=True)
        stdout = (
            resp_pub.get("result")
            or resp_pub.get("stdout")
            or getattr(response, "result", "")
            or ""
        )
        if not isinstance(stdout, str):
            stdout = str(stdout)
        exit_code = resp_pub.get("exit_code")
        if exit_code is None:
            exit_code = public_attr(response, "exit_code")

        stdout_sha = sha256_text(stdout)
        raw_sha = sha256_text(raw_json)
        lines = [ln.strip() for ln in stdout.strip().splitlines() if ln.strip()]
        observed_hash = lines[1] if len(lines) >= 2 else None
        recompute_match = observed_hash == EXPECTED_PAYLOAD_HASH if observed_hash else False

        exec_id = (
            resp_pub.get("execution_id")
            or resp_pub.get("session_id")
            or resp_pub.get("id")
            or workspace_id
        )

        base.update(
            {
                "execution_id": exec_id,
                "exec_started_at": started_exec,
                "exec_completed_at": ended_exec,
                "exit_code": exit_code,
                "stdout_sha256": stdout_sha,
                "raw_response_sha256": raw_sha,
                "python_version_observed": lines[0] if lines else None,
                "payload_hash_observed": observed_hash,
            }
        )
        base["hydradg_independent_recompute"]["match"] = recompute_match
        base["hydradg_independent_recompute"]["observed_sha256"] = observed_hash

        ok = (exit_code in (0, None)) and recompute_match and bool(workspace_id)
        if exit_code not in (0, None) and exit_code != 0:
            base["status"] = "ERROR"
            base["error_code"] = "SMOKE_NONEZERO_EXIT"
            base["error_summary"] = f"exit_code={exit_code}"
        elif not recompute_match:
            base["status"] = "NEGATIVE"
            base["error_code"] = "PAYLOAD_HASH_MISMATCH"
            base["error_summary"] = "Independent HydraDG recompute did not match Daytona stdout hash line."
        elif ok:
            base["status"] = "PASS"
            base["DAYTONA_STATE"] = "LIVE_PASS"
        else:
            base["status"] = "ERROR"
            base["error_code"] = "SMOKE_INCOMPLETE"
            base["error_summary"] = "Missing workspace id or incomplete stdout."

        (out_dir / "raw").mkdir(exist_ok=True)
        raw_path = out_dir / "raw" / "DAYTONA_EXEC_RESPONSE.json"
        raw_path.write_text(raw_json + "\n", encoding="utf-8")
        base["raw_response_path"] = str(raw_path.relative_to(repo))

    except TimeoutError as e:
        base["status"] = "TIMEOUT"
        base["DAYTONA_STATE"] = "ERROR"
        base["error_code"] = "TIMEOUT"
        base["error_summary"] = str(e)[:200]
    except Exception as e:
        msg = str(e)
        is_timeout = "TIMEOUT" in msg.upper() or "timed out" in msg.lower()
        base["status"] = "TIMEOUT" if is_timeout else "ERROR"
        base["DAYTONA_STATE"] = "ERROR"
        base["error_code"] = "TIMEOUT" if is_timeout else "DAYTONA_SMOKE_FAILED"
        base["error_summary"] = msg[:200]
        base["traceback_sha256"] = sha256_text(traceback.format_exc())
    finally:
        destroyed = False
        destroy_error = None
        if sandbox is not None and daytona is not None:
            try:
                daytona.delete(sandbox)
                destroyed = True
            except Exception as e:
                try:
                    if hasattr(sandbox, "delete"):
                        sandbox.delete()
                        destroyed = True
                    elif hasattr(sandbox, "stop"):
                        sandbox.stop()
                        destroyed = True
                    else:
                        raise e
                except Exception as e2:
                    destroy_error = str(e2)[:200]
        base["destroyed"] = destroyed
        if destroy_error:
            base["destroy_error"] = destroy_error
        base["completed_at"] = utcnow()
        write_receipt(receipt_path, base)

    print("DAYTONA_STATE=" + str(base.get("DAYTONA_STATE")))
    print("DAYTONA_MISSION=" + str(base.get("status")))
    print("WORKSPACE_ID=" + str(base.get("workspace_id") or "null"))
    print("EXIT_CODE=" + str(base.get("exit_code")))
    print("STDOUT_SHA256=" + str(base.get("stdout_sha256") or "null"))
    print("DESTROYED=" + str(base.get("destroyed")))
    return 0 if base.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
