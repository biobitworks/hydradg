# HydraDG remote-work readiness

Status: PARTIALLY_READY
Primary remote host: `magicstudiobox`
Branch: `hack-hydra/webapp-mvp-20260818`

## Decision

For the Hack Hydra MVP, `magicstudiobox` is the default application/database execution host. Cloud providers (Modal, Daytona, Kaggle, GMI Cloud, others) are optional adapters only after their credentials, provider contracts, retention behavior, and smoke tests are verified. They are not required for the critical demo path.

Ollarma remains the local-first bounded execution/router substrate. Keep its service bound to localhost unless a separately reviewed remote-access design is approved. Do not turn Ollarma into an unaudited public relay.

## Ready now

- HydraDG web-app scaffold and graph-query/status surface exist on the MVP branch.
- HydraDB/Neo4j graph adapter work exists in the MVP branch.
- Exa retrieval path exists in the MVP branch.
- Ollarma public substrate supports bounded local execution, HTTP/CLI routing, typed receipts, recovery checks, and launchd persistence.
- Local Ollama is the only provider lane treated as LIVE by the current public Ollarma provider roadmap.

## Not yet proven

- `magicstudiobox` has the HydraDG branch cloned at the intended commit.
- Ollarma is installed as a persistent launchd service on `magicstudiobox` and passes `ollarma startup-smoke` after reboot.
- HydraDB is running locally on `magicstudiobox` or a verified remote HydraDB endpoint is reachable from it.
- HydraDG web app starts automatically after reboot and reports healthy graph + Ollarma dependencies.
- Secure remote administration has been smoke-tested from an off-LAN network.
- Remote access survives reboot without opening Ollarma/HydraDB directly to the public Internet.
- Source/license registries, experiment outputs, lab notebooks, receipts, and graph storage are backed up to a second location.
- Secret scan confirms no API keys/private credentials are committed or exposed through browser bundles/logs.
- Recovery drill proves interrupted work can be resumed from git + receipts + graph state.

## Remote-readiness gate

Do not call the host `REMOTE_READY` until all items below have executed and receipts/logs are retained.

1. Host identity
   - record OS, hardware, hostname, date/time, git commit, Python/Node/Ollarma/HydraDB versions;
   - hash the resulting environment manifest.
2. Repository state
   - clone/fetch `biobitworks/hydradg`;
   - checkout the pinned MVP branch/commit;
   - verify clean working tree before unattended work.
3. Ollarma persistence
   - install persistent service using its supported launchd workflow;
   - run `ollarma startup-smoke`;
   - reboot once and rerun the smoke check;
   - preserve readiness receipt/log paths.
4. Graph/database
   - start the intended HydraDB service locally OR configure the verified HydraDB endpoint;
   - run current-state, historical-state, and write/read smoke queries;
   - do not use the uploaded Neo4j credential file as a committed config artifact.
5. HydraDG application
   - install pinned dependencies;
   - run type/build/tests;
   - run the web app as a persistent local service;
   - verify `/status`/health plus one end-to-end public-source demo query.
6. Remote administration
   - use a private authenticated remote path (for example a private VPN/SSH tunnel or equivalent reviewed mechanism);
   - keep Ollarma and database listeners private by default;
   - verify access from a different network;
   - verify public port scan does not expose Ollarma/HydraDB unintentionally.
7. Secrets
   - environment/keychain only;
   - no secrets in git, notebooks, browser bundles, screenshots, or lab notes;
   - rotate any credential previously pasted into chat or plaintext files before remote use.
8. Recovery and backup
   - backup git state, public-source registry, experiment manifests, FCO/FCG receipts, lab notebooks, and graph/object-store state;
   - simulate process interruption/reboot;
   - reconstruct current work from committed state + receipts;
   - record earliest unrecoverable dependency if reconstruction fails.
9. Resource guard
   - confirm disk free space, memory/swap, temperature/power behavior, and automatic restart policy;
   - prevent unattended jobs from starting when memory/swap safety thresholds fail.
10. Final remote smoke
   - from off-LAN: connect securely, inspect status, execute one bounded experiment, inspect its receipt, and verify no private source/content escaped its intended boundary.

## Provider policy for the hackathon

- `LOCAL_OLLAMA`: LIVE / preferred.
- `OLLARMA`: LIVE local bounded router/execution surface; not a public remote relay.
- `MODAL`: OPTIONAL_UNVERIFIED until a real provider smoke test and retention/storage experiment are recorded.
- `DAYTONA`: OPTIONAL_UNVERIFIED until a real provider smoke test and workspace persistence/retention experiment are recorded.
- `KAGGLE`: OPTIONAL_UNVERIFIED; use only for a bounded benchmark if credentials/runtime are verified and it adds value.
- `GMI_CLOUD`: OPTIONAL_UNVERIFIED until endpoint/model/retention/credential path is verified.
- other cloud providers: fail closed until explicitly admitted.

The Google AI Mode volatile/tokenization blueprints are experiment inputs, not production assertions. Claims such as `zero persistence`, `airtight`, `immutable`, `zero-trust`, fixed latency, fixed cost reduction, or PHI/compliance guarantees require separate executed evidence and must remain below the claim ceiling until then.

## State labels

- `PARTIALLY_READY`: local components exist but remote host/reboot/off-LAN recovery has not been proven.
- `REMOTE_SMOKE_READY`: host + persistence + secure remote path pass smoke tests, but unattended recovery/red-team is incomplete.
- `REMOTE_READY`: all gate items above pass with retained receipts.
