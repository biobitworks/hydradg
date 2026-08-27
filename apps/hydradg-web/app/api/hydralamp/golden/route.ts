import { NextResponse } from "next/server";
import { loadHydraLampServerEnv } from "@/lib/hydralamp/env";
import {
  unlockGoldenPath,
  stepGoldenPath,
  pauseGoldenPath,
  resetGoldenPath,
  setFollowCurrent,
  setFocus,
  getGoldenRun,
  publicRunView,
} from "@/lib/hydralamp/goldenPathMachine";
import { defaultTaskPrompt } from "@/lib/hydralamp/judgeSession";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

type Action =
  | "unlock"
  | "run"
  | "pause"
  | "step"
  | "reset"
  | "status"
  | "follow"
  | "focus"
  | "defaults";

export async function GET() {
  return NextResponse.json({
    schema: "hydralamp.golden_path_api.v1",
    actions: ["unlock", "run", "pause", "step", "reset", "status", "follow", "focus", "defaults"],
    default_task_prompt: defaultTaskPrompt(),
    judge_key_hint: "Demo capability e.g. JUDGE-HYDRA-2026 — not a cryptographic signing key",
    phase_rail: ["UNLOCK", "REFERENCE", "POISON", "AGENT", "VERIFY", "ANTIDOTE", "RESTORATION", "RECEIPT"],
  });
}

export async function POST(req: Request) {
  loadHydraLampServerEnv();
  const body = (await req.json().catch(() => ({}))) as {
    action?: Action;
    judge_key?: string;
    task_prompt?: string;
    run_id?: string;
    follow?: boolean;
    focus?: "current" | "poison" | "divergence" | "restoration" | "centroid";
  };
  const action = body.action || "status";

  try {
    if (action === "defaults") {
      return NextResponse.json({ default_task_prompt: defaultTaskPrompt() });
    }

    if (action === "unlock" || action === "reset") {
      const fn = action === "reset" ? resetGoldenPath : unlockGoldenPath;
      const result = fn({
        judge_key: body.judge_key || "",
        task_prompt: body.task_prompt,
      });
      if (!result.ok) {
        return NextResponse.json(result, { status: 401 });
      }
      return NextResponse.json({
        ok: true,
        run: publicRunView(result.run),
        session: {
          session_id: result.session.session_id,
          label: result.session.label,
          authorization_fco_id: result.session.authorization_fco_id,
          cryptographic_signed: false,
          namespace: result.session.namespace,
          claim_ceiling: result.session.claim_ceiling,
        },
      });
    }

    if (!body.run_id) {
      return NextResponse.json({ error: "run_id required" }, { status: 400 });
    }

    if (action === "status") {
      const run = getGoldenRun(body.run_id);
      if (!run) return NextResponse.json({ error: "NOT_FOUND" }, { status: 404 });
      return NextResponse.json({ ok: true, run: publicRunView(run) });
    }

    if (action === "pause") {
      return NextResponse.json({ ok: true, run: publicRunView(pauseGoldenPath(body.run_id)) });
    }

    if (action === "step") {
      const run = stepGoldenPath(body.run_id);
      return NextResponse.json({ ok: true, run: publicRunView(run) });
    }

    if (action === "run") {
      const existing = getGoldenRun(body.run_id);
      if (!existing) return NextResponse.json({ error: "NOT_FOUND" }, { status: 404 });
      existing.paused = false;
      existing.follow_current = true;
      let run = existing;
      for (let i = 0; i < 10; i++) {
        if (run.done) break;
        run = stepGoldenPath(body.run_id);
      }
      return NextResponse.json({ ok: true, run: publicRunView(run) });
    }

    if (action === "follow") {
      return NextResponse.json({
        ok: true,
        run: publicRunView(setFollowCurrent(body.run_id, Boolean(body.follow))),
      });
    }

    if (action === "focus") {
      if (!body.focus) return NextResponse.json({ error: "focus required" }, { status: 400 });
      return NextResponse.json({ ok: true, run: publicRunView(setFocus(body.run_id, body.focus)) });
    }

    return NextResponse.json({ error: `unknown action ${action}` }, { status: 400 });
  } catch (e) {
    return NextResponse.json(
      { error: String((e as Error).message || e).slice(0, 200) },
      { status: 500 },
    );
  }
}
