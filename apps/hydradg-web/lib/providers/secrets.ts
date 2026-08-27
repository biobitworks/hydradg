/**
 * Server-only secret presence helpers. Never log or return secret values.
 */
import { loadHydraLampServerEnv } from "../hydralamp/env";

const PLACEHOLDERS = new Set([
  "",
  "your_actual_key_here",
  "changeme",
  "replace_me",
  "xxx",
  "insert_key_here",
]);

export type SecretPresence = "PRESENT" | "MISSING" | "INVALID_PLACEHOLDER";

function classify(value: string | undefined): SecretPresence {
  if (!value) return "MISSING";
  const v = value.trim();
  if (!v) return "MISSING";
  if (PLACEHOLDERS.has(v.toLowerCase())) return "INVALID_PLACEHOLDER";
  if (/^your_.*_here$/i.test(v)) return "INVALID_PLACEHOLDER";
  if (/^<[^>]+>$/.test(v)) return "INVALID_PLACEHOLDER";
  if (/^tvly-your/i.test(v) || /^tk_your/i.test(v) || /^dtn_your/i.test(v)) {
    return "INVALID_PLACEHOLDER";
  }
  return "PRESENT";
}

function read(name: string): SecretPresence {
  loadHydraLampServerEnv();
  return classify(process.env[name]);
}

export function secretPresence(name: string): SecretPresence {
  return read(name);
}

export function tavilyApiKeyStatus(): SecretPresence {
  return read("TAVILY_API_KEY");
}

export function runtypeApiKeyStatus(): SecretPresence {
  return read("RUNTYPE_API_KEY");
}

export function daytonaApiKeyStatus(): SecretPresence {
  return read("DAYTONA_API_KEY");
}

export function hydraDbApiKeyStatus(): SecretPresence {
  loadHydraLampServerEnv();
  const a = classify(process.env.HYDRA_DB_API_KEY);
  if (a === "PRESENT") return a;
  return classify(process.env.HYDRADB_API_KEY);
}

export function envOrDefault(name: string, fallback: string): string {
  loadHydraLampServerEnv();
  const v = (process.env[name] || "").trim();
  return v || fallback;
}

/** Redact likely secret tokens from error strings. */
export function redactSecrets(text: string): string {
  return text
    .replace(/tvly-[A-Za-z0-9_-]+/g, "tvly_REDACTED")
    .replace(/dtn_[A-Za-z0-9]+/g, "dtn_REDACTED")
    .replace(/rt_[A-Za-z0-9_]+/g, "rt_REDACTED")
    .replace(/mi_[0-9a-fA-F]{16,}/g, "mi_REDACTED")
    .replace(/tk_[A-Za-z0-9_-]+/g, "tk_REDACTED")
    .replace(/sk_live_[A-Za-z0-9._-]+/g, "sk_live_REDACTED")
    .replace(/Bearer\s+[A-Za-z0-9._-]+/gi, "Bearer REDACTED");
}

export const DOCUMENTED_SERVER_ENV = [
  "TAVILY_API_KEY",
  "RUNTYPE_API_KEY",
  "RUNTYPE_API_URL",
  "DAYTONA_API_KEY",
  "DAYTONA_API_URL",
  "HYDRA_DB_API_KEY",
  "HYDRADB_DATABASE",
  "HYDRADB_COLLECTION",
  "HYDRADB_API_URL",
] as const;
