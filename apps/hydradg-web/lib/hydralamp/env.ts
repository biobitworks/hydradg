/**
 * Server-side env loader for HydraLamp/Runtype.
 * Never logs or returns secret values — presence only.
 */
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

let loaded = false;

function parseEnvFile(filePath: string): void {
  if (!existsSync(filePath)) return;
  const text = readFileSync(filePath, "utf8");
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    if (!line || line.startsWith("#") || !line.includes("=")) continue;
    const eq = line.indexOf("=");
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    if (!(key in process.env) || process.env[key] === "") {
      process.env[key] = val;
    }
  }
}

/** Load gitignored local env files into process.env (idempotent). */
export function loadHydraLampServerEnv(): void {
  if (loaded) return;
  const cwd = process.cwd();
  // apps/hydradg-web/.env.local and repo-root .env.local
  const candidates = [
    path.join(cwd, ".env.local"),
    path.join(cwd, ".env"),
    path.join(cwd, "..", "..", ".env.local"),
    path.join(cwd, "..", "..", ".env"),
  ];
  for (const c of candidates) parseEnvFile(c);
  loaded = true;
}

export function runtypeApiKeyStatus(): "PRESENT" | "MISSING" {
  loadHydraLampServerEnv();
  const v = process.env.RUNTYPE_API_KEY;
  return v && v.trim() ? "PRESENT" : "MISSING";
}
