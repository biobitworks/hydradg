/**
 * Shared canonical JSON — identical algorithm for Node and browser.
 * Used as the preimage for all HydraLamp domain hashes.
 */
export function normalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(normalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => [k, normalize(v)]),
    );
  }
  return value;
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(normalize(value));
}

export const DOMAIN = {
  EVENT: "HYDRALAMP_EVENT_V1",
  MODEL_CONTEXT: "HYDRALAMP_MODEL_CONTEXT_V1",
  MODEL_OUTPUT: "HYDRALAMP_MODEL_OUTPUT_V1",
  TOOL_INPUT: "HYDRALAMP_TOOL_INPUT_V1",
  TOOL_OUTPUT: "HYDRALAMP_TOOL_OUTPUT_V1",
  PROPOSAL: "HYDRALAMP_PROPOSAL_V1",
  KG_SNAPSHOT: "HYDRALAMP_KG_SNAPSHOT_V1",
} as const;

export type DomainKey = (typeof DOMAIN)[keyof typeof DOMAIN];

export function domainPreimage(domain: DomainKey, value: unknown): string {
  return `${domain}\n${canonicalJson(value)}`;
}

export const GENESIS_PREV_HASH_PREIMAGE = "HYDRALAMP_EVENT_V1\nGENESIS";
