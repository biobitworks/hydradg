#!/usr/bin/env npx tsx
/** Daytona infrastructure smoke — loads env locally, never prints secret values. */
import { spawnSync } from "node:child_process";
import path from "node:path";
import envModNs from "../lib/hydralamp/env.ts";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { loadHydraLampServerEnv, daytonaApiKeyStatus, daytonaApiUrl } = unwrapHydraLampMod(
  envModNs,
) as {
  loadHydraLampServerEnv: () => void;
  daytonaApiKeyStatus: () => "PRESENT" | "MISSING" | "INVALID_PLACEHOLDER";
  daytonaApiUrl: () => string;
};
const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};

loadHydraLampServerEnv();
const status = daytonaApiKeyStatus();
const apiUrl = daytonaApiUrl();
console.log("DAYTONA_API_KEY=" + status);
console.log("DAYTONA_API_URL=" + apiUrl);

if (status !== "PRESENT") {
  console.log("DAYTONA_STATE=BLOCKED");
  process.exit(2);
}

const py = path.join(repoRoot(), "apps", "hydradg-web", "scripts", "sponsor_daytona_smoke.py");
const venvPython = process.env.DAYTONA_VENV_PYTHON || "";
const python = venvPython || "python3";

const child = spawnSync(python, [py], {
  env: {
    ...process.env,
    DAYTONA_API_URL: apiUrl,
    DAYTONA_USE_DEPRECATED_POLLING: "true",
  },
  encoding: "utf8",
  timeout: 180_000,
  maxBuffer: 4 * 1024 * 1024,
});

if (child.stdout) process.stdout.write(child.stdout);
if (child.stderr) {
  const redacted = child.stderr.replace(/dtn_[A-Za-z0-9]+/g, "dtn_REDACTED");
  process.stderr.write(redacted);
}

if (child.error && (child.error as NodeJS.ErrnoException).code === "ETIMEDOUT") {
  console.log("DAYTONA_MISSION=TIMEOUT");
  process.exit(1);
}

process.exit(child.status ?? 1);
