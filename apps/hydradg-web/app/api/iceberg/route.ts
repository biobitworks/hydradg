import { createHash } from "node:crypto";
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

type TimelineState = {
  t: number;
  label: string;
  distribution: readonly number[];
  g_star: number;
  delta_g_star: number;
  js_divergence?: number;
  cloud_drift_0_100?: number;
  [key: string]: unknown;
};

type LiveIcebergPayload = {
  schema?: string;
  source_state?: string;
  claim_ceiling?: string;
  project_fcg_root?: string | null;
  hydradb_projection_root?: string | null;
  signature_state?: string;
  merkle_state?: string;
  timeline: ReadonlyArray<TimelineState>;
  scene: {
    nodes: ReadonlyArray<SceneNode>;
    links: ReadonlyArray<{ source: string; target: string; relation: string }>;
  };
};

function validateStructure(payload: LiveIcebergPayload) {
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

function validateFrozenLiveScores(payload: LiveIcebergPayload) {
  validateStructure(payload);
  for (const state of payload.timeline) {
    if (!Number.isFinite(state.js_divergence) || !Number.isFinite(state.cloud_drift_0_100)) {
      throw new Error("live iceberg timeline requires receipt-owned js_divergence and cloud_drift_0_100");
    }
    const js = Number(state.js_divergence);
    const drift = Number(state.cloud_drift_0_100);
    if (js < 0 || js > 1 || drift < 0 || drift > 100) {
      throw new Error("live iceberg drift scores are outside declared bounds");
    }
    if (Math.abs(drift - js * 100) > 1e-8) {
      throw new Error("live iceberg CloudDrift is inconsistent with 100 × JSD");
    }
  }
}

function inheritNodeScores(payload: LiveIcebergPayload) {
  const byTime = new Map(payload.timeline.map((state) => [state.t, state]));
  return {
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
}

function demoPayload(): LiveIcebergPayload {
  const fixture = buildDemoFixture();
  const timeline = addContextIcebergScores(fixture.timeline);
  const payload: LiveIcebergPayload = {
    schema: "hydradg.context_iceberg.ui.v1",
    source_state: "DETERMINISTIC_SYNTHETIC_TEST_FIXTURE",
    claim_ceiling: "SYNTHETIC_INFORMATION_STATE_VISUALIZATION_ONLY",
    project_fcg_root: null,
    hydradb_projection_root: null,
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
    timeline,
    scene: fixture.scene,
  };
  return { ...payload, scene: inheritNodeScores(payload) };
}

async function loadLivePayload(path: string) {
  const bytes = await readFile(path);
  const parsed = JSON.parse(bytes.toString("utf8")) as LiveIcebergPayload;
  validateFrozenLiveScores(parsed);
  const payload: LiveIcebergPayload = {
    ...parsed,
    schema: parsed.schema || "hydradg.context_iceberg.ui.v1",
    source_state: parsed.source_state || "LIVE_CANONICAL_CUSTODY_ARTIFACT",
  };
  return {
    ...payload,
    scene: inheritNodeScores(payload),
    artifact_sha256: createHash("sha256").update(bytes).digest("hex"),
    score_provenance: "RECEIPT_OWNED_READ_ONLY",
    local_path_disclosure: "NOT_INCLUDED",
  };
}

export async function GET() {
  try {
    const statePath = process.env.HYDRADG_ICEBERG_STATE_PATH?.trim();
    const payload = statePath
      ? await loadLivePayload(statePath)
      : {
          ...demoPayload(),
          score_provenance: "DETERMINISTIC_SYNTHETIC_UI_CONTROL",
        };
    return NextResponse.json(
      {
        ...payload,
        refreshed_at: new Date().toISOString(),
        operational_note: "refreshed_at is operational metadata and is not part of the scientific identity",
        release_watch_boundary: "LIVE_SCORES_ARE_READ_FROM_THE_FROZEN_ARTIFACT_RELEASE_WATCH_DOES_NOT_CHOOSE_GIBBS_WEIGHTS",
      },
      { headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" } },
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return NextResponse.json(
      {
        error: message,
        source_state: "BLOCKED_INVALID_ICEBERG_STATE",
        claim_ceiling: "NO_VISUALIZATION_CLAIM",
      },
      { status: 500, headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" } },
    );
  }
}
