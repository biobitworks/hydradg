import { NextResponse } from "next/server";

import { graphBackend, graphConfigured, probeGraph } from "@/lib/graph";
import { eligibilityClaimCeiling, hackHydraEligibility } from "@/lib/eligibility";
import { projectSources } from "@/lib/sources";

export const runtime = "nodejs";

export async function GET() {
  const graph = await probeGraph();
  return NextResponse.json({
    app: "HydraDG",
    track: "Hack Hydra Track 03 — Memory + Context Retrieval",
    graph: {
      backend: graphBackend(),
      configured: graphConfigured(),
      reachable: graph.ok,
      error: graph.error || null,
    },
    providers: {
      exa: Boolean(process.env.EXA_API_KEY),
      tavily: Boolean(process.env.TAVILY_API_KEY),
      daytona: Boolean(process.env.DAYTONA_API_KEY),
      mitosis: Boolean(process.env.MI_API_KEY),
      tenki: Boolean(process.env.TENKI_API_KEY),
      gmi: Boolean(process.env.GMI_API_KEY),
      modal: Boolean(process.env.MODAL_ENDPOINT_URL && process.env.MODAL_PROXY_TOKEN),
    },
    hydradb_pin: {
      repository: "hydra-db/hydradb",
      commit: "6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219",
      claim_ceiling: "SOURCE_REVISION_PIN_ONLY",
    },
    eligibility: {
      claim_ceiling: eligibilityClaimCeiling,
      items: hackHydraEligibility,
    },
    sources: projectSources,
  });
}
