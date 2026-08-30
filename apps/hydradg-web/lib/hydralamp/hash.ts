/**
 * HydraLamp hash domains — SHA-256 = byte/state identity only.
 * HASH CHANGE ≠ SEMANTIC DISTANCE.
 */
import { createHash } from "node:crypto";
import {
  DOMAIN,
  domainPreimage,
  canonicalJson,
  GENESIS_PREV_HASH_PREIMAGE,
  type DomainKey,
} from "./canonical";

export { DOMAIN, canonicalJson, type DomainKey };
export { normalize } from "./canonical";

export function sha256Text(text: string): string {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

export function sha256Bytes(bytes: Uint8Array | Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

export function domainHash(domain: DomainKey, value: unknown): string {
  return sha256Text(domainPreimage(domain, value));
}

export function hashModelContext(ctx: unknown): string {
  return domainHash(DOMAIN.MODEL_CONTEXT, ctx);
}

export function hashModelOutput(text: string): string {
  return domainHash(DOMAIN.MODEL_OUTPUT, { text });
}

export function hashRawBytes(bytes: Uint8Array | Buffer): string {
  return sha256Bytes(bytes);
}

export function hashToolInput(input: unknown): string {
  return domainHash(DOMAIN.TOOL_INPUT, input);
}

export function hashToolOutput(output: unknown): string {
  return domainHash(DOMAIN.TOOL_OUTPUT, output);
}

export function hashProposal(proposal: unknown): string {
  return domainHash(DOMAIN.PROPOSAL, proposal);
}

export function hashKgSnapshot(snapshot: { objects: unknown; edges: unknown }): string {
  return domainHash(DOMAIN.KG_SNAPSHOT, snapshot);
}

/**
 * Event hash binds custody fields. event_hash itself is excluded from preimage.
 * Timing fields are observational and must not affect the custody hash.
 */
export function hashEvent(eventWithoutHash: Record<string, unknown>): string {
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

export const GENESIS_PREV_HASH = sha256Text(GENESIS_PREV_HASH_PREIMAGE);
