import type { ExperimentRun, HydraLampEvent } from "./types";

const runs = new Map<string, ExperimentRun>();
const waiters = new Map<string, Set<(e: HydraLampEvent | { type: "DONE_SENTINEL" }) => void>>();

export function putRun(run: ExperimentRun) {
  runs.set(run.run_id, run);
}

export function getRun(runId: string): ExperimentRun | undefined {
  return runs.get(runId);
}

export function pushEvent(runId: string, event: HydraLampEvent) {
  const run = runs.get(runId);
  if (!run) return;
  run.events.push(event);
  const set = waiters.get(runId);
  if (set) for (const w of set) w(event);
}

export function markDone(runId: string) {
  const run = runs.get(runId);
  if (run) run.done = true;
  const set = waiters.get(runId);
  if (set) for (const w of set) w({ type: "DONE_SENTINEL" });
}

export function subscribe(runId: string, cb: (e: HydraLampEvent | { type: "DONE_SENTINEL" }) => void) {
  if (!waiters.has(runId)) waiters.set(runId, new Set());
  waiters.get(runId)!.add(cb);
  return () => waiters.get(runId)?.delete(cb);
}
