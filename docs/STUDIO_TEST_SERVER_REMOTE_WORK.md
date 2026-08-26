# Studio Test Server — Remote Work

## Topology

```text
Cursor (any device)
  → commit/push hack-hydra/agent-native-builders-20260826
  → GitHub Actions (ubuntu-latest) validates exact SHA
  → advances deploy/studio-test to that SHA
  → Studio launchd watcher polls outbound every ~60s
  → builds release on magicBLACKbox
  → activates symlink + restarts com.biobitworks.hydradg-test
  → Tailscale Serve → https://magicstudiobox.tail0cf9bb.ts.net/
```

Backend bind: `127.0.0.1:3000` only. Funnel OFF.

## Runtime root

`/Volumes/magicBLACKbox/hydradg/services/hydradg-test`

Convenience symlink: `/Users/byron/services/hydradg-test`

npm cache + TMPDIR live on magicBLACKbox to protect root disk.

## Services

| Mechanism | Role |
| --- | --- |
| `ops/studio-test/bin/hydradg-test-supervise-loop.sh` (nohup) | Next production server on `127.0.0.1:3000` |
| `com.biobitworks.hydradg-deploy-watcher` (launchd) | `deploy.py --once` every 60s |

Install:

```bash
bash ops/studio-test/install_launchd.sh
```

Notes:
- Wrappers live in-repo under `ops/studio-test/bin/` (boot volume).
- Paths under `/Volumes/magicBLACKbox` in launchd `ProgramArguments` / stdio cause **exit 78**.
- Builds, releases, npm cache, and TMPDIR stay on magicBLACKbox.
- On this host, launchd-managed `next start` has been observed to hang without binding
  `:3000`; the install script therefore defaults web persistence to **nohup supervise**.
- Cursor agents may be TCC-blocked from writing `~/Library/LaunchAgents`; copy plist
  templates from Terminal.app if login persistence for the watcher is required.

## Operator commands

```bash
# Deploy status
python3 ops/studio-test/deploy.py --check

# Force one deploy of current deploy/studio-test tip
python3 ops/studio-test/deploy.py --once

# Rollback to previous release
python3 ops/studio-test/deploy.py --rollback

# Health
python3 ops/studio-test/healthcheck.py --base http://127.0.0.1:3000
python3 ops/studio-test/healthcheck.py --base https://magicstudiobox.tail0cf9bb.ts.net

# launchctl
launchctl print gui/$(id -u)/com.biobitworks.hydradg-test | head
launchctl print gui/$(id -u)/com.biobitworks.hydradg-deploy-watcher | head

# Logs (boot-volume launchd stdio + BLACKBOX app logs)
tail -n 100 ~/Library/Logs/hydradg-test/hydradg-test.err.log
tail -n 100 ~/Library/Logs/hydradg-test/deploy-watcher.out.log
tail -n 100 /Volumes/magicBLACKbox/hydradg/services/hydradg-test/logs/web.err.log
tail -n 100 /Volumes/magicBLACKbox/hydradg/services/hydradg-test/logs/supervise_web.log
```

## Boundaries

- Does not touch SeedGraph / Daisy / HydraDB writes.
- Does not expose Ollarma `:8484` on Tailscale.
- Immersive Commons Floor10 credential is independent (`~/.config/immersivecommons/env`).
- `DELTADG_STATE=NOT_APPLICABLE` for this workflow.

## Floor10 credential (human, on Studio)

```bash
mkdir -p ~/.config/immersivecommons
chmod 700 ~/.config/immersivecommons
read -s '?Floor10 token: ' FLOOR10_AGENT_TOKEN
printf 'export FLOOR10_AGENT_TOKEN=%q\n' "$FLOOR10_AGENT_TOKEN" > ~/.config/immersivecommons/env
unset FLOOR10_AGENT_TOKEN
chmod 600 ~/.config/immersivecommons/env
```

Do not paste the token into Cursor chat or Git.
