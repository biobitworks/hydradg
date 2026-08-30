"""Centralized secret source registry — presence and resolution metadata only."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Ollarma SSOT for resolution + keychain
OLLARMA_SRC = Path("/Users/byron/projects/active/ollarma/src")
if str(OLLARMA_SRC) not in sys.path:
    sys.path.insert(0, str(OLLARMA_SRC))

try:
    from ollarma import credentials as ollarma_creds
except ImportError:
    ollarma_creds = None  # type: ignore

PRECEDENCE = [
    "process_env",
    "portfolio_keys_env",
    "project_root_env",
    "project_env_local",
    "application_env",
    "application_env_local",
    "provider_standard_file",
    "keychain",
]

SECRET_SOURCE_REGISTRY: list[dict[str, Any]] = [
    {"path": Path.home() / ".config/ai-keys/keys.env", "source_class": "portfolio_keys_env"},
    {"path": Path("/Users/byron/projects/.env"), "source_class": "project_root_env"},
    {"path": Path("/Users/byron/projects/active/ollarma/.env"), "source_class": "application_env"},
    {"path": Path("/Users/byron/projects/active/hydradg/.env"), "source_class": "application_env"},
    {"path": Path("/Users/byron/projects/active/hydradg/.env.local"), "source_class": "application_env_local"},
    {"path": Path("/Users/byron/projects/active/hydradg/apps/hydradg-web/.env"), "source_class": "application_env"},
    {"path": Path("/Users/byron/projects/active/hydradg/apps/hydradg-web/.env.local"), "source_class": "application_env_local"},
    {"path": Path("/Users/byron/projects/active/biocustody/.env"), "source_class": "application_env"},
    {"path": Path("/Users/byron/projects/active/biocustody/.env.local"), "source_class": "application_env_local"},
    {"path": Path("/Users/byron/projects/active/protein-hinge/.env"), "source_class": "application_env"},
    {"path": Path("/Users/byron/projects/active/protein-hinge/.env.local"), "source_class": "application_env_local"},
    {"path": Path("/Users/byron/projects/active/seedgraph/.env"), "source_class": "application_env"},
    {"path": Path("/Users/byron/projects/active/seedgraph/.env.local"), "source_class": "application_env_local"},
    {"path": Path("/Users/byron/projects/active/gettingsciencedone/.env"), "source_class": "application_env"},
    {"path": Path("/Users/byron/projects/active/gettingsciencedone/.env.local"), "source_class": "application_env_local"},
    {"path": Path.home() / ".kaggle/kaggle.json", "source_class": "provider_standard_file", "provider": "KAGGLE"},
]

EXCLUDE_SCAN = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build",
    ".next", "cache", "content_store", "seedgraph_delta",
}

CORE_CREDENTIALS = [
    ("DAYTONA_API_KEY", "DAYTONA", "DAYTONA_API_TOKEN"),
    ("KAGGLE_USERNAME", "KAGGLE", "KAGGLE_KEY"),
    ("MISTRAL_API_KEY", "MISTRAL",),
    ("HF_TOKEN", "HUGGINGFACE", "HUGGING_FACE_HUB_TOKEN"),
    ("OPENAI_API_KEY", "OPENAI",),
    ("ANTHROPIC_API_KEY", "ANTHROPIC",),
    ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE", "CLOUDFLARE_API_KEY", "CLOUDFLARE_ACCOUNT_ID"),
    ("VERCEL_TOKEN", "VERCEL",),
    ("NEBIUS_API_KEY", "NEBIUS",),
]


def _parse_env_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    if not path.is_file():
        return keys
    try:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" in line:
                keys.add(line.split("=", 1)[0].strip())
    except OSError:
        pass
    return keys


def _kaggle_json_keys_present(path: Path) -> dict[str, bool]:
    if not path.is_file():
        return {"username": False, "key": False}
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
        u = str(blob.get("KAGGLE_USERNAME") or blob.get("username") or "").strip()
        k = str(blob.get("KAGGLE_KEY") or blob.get("key") or "").strip()
        return {"username": bool(u), "key": bool(k)}
    except (OSError, json.JSONDecodeError):
        return {"username": False, "key": False}


def discover_env_files(root: Path, max_depth: int = 4) -> list[Path]:
    found: list[Path] = []
    root = root.resolve()
    for depth, dirpath, dirnames, filenames in _walk_limited(root, max_depth):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_SCAN and not d.startswith(".git")]
        for fn in filenames:
            if fn in {".env", ".env.local", ".envrc"} or fn.endswith(".env.example"):
                found.append(Path(dirpath) / fn)
    return sorted(set(found))


def _walk_limited(root: Path, max_depth: int):
    root_parts = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root):
        depth = len(Path(dirpath).parts) - root_parts
        if depth > max_depth:
            dirnames.clear()
            continue
        yield depth, dirpath, dirnames, filenames


def scan_variable_names_in_code(root: Path) -> set[str]:
    pattern = re.compile(
        r"(?:os\.environ\.get|os\.getenv|environ\[)\s*[\(\[]?\s*['\"]([A-Z][A-Z0-9_]{2,})['\"]"
    )
    names: set[str] = set()
    for path in root.rglob("*"):
        if any(x in path.parts for x in EXCLUDE_SCAN):
            continue
        if path.suffix not in {".py", ".ts", ".tsx", ".js", ".sh", ".yaml", ".yml", ".md"}:
            continue
        if path.stat().st_size > 500_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        names.update(pattern.findall(text))
        for m in re.finditer(r"^([A-Z][A-Z0-9_]{2,})=\s*$", text, re.M):
            names.add(m.group(1))
    return names


@dataclass
class CredentialResolution:
    credential_name: str
    provider: str
    source_class: str | None
    source_path_or_store: str | None
    variable_present: bool
    candidate_count: int
    terminal_state: str
    resolution_precedence: list[str]


def _find_candidates(credential_name: str) -> list[tuple[str, str]]:
    """Return (source_class, path) for each source containing the variable name."""
    hits: list[tuple[str, str]] = []
    if os.environ.get(credential_name, "").strip():
        hits.append(("process_env", "process_environment"))
    for entry in SECRET_SOURCE_REGISTRY:
        path: Path = entry["path"]
        sc = entry["source_class"]
        if path.name == "kaggle.json":
            k = _kaggle_json_keys_present(path)
            if credential_name == "KAGGLE_USERNAME" and k["username"]:
                hits.append((sc, str(path)))
            if credential_name == "KAGGLE_KEY" and k["key"]:
                hits.append((sc, str(path)))
            continue
        if credential_name in _parse_env_keys(path):
            hits.append((sc, str(path)))
    if ollarma_creds and credential_name not in {"KAGGLE_USERNAME", "KAGGLE_KEY"}:
        spec = ollarma_creds.PROVIDERS.get("daytona")
        kc_map = {
            "DAYTONA_API_KEY": ("daytona", "ollarma-daytona"),
            "ANTHROPIC_API_KEY": ("anthropic", "ollarma-anthropic"),
            "OPENAI_API_KEY": ("openai", "ollarma-openai"),
            "NEBIUS_API_KEY": ("nebius", "ollarma-nebius"),
        }
        if credential_name in kc_map:
            _, kc = kc_map[credential_name]
            val, src = ollarma_creds.resolve_key_with_source(credential_name, kc)
            if val and src == "keychain":
                hits.append(("keychain", f"keychain:{kc}"))
    return hits


def resolve_credential_metadata(credential_name: str, provider: str) -> CredentialResolution:
    if credential_name in {"KAGGLE_USERNAME", "KAGGLE_KEY"} and ollarma_creds:
        creds, src = ollarma_creds.resolve_kaggle_with_source()
        if creds:
            path = str(ollarma_creds.kaggle_json_path()) if src == "kaggle.json" else src
            return CredentialResolution(
                credential_name=credential_name,
                provider=provider,
                source_class=src,
                source_path_or_store=path,
                variable_present=True,
                candidate_count=1,
                terminal_state="PRESENT_UNVERIFIED",
                resolution_precedence=PRECEDENCE,
            )
    hits = _find_candidates(credential_name)
    if ollarma_creds:
        kc_services = {
            "DAYTONA_API_KEY": "ollarma-daytona",
            "ANTHROPIC_API_KEY": "ollarma-anthropic",
            "OPENAI_API_KEY": "ollarma-openai",
            "NEBIUS_API_KEY": "ollarma-nebius",
        }
        if credential_name in kc_services:
            val, src = ollarma_creds.resolve_key_with_source(credential_name, kc_services[credential_name])
            if val:
                path = {
                    "env": "process_environment",
                    "keys.env": str(ollarma_creds.keys_env_path()),
                    "keychain": f"keychain:{kc_services[credential_name]}",
                }.get(src, src)
                return CredentialResolution(
                    credential_name=credential_name,
                    provider=provider,
                    source_class=src,
                    source_path_or_store=path,
                    variable_present=True,
                    candidate_count=max(1, len(hits)),
                    terminal_state="PRESENT_UNVERIFIED",
                    resolution_precedence=PRECEDENCE,
                )
    if not hits:
        return CredentialResolution(
            credential_name=credential_name,
            provider=provider,
            source_class=None,
            source_path_or_store=None,
            variable_present=False,
            candidate_count=0,
            terminal_state="NOT_FOUND",
            resolution_precedence=PRECEDENCE,
        )
    unique_paths = {h[1] for h in hits}
    if len(unique_paths) > 1:
        terminal = "MULTIPLE_CANDIDATES"
    else:
        terminal = "PRESENT_UNVERIFIED"
    sc, path = hits[0]
    return CredentialResolution(
        credential_name=credential_name,
        provider=provider,
        source_class=sc,
        source_path_or_store=path,
        variable_present=True,
        candidate_count=len(unique_paths),
        terminal_state=terminal,
        resolution_precedence=PRECEDENCE,
    )


def resolve_secret_source(credential_name: str) -> str | None:
    """GUM Doctor compatible: returns source class/path tag, never the value."""
    meta = resolve_credential_metadata(credential_name, "UNKNOWN")
    if not meta.variable_present:
        return None
    return meta.source_class or meta.source_path_or_store
