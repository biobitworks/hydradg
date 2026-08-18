# HydraDG Remote Work Architecture

Status: TEST / REMOTE-WORK SETUP

This document defines the remote-work topology for HydraDG when `magicPRObox` is mobile and `magicSTUDIObox` remains the stateful compute/storage host.

## Roles

### magicPRObox

Control plane / mobile client:

- GitHub review and orchestration
- SSH over Tailscale
- local port-forward endpoints
- lightweight development and inspection
- no requirement to copy large training datasets or persistent database state

### magicSTUDIObox

Stateful compute node:

- Daisy/Vithia training
- Ollarma/Ollama serving
- HydraDB and other persistent databases
- long-running jobs
- local research assets that should not move with the laptop

## Network boundary

Use Tailscale only as the private network transport. Keep ordinary OpenSSH key authentication for SSH unless a later governed change explicitly enables Tailscale SSH.

Prefer a stable MagicDNS host name for the studio machine. The default SSH alias used by the scripts is `magicstudio`; configure that alias to resolve the Tailscale/MagicDNS host.

Do not expose Ollarma, HydraDB, or database ports to the public Internet. Services should remain bound to localhost on magicSTUDIObox unless a later explicit tailnet-only service design is reviewed.

## Default tunnels

The helper script creates local forwards from magicPRObox to localhost-bound services on magicSTUDIObox:

| Service | Laptop endpoint | Studio endpoint | Purpose |
|---|---|---|---|
| Ollarma | `127.0.0.1:18484` | `127.0.0.1:8484` | governed local-model bridge |
| HydraDB HTTP | `127.0.0.1:18443` | `127.0.0.1:8443` | OpenCypher/HTTP API |
| HydraDB Bolt | `127.0.0.1:17687` | `127.0.0.1:7687` | Bolt API |
| HydraDB readiness | `127.0.0.1:19090` | `127.0.0.1:9090` | readiness/admin checks |

All ports are overridable with environment variables. These mappings are transport configuration, not evidence that the corresponding service is running.

## Long-running work

Daisy training and other multi-hour processes should run inside `tmux` (or an equivalent persistent session) on magicSTUDIObox so laptop sleep, Wi-Fi changes, or SSH disconnects do not terminate the job.

Recommended execution pattern:

```text
GitHub TEST commit
    -> magicSTUDIObox pulls exact commit
    -> tmux job starts from that commit
    -> receipts/results written locally
    -> secret/size gates
    -> commit + push
    -> ChatGPT reviews exact GitHub commit
```

Do not use ad-hoc file copies as the canonical handoff between machines. GitHub is the code/config/receipt boundary. Large research assets may remain local or use Git LFS when intentionally versioned.

## Persistent services

Ollarma/HydraDB should eventually run under a host service manager so a reboot restores the intended service state. Do not install a launchd definition until the executable paths, working directories, and service ports are frozen and tested.

## SSH configuration

A typical client entry on magicPRObox is:

```sshconfig
Host magicstudio
    HostName <magicSTUDIObox MagicDNS name or Tailscale IP>
    User byron
    IdentityFile ~/.ssh/<dedicated-key>
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    TCPKeepAlive yes
```

Do not commit the private key or a private-key body to GitHub.

## Git synchronization invariant

Every evidence-producing checkpoint uses:

```text
fetch -> pull --ff-only -> verify sync -> execute/edit -> test
-> receipts/hashes -> Gitleaks/size/claim gates -> commit -> push
-> fetch/pull --ff-only -> verify local == remote -> review
```

The local machine and magicSTUDIObox must not both modify the same branch without first pulling the remote tip.

## TEST / STAGE / PUBLIC

- `biobitworks/hydradg`: private TEST/canonical working history.
- `hydradg-stage`: private sanitized release candidate, once created.
- `hydradg-public`: clean public export, once created.

Promotion is an explicit transformation. Do not make the TEST repository public.

## FCO/FCG boundaries

- Tailscale/SSH connectivity establishes transport, not scientific correctness.
- A Git commit establishes a versioned source state, not a signature.
- A successful service probe establishes bounded availability only.
- A training run remains probabilistic unless its declared reproducibility envelope supports a stronger claim.
- Private signing keys remain outside GitHub.
