/**
 * Durable run-state projection for HydraLamp.
 * Cloudflare Worker/DO is the preferred remote transport; when not configured,
 * this module keeps an in-process durable map with honest provider badge.
 * Canonical custody remains FCO/FCG — this is projection only.
 */
import { createHash } from "node:crypto";

export type CfLifecycle =
  | "NORMAL"
  | "POISON"
  | "QUARANTINED"
  | "ANTIDOTE"
  | "RESTORED";

export type CfRunProjection = {
  run_id: string;
  lifecycle: CfLifecycle;
  custody_state: "PENDING_CUSTODY" | "CUSTODY_VERIFIED";
  event_count: number;
  last_event_hash: string | null;
  fcg_root: string | null;
  updated_at: string;
  transport: "CLOUDFLARE_DO" | "LOCAL_DURABLE_PROJECTION";
  provider_badge: "LIVE" | "BOUNDED" | "REPLAY" | "ERROR" | "BLOCKED";
};

const localStore = new Map<string, CfRunProjection>();

function sha(s: string) {
  return createHash("sha256").update(s, "utf8").digest("hex");
}

export function cloudflareConfigured(): boolean {
  return Boolean(
    process.env.HYDRALAMP_CF_WORKER_URL?.trim() ||
      process.env.CLOUDFLARE_HYDRALAMP_URL?.trim(),
  );
}

export function cloudflareBaseUrl(): string | null {
  const u =
    process.env.HYDRALAMP_CF_WORKER_URL?.trim() ||
    process.env.CLOUDFLARE_HYDRALAMP_URL?.trim();
  return u ? u.replace(/\/$/, "") : null;
}

export async function projectRunState(input: {
  run_id: string;
  lifecycle: CfLifecycle;
  custody_state: "PENDING_CUSTODY" | "CUSTODY_VERIFIED";
  event_count: number;
  last_event_hash: string | null;
  fcg_root: string | null;
  provider_badge: CfRunProjection["provider_badge"];
}): Promise<CfRunProjection> {
  const projection: CfRunProjection = {
    ...input,
    updated_at: new Date().toISOString(),
    transport: cloudflareConfigured() ? "CLOUDFLARE_DO" : "LOCAL_DURABLE_PROJECTION",
  };

  const base = cloudflareBaseUrl();
  if (base) {
    try {
      const res = await fetch(`${base}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(projection),
        signal: AbortSignal.timeout(8_000),
      });
      if (res.ok) {
        const remote = (await res.json()) as CfRunProjection;
        localStore.set(input.run_id, remote);
        return remote;
      }
    } catch {
      // fall through to local durable projection — never invent CF success
    }
  }

  localStore.set(input.run_id, projection);
  return projection;
}

export function getProjectedRun(run_id: string): CfRunProjection | null {
  return localStore.get(run_id) || null;
}

export function listProjectedRuns(): string[] {
  return [...localStore.keys()];
}

export function projectionReceiptHash(p: CfRunProjection): string {
  return sha(JSON.stringify(p));
}
