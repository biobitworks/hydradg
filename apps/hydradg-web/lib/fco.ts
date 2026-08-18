import { createHash } from "node:crypto";

export type FcoNode = {
  id: string;
  object_sha256: string;
  type: string;
  payload: Record<string, unknown>;
};

function normalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(normalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, val]) => [key, normalize(val)]),
    );
  }
  return value;
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(normalize(value));
}

export function sha256Text(value: string): string {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

export function makeFcoNode(
  type: string,
  payload: Record<string, unknown>,
): FcoNode {
  const body = { type, payload };
  const object_sha256 = sha256Text(canonicalJson(body));
  return {
    id: `fco:${object_sha256}`,
    object_sha256,
    type,
    payload,
  };
}

/**
 * HydraDB's native vertex identity is a u64. FCO identity remains the complete
 * SHA-256 string; this helper derives a deterministic 52-bit traversal key that
 * stays exactly representable as a JavaScript number. The canonical fco_id and
 * object_sha256 are always stored as properties and remain the custody identity.
 *
 * This is an addressing adapter, not a cryptographic identity replacement.
 */
export function hydraNumericId(stableId: string): number {
  const digest = /^[a-z]+:([0-9a-f]{64})$/i.exec(stableId)?.[1] || sha256Text(stableId);
  const value = Number.parseInt(digest.slice(0, 13), 16); // 52 bits, JS-safe integer
  return value === 0 ? 1 : value;
}
