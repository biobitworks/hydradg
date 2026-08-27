/**
 * Server-side env loader for HydraLamp/Runtype.
 * Never logs or returns secret values — presence only.
 */
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

let loaded = false;

/** Obvious template values — treated as MISSING (never logged). */
const RUNTYPE_KEY_PLACEHOLDERS = new Set([
  "",
  "your_actual_key_here",
  "changeme",
  "replace_me",
  "xxx",
  "insert_key_here",
]);

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
    // Last assignment within a file wins (append-safe for .env.local).
    process.env[key] = val;
  }
}

function parseEnvFileFirstWinsAcrossFiles(filePath: string): void {
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
    if (!(key in process.env)) {
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
  // App-local .env.local last-wins (safe when operators append keys).
  // Other files only fill keys not already set by a higher-precedence file.
  for (let i = 0; i < candidates.length; i++) {
    const c = candidates[i]!;
    const isAppLocal =
      i === 0 && c.endsWith(`${path.sep}.env.local`);
    if (isAppLocal) parseEnvFile(c);
    else parseEnvFileFirstWinsAcrossFiles(c);
  }
  loaded = true;
}

function isRuntypeKeyPlaceholder(value: string): boolean {
  const v = value.trim();
  if (!v) return true;
  if (RUNTYPE_KEY_PLACEHOLDERS.has(v.toLowerCase())) return true;
  if (/^your_.*_here$/i.test(v)) return true;
  if (/^<[^>]+>$/.test(v)) return true;
  return false;
}

export function runtypeApiKeyStatus(): "PRESENT" | "MISSING" {
  loadHydraLampServerEnv();
  const v = process.env.RUNTYPE_API_KEY;
  if (!v || isRuntypeKeyPlaceholder(v)) return "MISSING";
  return "PRESENT";
}
