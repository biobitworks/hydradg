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

| Label | Role |
| --- | --- |
| `com.biobitworks.hydradg-test` | Next production server |
| `com.biobitworks.hydradg-deploy-watcher` | `deploy.py --once` every 60s |

Install:

```bash
bash ops/studio-test/install_launchd.sh
```

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

# Logs
tail -n 100 /Volumes/magicBLACKbox/hydradg/services/hydradg-test/logs/hydradg-test.out.log
tail -n 100 /Volumes/magicBLACKbox/hydradg/services/hydradg-test/logs/deploy-watcher.out.log
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
