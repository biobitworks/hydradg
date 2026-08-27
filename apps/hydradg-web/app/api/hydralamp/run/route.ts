import { NextResponse } from "next/server";
import { startHydraLampExperiment, runtypeKeyPresent, loadModelInventory } from "@/lib/hydralamp/coordinator";
import { loadHydraLampServerEnv } from "@/lib/hydralamp/env";
import type { PerturbationKind } from "@/lib/hydralamp/types";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const ALLOWED: PerturbationKind[] = [
  "CONTROL",
  "INVALID_PROOF",
  "REPLAYED_PROOF",
  "BROKEN_AUTHORIZATION_EDGE",
];

export async function POST(req: Request) {
  loadHydraLampServerEnv();
  const body = (await req.json().catch(() => ({}))) as {
    perturbation?: string;
    demo_20s?: boolean;
    allow_synthetic_ui_fixture?: boolean;
  };
  const perturbation = (ALLOWED.includes(body.perturbation as PerturbationKind)
    ? body.perturbation
    : "INVALID_PROOF") as PerturbationKind;

  const inventory = loadModelInventory();
  const key = runtypeKeyPresent();

  const run = await startHydraLampExperiment({
    perturbation,
    demo_20s: Boolean(body.demo_20s),
    // Explicit opt-in only — never confuse with live Runtype
    allow_synthetic_ui_fixture: Boolean(body.allow_synthetic_ui_fixture) && !key,
  });

  return NextResponse.json({
    run_id: run.run_id,
    mode: run.mode,
    runtype_state: key ? inventory.runtype_state || "CONFIGURED" : "NOT_CONFIGURED",
    perturbation: run.perturbation,
    reference_root: run.reference_root,
    stream_url: `/api/hydralamp/stream?run_id=${run.run_id}`,
    status_url: `/api/hydralamp/status?run_id=${run.run_id}`,
    label:
      run.mode === "SYNTHETIC_UI_FIXTURE"
        ? "SYNTHETIC FIXTURE ≠ LIVE RUNTYPE DEMO"
        : run.mode === "NOT_CONFIGURED"
          ? "RUNTYPE_STATE=NOT_CONFIGURED"
          : "LIVE_RUNTYPE",
  });
}

export async function GET() {
  loadHydraLampServerEnv();
  return NextResponse.json({
    runtype_api_key_present: runtypeKeyPresent(),
    inventory: loadModelInventory(),
    perturbations: ALLOWED,
  });
}
