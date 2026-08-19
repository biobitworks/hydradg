import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";

export const dynamic = "force-dynamic";

export async function GET() {
  return Response.json(buildKnowledgeProjection(), {
    headers: {
      "Cache-Control": "no-store, max-age=0",
      "X-HydraDG-Read-Only": "true",
    },
  });
}
