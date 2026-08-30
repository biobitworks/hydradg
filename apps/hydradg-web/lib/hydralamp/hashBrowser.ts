/**
 * Browser Web Crypto twin of server hash.ts — same canonicalization + domains.
 */
import {
  DOMAIN,
  domainPreimage,
  canonicalJson,
  GENESIS_PREV_HASH_PREIMAGE,
  type DomainKey,
} from "./canonical";

export { DOMAIN, canonicalJson, type DomainKey };

async function sha256Hex(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export async function domainHash(domain: DomainKey, value: unknown): Promise<string> {
  return sha256Hex(domainPreimage(domain, value));
}

export async function hashEvent(eventWithoutHash: Record<string, unknown>): Promise<string> {
  const {
    event_hash: _ignored,
    hash_compute_ms: _h,
    context_delta_compute_ms: _c,
    graph_render_update_ms: _g,
    SSE_delivery_ms: _s,
    model_latency_ms: _m,
    end_to_end_ms: _e,
    ...rest
  } = eventWithoutHash;
  return domainHash(DOMAIN.EVENT, rest);
}

export async function genesisPrevHash(): Promise<string> {
  return sha256Hex(GENESIS_PREV_HASH_PREIMAGE);
}

export async function verifyEventHash(event: Record<string, unknown>): Promise<{
  server_hash: string | null;
  client_recompute: string;
  verified: boolean;
}> {
  const server = typeof event.event_hash === "string" ? event.event_hash : null;
  const client = await hashEvent(event);
  return {
    server_hash: server,
    client_recompute: client,
    verified: server !== null && server === client,
  };
}
