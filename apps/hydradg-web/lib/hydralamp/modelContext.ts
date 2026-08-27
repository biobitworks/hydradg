import { randomUUID } from "node:crypto";
import {
  hashModelContext,
  hashKgSnapshot,
} from "./hash";
import type { FixtureState, ModelContextReceipt } from "./types";

export function buildModelVisibleContext(params: {
  run_id: string;
  actor_id: string;
  lane: string;
  state: FixtureState;
  fcg_root: string;
  capability_scope: string[];
  public_only?: boolean;
}): ModelContextReceipt {
  const { run_id, actor_id, lane, state, fcg_root, capability_scope } = params;
  const public_only = params.public_only !== false;

  // Never include private plaintext for unauthorized actors.
  const objects: Record<string, unknown> = {};
  for (const [id, obj] of Object.entries(state.objects)) {
    const classification = String(obj.payload.classification || "public");
    if (public_only && classification === "private") {
      objects[id] = {
        id,
        type: obj.type,
        object_sha256: obj.object_sha256,
        classification: "private_redacted",
        payload: { redacted: true },
      };
      continue;
    }
    objects[id] = {
      id,
      type: obj.type,
      object_sha256: obj.object_sha256,
      payload: obj.payload,
    };
  }

  const model_visible_context = {
    run_id,
    actor_id,
    lane,
    state_id: state.state_id,
    state_root: state.state_root,
    source_fcg_root: fcg_root,
    objects,
    edges: state.edges,
    capability_scope,
  };

  const context_hash = hashModelContext(model_visible_context);
  const token_count = JSON.stringify(model_visible_context).length; // deterministic proxy, not tokenizer claim

  return {
    context_id: `ctx_${randomUUID().slice(0, 12)}`,
    context_hash,
    source_fco_ids: Object.keys(state.objects),
    source_edge_ids: state.edges.map((e, i) => `${e.type}:${e.from}->${e.to}:${i}`),
    source_fcg_root: fcg_root,
    actor_capability_scope: capability_scope,
    public_private: public_only ? "public" : "private_redacted",
    token_count,
    model_visible_context,
  };
}

export function kgSnapshotHash(state: FixtureState): string {
  return hashKgSnapshot({ objects: state.objects, edges: state.edges });
}
