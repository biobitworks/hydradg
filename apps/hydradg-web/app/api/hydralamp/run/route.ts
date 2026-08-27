import { NextResponse } from "next/server";
import { startHydraLampExperiment, runtypeKeyPresent, loadModelInventory } from "@/lib/hydralamp/coordinator";
import { loadHydraLampServerEnv } from "@/lib/hydralamp/env";
import { isVercelRuntime, NOT_HOSTED_ON_VERCEL, SCIENTIFIC_EXECUTION_AUTHORITY } from "@/lib/providers/vercelBoundary";
import type { ExecutionMode, PerturbationKind } from "@/lib/hydralamp/types";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const ALLOWED: PerturbationKind[] = [
  "CONTROL",
  "INVALID_PROOF",
  "REPLAYED_PROOF",
  "BROKEN_AUTHORIZATION_EDGE",
];

const MODES: ExecutionMode[] = [
  "DETERMINISTIC_FIXTURE",
  "LOCAL_MODEL_GUM_OLLARMA",
  "LIVE_RUNTYPE",
];

export async function POST(req: Request) {
  loadHydraLampServerEnv();
  const body = (await req.json().catch(() => ({}))) as {
    perturbation?: string;
    demo_20s?: boolean;
    allow_synthetic_ui_fixture?: boolean;
    mode?: string;
  };
  const perturbation = (ALLOWED.includes(body.perturbation as PerturbationKind)
    ? body.perturbation
    : "INVALID_PROOF") as PerturbationKind;

  const inventory = loadModelInventory();
  const key = runtypeKeyPresent();

  const requestedMode = MODES.includes(body.mode as ExecutionMode)
    ? (body.mode as ExecutionMode)
    : body.allow_synthetic_ui_fixture
      ? "DETERMINISTIC_FIXTURE"
      : undefined;

  if (isVercelRuntime() && requestedMode === "LOCAL_MODEL_GUM_OLLARMA") {
    return NextResponse.json(
      {
        error: "LOCAL_MODEL_NOT_HOSTED_ON_VERCEL",
        blocked_on_vercel: [...NOT_HOSTED_ON_VERCEL],
        scientific_execution_authority: SCIENTIFIC_EXECUTION_AUTHORITY,
        allowed_modes: ["DETERMINISTIC_FIXTURE", "LIVE_RUNTYPE"],
      },
      { status: 403 },
    );
  }

  const run = await startHydraLampExperiment({
    perturbation,
    demo_20s: Boolean(body.demo_20s),
    allow_synthetic_ui_fixture: Boolean(body.allow_synthetic_ui_fixture) && !key,
    mode: requestedMode,
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
      run.mode === "DETERMINISTIC_FIXTURE" || run.mode === "SYNTHETIC_UI_FIXTURE"
        ? "DETERMINISTIC FIXTURE ≠ LIVE RUNTYPE"
        : run.mode === "LOCAL_MODEL_GUM_OLLARMA"
          ? "LOCAL MODEL (Ollarma) — GUM Doctor unresolved"
          : run.mode === "NOT_CONFIGURED"
            ? "NOT_CONFIGURED"
            : "LIVE_RUNTYPE",
  });
}

export async function GET() {
  loadHydraLampServerEnv();
  const vercel = isVercelRuntime();
  return NextResponse.json({
    runtype_api_key_present: runtypeKeyPresent(),
    inventory: loadModelInventory(),
    perturbations: ALLOWED,
    modes: vercel ? MODES.filter((m) => m !== "LOCAL_MODEL_GUM_OLLARMA") : MODES,
    vercel_runtime: vercel,
    scientific_execution_authority: SCIENTIFIC_EXECUTION_AUTHORITY,
    blocked_on_vercel: [...NOT_HOSTED_ON_VERCEL],
  });
}
