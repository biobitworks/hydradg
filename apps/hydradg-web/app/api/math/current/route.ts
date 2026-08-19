import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

import {
  PENDING_CONTEXT_ICEBERG,
  type ContextIcebergObservation,
} from "@/lib/contextIceberg";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function response(body: unknown, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      "Cache-Control": "no-store, max-age=0",
      "X-HydraDG-Read-Only": "true",
    },
  });
}

function isObservation(value: unknown): value is ContextIcebergObservation {
  if (!value || typeof value !== "object") return false;
  const item = value as Record<string, unknown>;
  return item.schema === "hydradg.context_iceberg_projection.v1"
    && typeof item.state === "string"
    && item.read_only === true
    && typeof item.scores === "object"
    && typeof item.governance === "object";
}

export async function GET() {
  const configuredPath = process.env.HYDRADG_CONTEXT_ICEBERG_JSON?.trim();
  if (!configuredPath) {
    return response({
      ...PENDING_CONTEXT_ICEBERG,
      source: "NO_CONFIGURED_CANONICAL_RECEIPT",
      gibbs_config_state: "PENDING",
      distribution_reference_state: "PENDING",
      note: "Release Watch does not choose G* weights or invent CloudDrift values. Configure HYDRADG_CONTEXT_ICEBERG_JSON only after Daisy freezes and writes the canonical read-only observation receipt.",
    });
  }

  try {
    const bytes = await readFile(configuredPath);
    if (bytes.byteLength > 5_000_000) {
      return response({
        ...PENDING_CONTEXT_ICEBERG,
        state: "ERROR",
        blocker: "CONTEXT_ICEBERG_RECEIPT_TOO_LARGE",
      }, 422);
    }
    const parsed = JSON.parse(bytes.toString("utf8"));
    if (!isObservation(parsed)) {
      return response({
        ...PENDING_CONTEXT_ICEBERG,
        state: "ERROR",
        blocker: "CONTEXT_ICEBERG_SCHEMA_MISMATCH",
      }, 422);
    }

    const artifactSha256 = createHash("sha256").update(bytes).digest("hex");
    return response({
      ...parsed,
      artifact_sha256: artifactSha256,
      source: "CONFIGURED_READ_ONLY_CANONICAL_RECEIPT",
      local_path_disclosure: "NOT_INCLUDED",
    });
  } catch (error) {
    return response({
      ...PENDING_CONTEXT_ICEBERG,
      state: "ERROR",
      blocker: "CONTEXT_ICEBERG_RECEIPT_READ_FAILED",
      error: error instanceof Error ? error.message : String(error),
    }, 503);
  }
}
