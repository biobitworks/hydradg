#!/usr/bin/env bash
set -euo pipefail

# Hack Hydra Best Use v2 — explicit macOS dependency bootstrap.
# Installs only build prerequisites documented by the pinned HydraDB README,
# configures Homebrew native header/libclang discovery for Rust bindgen, then
# delegates to best_use_magicstudio.sh. It never reads project/provider secrets.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$SCRIPT_DIR/best_use_magicstudio.sh"

say() { printf '%s\n' "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

[[ "$(uname -s)" == "Darwin" ]] || fail "this bootstrap is for macOS; install the pinned HydraDB prerequisites for your OS, then run $LAUNCHER"
have curl || fail "curl is required"
have git || fail "git is required"
have python3 || fail "python3 is required"

if ! xcode-select -p >/dev/null 2>&1; then
  say "[bootstrap] Xcode Command Line Tools are missing."
  say "[bootstrap] Launching Apple's installer; complete it, then rerun this command."
  xcode-select --install || true
  exit 2
fi

if ! have brew; then
  fail "Homebrew is required for HydraDB native libraries. Install Homebrew, then rerun this bootstrap."
fi

# HydraDB pinned source README requirements for macOS.
for formula in cmake pkg-config llvm suite-sparse; do
  if ! brew list --versions "$formula" >/dev/null 2>&1; then
    say "[bootstrap] installing Homebrew dependency: $formula"
    brew install "$formula"
  else
    say "[bootstrap] present: $formula"
  fi
done

if ! brew list --versions cleishm/neo4j/libcypher-parser >/dev/null 2>&1; then
  say "[bootstrap] installing Homebrew dependency: cleishm/neo4j/libcypher-parser"
  brew install cleishm/neo4j/libcypher-parser
else
  say "[bootstrap] present: cleishm/neo4j/libcypher-parser"
fi

# libcypher-parser-sys links the library through pkg-config but its bindgen step
# still needs the Homebrew include path explicitly on macOS. Bindgen supports
# BINDGEN_EXTRA_CLANG_ARGS for this purpose. Homebrew llvm is keg-only, so also
# point clang-sys at its libclang directory without overriding a caller-supplied
# LIBCLANG_PATH.
CYPHER_PREFIX="$(brew --prefix cleishm/neo4j/libcypher-parser)"
LLVM_PREFIX="$(brew --prefix llvm)"
CYPHER_HEADER="$CYPHER_PREFIX/include/cypher-parser.h"
[[ -f "$CYPHER_HEADER" ]] || fail "cypher-parser header missing after install: $CYPHER_HEADER"
export BINDGEN_EXTRA_CLANG_ARGS="-I$CYPHER_PREFIX/include${BINDGEN_EXTRA_CLANG_ARGS:+ $BINDGEN_EXTRA_CLANG_ARGS}"
export LIBCLANG_PATH="${LIBCLANG_PATH:-$LLVM_PREFIX/lib}"
say "[bootstrap] bindgen include: $CYPHER_PREFIX/include"
say "[bootstrap] libclang path: $LIBCLANG_PATH"

# Rust's official installation route. HydraDB requires Rust >=1.91 and pins stable.
if ! have rustup && ! have cargo; then
  say "[bootstrap] cargo/rustup missing; installing Rust stable with the official rustup installer"
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
fi

[[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"

if have rustup; then
  say "[bootstrap] ensuring stable Rust toolchain is installed"
  rustup toolchain install stable
  rustup default stable
fi

have cargo || fail "cargo is still unavailable after Rust bootstrap; open a new shell or source $HOME/.cargo/env"
have rustc || fail "rustc is unavailable after Rust bootstrap"

say "[bootstrap] rustc: $(rustc --version)"
say "[bootstrap] cargo: $(cargo --version)"
say "[bootstrap] cypher-parser: $(pkg-config --modversion cypher-parser 2>/dev/null || pkg-config --modversion libcypher-parser 2>/dev/null || echo UNRESOLVED)"

# Homebrew's SuiteSparse package is the source of GraphBLAS on macOS; the .pc
# filename varies across package versions, so do not fail solely on pkg-config name.
if brew list --versions suite-sparse >/dev/null 2>&1; then
  say "[bootstrap] SuiteSparse: $(brew list --versions suite-sparse | head -1)"
else
  fail "suite-sparse is not installed"
fi

say "[bootstrap] dependency bootstrap PASS"
say "[bootstrap] delegating to Best Use launcher"
exec bash "$LAUNCHER" "${1:-start}"
