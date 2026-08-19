import { readFile } from "node:fs/promises";

import { NextResponse } from "next/server";

import { addContextIcebergScores } from "@/lib/contextIceberg";
import { buildDemoFixture } from "@/lib/demoFixture";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type SceneNode = {
  id: string;
  label: string;
  x: number;
  y: number;
  z: number;
  t: number;
  access?: string;
  payload?: Record<string, unknown>;
  context_drift?: {
    cloud_drift_0_100?: number;
    delta_g_star?: number;
    scope?: string;
  };
};

type LiveIcebergPayload = {
  schema?: string;
  source_state?: string;
  claim_ceiling?: string;
  project_fcg_root?: string | null;
  hydradb_projection_root?: string | null;
  signature_state?: string;
  merkle_state?: string;
  timeline: ReadonlyArray<{
    t: number;
    label: string;
    distribution: readonly number[];
    g_star: number;
    delta_g_star: number;
    [key: string]: unknown;
  }>;
  scene: {
    nodes: ReadonlyArray<SceneNode>;
    links: ReadonlyArray<{ source: string; target: string; relation: string }>;
  };
};

function validatePayload(payload: LiveIcebergPayload) {
  if (!payload || !Array.isArray(payload.timeline) || !payload.timeline.length) {
    throw new Error("iceberg state requires a non-empty timeline");
  }
  if (!payload.scene || !Array.isArray(payload.scene.nodes) || !Array.isArray(payload.scene.links)) {
    throw new Error("iceberg state requires scene.nodes and scene.links");
  }
  for (const state of payload.timeline) {
    if (!Number.isFinite(state.t) || typeof state.label !== "string" || !Array.isArray(state.distribution)) {
      throw new Error("invalid iceberg timeline state");
    }
    if (!Number.isFinite(state.g_star) || !Number.isFinite(state.delta_g_star)) {
      throw new Error("iceberg timeline requires finite G* and delta G*");
    }
  }
}

function enrich(payload: LiveIcebergPayload) {
  validatePayload(payload);
  const timeline = addContextIcebergScores(payload.timeline);
  const byTime = new Map(timeline.map((state) => [state.t, state]));
  const scene = {
    ...payload.scene,
    nodes: payload.scene.nodes.map((node) => {
      const inherited = byTime.get(node.t);
      return {
        ...node,
        context_drift: {
          cloud_drift_0_100: node.context_drift?.cloud_drift_0_100 ?? inherited?.cloud_drift_0_100 ?? 0,
          delta_g_star: node.context_drift?.delta_g_star ?? inherited?.delta_g_star ?? 0,
          scope: node.context_drift?.scope ?? "STATE_INHERITED",
        },
      };
    }),
  };
  return { ...payload, timeline, scene };
}

function demoPayload(): LiveIcebergPayload {
  const fixture = buildDemoFixture();
  return {
    schema: "hydradg.context_iceberg.ui.v1",
    source_state: "DETERMINISTIC_SYNTHETIC_TEST_FIXTURE",
    claim_ceiling: "SYNTHETIC_INFORMATION_STATE_VISUALIZATION_ONLY",
    project_fcg_root: null,
    hydradb_projection_root: null,
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
    timeline: fixture.timeline,
    scene: fixture.scene,
  };
}

async function loadLivePayload(path: string) {
  const raw = await readFile(path, "utf8");
  const parsed = JSON.parse(raw) as LiveIcebergPayload;
  return enrich({
    ...parsed,
    schema: parsed.schema || "hydradg.context_iceberg.ui.v1",
    source_state: parsed.source_state || "LIVE_CUSTODY_ARTIFACT",
  });
}

export async function GET() {
  try {
    const statePath = process.env.HYDRADG_ICEBERG_STATE_PATH?.trim();
    const payload = statePath ? await loadLivePayload(statePath) : enrich(demoPayload());
    return NextResponse.json(
      {
        ...payload,
        refreshed_at: new Date().toISOString(),
        operational_note: "refreshed_at is operational metadata and is not part of the scientific identity",
      },
      { headers: { "Cache-Control": "no-store, max-age=0" } },
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return NextResponse.json(
      {
        error: message,
        source_state: "BLOCKED_INVALID_ICEBERG_STATE",
        claim_ceiling: "NO_VISUALIZATION_CLAIM",
      },
      { status: 500, headers: { "Cache-Control": "no-store, max-age=0" } },
    );
  }
}
