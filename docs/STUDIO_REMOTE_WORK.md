# Remote work: magicPRObox → magicSTUDIObox

Scientific GPU lanes (Daytona, SGLang, CFOS, Ollama heavy runs) execute on **magicSTUDIObox**.
magicPRObox is the cockpit: SSH in, edit, push, and drive Studio jobs from here.

## One paste (gum doctor E2E from Pro)

Runs **gum doctor v2 → CFOS → SGLang** on Studio via SSH, plus Pro CFOS controller lane:

```bash
bash ~/projects/active/hydradg/scripts/gum_studio_piecewise_e2e.sh
```

Default SSH target after 2026-09-02 Wi-Fi migration: `magicstudiobox-ip` → Tailscale `100.105.40.90` (override with `STUDIO_SSH_HOST`).

Log: `/tmp/gum_studio_piecewise_e2e.log` (Pro) and `/tmp/gum_studio_piecewise_e2e.studio.log` (Studio).

## Quick start (from Pro)

```bash
cd ~/projects/active/hydradg
chmod +x scripts/studio_remote.sh

# Verify SSH + Homebrew PATH + daytona on Studio
./scripts/studio_remote.sh smoke

# Interactive Studio shell (full login environment)
./scripts/studio_remote.sh shell

# Run in hydradg on Studio
./scripts/studio_remote.sh hydradg 'git status --short'

# SGLang GPU orchestrator (foreground)
./scripts/studio_remote.sh sglang

# SGLang in background
./scripts/studio_remote.sh sglang-bg
./scripts/studio_remote.sh sglang-log
```

## Why the wrapper exists

Non-interactive `ssh host 'command'` on Studio gets a minimal `PATH` (`/usr/bin` only).
`daytona`, Homebrew `python3`, and `pnpm` live under `/opt/homebrew/bin` and are invisible
unless PATH is set. `studio_remote.sh` also sources `~/.config/ai-keys/keys.env` on **Studio**
(not Pro).

## SSH host

Default: `magicSTUDIObox` (see `~/.ssh/config` on Pro).

Override:

```bash
export STUDIO_SSH_HOST=magicstudiobox-ip   # Tailscale IP alias
./scripts/studio_remote.sh smoke
```

## keys.env

Both hosts have `~/.config/ai-keys/keys.env`. Placeholder lines like
`export BAND_ACCESS_TOKEN=<FILL_AFTER_OAUTH>` break `source` — comment them out or quote them.

Syntax check:

```bash
zsh -n ~/.config/ai-keys/keys.env
```

## Do not run on Pro

| Lane | Host |
|------|------|
| `newinml_gpu_sglang_daisy_execute.py` | Studio only |
| CFOS `:8787` + Ollama canaries | Studio only |
| HydraLamp CFOS-HL-001 deterministic fixtures | Pro or Studio |
| Yappy / tunnel client | Pro |
