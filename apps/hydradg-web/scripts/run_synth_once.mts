import { startHydraLampExperiment } from "../lib/hydralamp/coordinator.ts";
import { getRun, subscribe } from "../lib/hydralamp/store.ts";

async function main() {
  const run = await startHydraLampExperiment({
    perturbation: "INVALID_PROOF",
    allow_synthetic_ui_fixture: true,
    demo_20s: true,
  });
  console.log("STARTED", run.run_id, run.mode);
  await new Promise<void>((resolve) => {
    const unsub = subscribe(run.run_id, () => {});
    const t = setInterval(() => {
      const r = getRun(run.run_id);
      if (r?.done) {
        clearInterval(t);
        unsub();
        console.log("DONE mode=", r.mode);
        console.log("FCG", r.fcg.append_state, (r.fcg.root_after || "").slice(0, 16));
        console.log("HYDRADB", r.hydradb.state);
        console.log(
          "LANES",
          r.lanes.map((l) => l.structured?.decision || l.status).join(","),
        );
        console.log(
          "UNAUTHORIZED",
          (r.verifier as { unauthorized_canonical_writes?: number })?.unauthorized_canonical_writes,
        );
        console.log("RUN_ID", r.run_id);
        resolve();
      }
    }, 50);
    setTimeout(() => {
      clearInterval(t);
      unsub();
      console.log("WAIT_TIMEOUT");
      resolve();
    }, 15000);
  });
}

void main();
