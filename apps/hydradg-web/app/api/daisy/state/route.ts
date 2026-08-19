import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const pending = {
  schema: "hydradg.release_watch_daisy_state.v1",
  state: "PENDING_EXTERNAL_TO_RELEASE_WATCH",
  read_only: true,
  active_scientific_lane_owner: "DAISY_GEMINI_ANTIGRAVITY",
  current_gate: "STABLE_CANONICAL_HANDOFF_PENDING",
  next_action: "WAIT_FOR_STABLE_DAISY_HANDOFF",
  claim_ceiling: "RELEASE_WATCH_RESUME_STATE_ONLY",
  signature_state: "PENDING_EXTERNAL_PRIVATE_KEY_OPERATION",
  merkle_state: "NOT_MERKLE_COMMITTED",
};

export async function GET() {
  const path = process.env.HYDRADG_DAISY_STATE_JSON?.trim();
  if (!path) return Response.json(pending, { headers: { "Cache-Control": "no-store", "X-HydraDG-Read-Only": "true" } });
  try {
    const bytes = await readFile(path);
    return Response.json({
      schema: "hydradg.release_watch_daisy_state.v1",
      state: "READ_ONLY_HANDOFF_LOADED",
      read_only: true,
      artifact_sha256: createHash("sha256").update(bytes).digest("hex"),
      daisy_state: JSON.parse(bytes.toString("utf8")),
      local_path_disclosure: "NOT_INCLUDED",
      claim_ceiling: "DAISY_STATE_FILE_READOUT_ONLY",
    }, { headers: { "Cache-Control": "no-store", "X-HydraDG-Read-Only": "true" } });
  } catch (error) {
    return Response.json({ ...pending, state: "BLOCKED", blocker: "DAISY_STATE_READ_FAILED", error: error instanceof Error ? error.message : String(error) }, {
      status: 503,
      headers: { "Cache-Control": "no-store", "X-HydraDG-Read-Only": "true" },
    });
  }
}
