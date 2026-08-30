# Studio Test Server — Current State (2026-08-26)

Machine-local persistent HydraDG web test server for tailnet/iPad access.

- Localhost port: `127.0.0.1:3000` (loopback only; not `0.0.0.0`)
- Web persistence: `ops/studio-test/bin/hydradg-test-supervise-loop.sh` (nohup; launchd `next start` hangs without bind on this host)
- Deploy watcher: `com.biobitworks.hydradg-deploy-watcher` (launchd StartInterval ~60s)
- Runtime root: `/Volumes/magicBLACKbox/hydradg/services/hydradg-test`
- Tailnet URL: `https://magicstudiobox.tail0cf9bb.ts.net/`
- Boundary: Tailscale Serve, **tailnet only**; Funnel OFF; no public exposure
- App path: `apps/hydradg-web` (served from `current` release symlink)
- Git SHA at doc write: `03558a9361b1e3d2d2b6301842595d6ca433491d` on branch `hack-hydra/agent-native-builders-20260826`
- `DELTADG_STATE=NOT_APPLICABLE`

## Logs

Launchd ProgramArguments/stdio must stay on the boot volume (paths under
`/Volumes/magicBLACKbox` → exit 78 EX_CONFIG). App logs live on BLACKBOX:

- `/Volumes/magicBLACKbox/hydradg/services/hydradg-test/logs/web.out.log`
- `/Volumes/magicBLACKbox/hydradg/services/hydradg-test/logs/web.err.log`
- `/Volumes/magicBLACKbox/hydradg/services/hydradg-test/logs/supervise_web.log`
- `~/Library/Logs/hydradg-test/deploy-watcher.out.log`

## Health commands

```bash
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/
curl -fsS -o /dev/null -w '%{http_code}\n' https://magicstudiobox.tail0cf9bb.ts.net/
ps -p "$(cat /Volumes/magicBLACKbox/hydradg/services/hydradg-test/state/supervise.pid)" -o pid,etime,command
launchctl print gui/$(id -u)/com.biobitworks.hydradg-deploy-watcher | head
python3 ops/studio-test/deploy.py --check
tailscale serve status
```

Canonical operator doc: `docs/STUDIO_TEST_SERVER_REMOTE_WORK.md`.

No secrets in this document.
