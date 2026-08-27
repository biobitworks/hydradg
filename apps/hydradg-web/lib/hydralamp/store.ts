import type { ExperimentRun, HydraLampEvent } from "./types";
import { GENESIS_PREV_HASH, hashEvent } from "./hash";

const runs = new Map<string, ExperimentRun>();
const waiters = new Map<
  string,
  Set<(e: HydraLampEvent | { type: "DONE_SENTINEL"; run_id: string }) => void>
>();

export function putRun(run: ExperimentRun) {
  if (!run.last_event_hash) run.last_event_hash = GENESIS_PREV_HASH;
  runs.set(run.run_id, run);
}

export function getRun(runId: string): ExperimentRun | undefined {
  return runs.get(runId);
}

export function listRunIds(): string[] {
  return [...runs.keys()];
}

/**
 * Finalize custody fields and append to chain.
 * Caller may omit hash fields; store fills prev_event_hash + event_hash.
 */
export function pushEvent(
  runId: string,
  event: Omit<HydraLampEvent, "prev_event_hash" | "event_hash"> &
    Partial<Pick<HydraLampEvent, "prev_event_hash" | "event_hash">>,
): HydraLampEvent {
  const run = runs.get(runId);
  if (!run) {
    throw new Error(`pushEvent: unknown run ${runId}`);
  }
  const hashStarted = Date.now();
  const prev = run.last_event_hash || GENESIS_PREV_HASH;
  // Deep-clone public_payload so later mutations to run.fcg/timings cannot invalidate event_hash.
  const public_payload =
    event.public_payload === undefined
      ? undefined
      : (JSON.parse(JSON.stringify(event.public_payload)) as Record<string, unknown>);
  const draft: HydraLampEvent = {
    ...event,
    public_payload,
    actor_id: event.actor_id || event.lane,
    evidence_class: event.evidence_class || "UNKNOWN",
    claim_ceiling: event.claim_ceiling || run.claim_ceiling,
    context_hash_before: event.context_hash_before ?? null,
    context_hash_after: event.context_hash_after ?? null,
    kg_snapshot_hash_before: event.kg_snapshot_hash_before ?? null,
    kg_snapshot_hash_after: event.kg_snapshot_hash_after ?? null,
    model_output_hash: event.model_output_hash ?? null,
    tool_input_hash: event.tool_input_hash ?? null,
    tool_output_hash: event.tool_output_hash ?? null,
    proposal_hash: event.proposal_hash ?? null,
    fcg_root_before: event.fcg_root_before ?? null,
    fcg_root_after: event.fcg_root_after ?? null,
    context_delta: event.context_delta
      ? (JSON.parse(JSON.stringify(event.context_delta)) as HydraLampEvent["context_delta"])
      : null,
    verification_result: event.verification_result ?? null,
    prev_event_hash: prev,
    event_hash: "",
  };
  const event_hash = hashEvent(draft as unknown as Record<string, unknown>);
  draft.event_hash = event_hash;
  draft.hash_compute_ms = Date.now() - hashStarted;
  run.events.push(draft);
  run.last_event_hash = event_hash;
  if (run.timings) {
    run.timings.hash_compute_ms_total =
      (run.timings.hash_compute_ms_total || 0) + (draft.hash_compute_ms || 0);
  }
  const set = waiters.get(runId);
  if (set) for (const w of set) w(draft);
  return draft;
}

export function markDone(runId: string) {
  const run = runs.get(runId);
  if (run) run.done = true;
  const set = waiters.get(runId);
  if (set) for (const w of set) w({ type: "DONE_SENTINEL", run_id: runId });
}

export function subscribe(
  runId: string,
  cb: (e: HydraLampEvent | { type: "DONE_SENTINEL"; run_id: string }) => void,
) {
  if (!waiters.has(runId)) waiters.set(runId, new Set());
  waiters.get(runId)!.add(cb);
  return () => waiters.get(runId)?.delete(cb);
}

export function verifyEventChain(events: HydraLampEvent[]): {
  ok: boolean;
  checked: number;
  failures: Array<{ seq: number; reason: string }>;
} {
  const failures: Array<{ seq: number; reason: string }> = [];
  let prev = GENESIS_PREV_HASH;
  for (const ev of events) {
    if (ev.prev_event_hash !== prev) {
      failures.push({ seq: ev.seq, reason: "PREV_HASH_DISCONTINUITY" });
    }
    const recomputed = hashEvent(ev as unknown as Record<string, unknown>);
    if (recomputed !== ev.event_hash) {
      failures.push({ seq: ev.seq, reason: "EVENT_HASH_MISMATCH" });
    }
    prev = ev.event_hash;
  }
  return { ok: failures.length === 0, checked: events.length, failures };
}
