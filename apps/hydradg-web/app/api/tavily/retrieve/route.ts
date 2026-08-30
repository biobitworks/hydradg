import { NextResponse } from "next/server";
import { publicQuarantine } from "@/lib/providers/types";
import { tavilyRetrieve, type TavilyOperation } from "@/lib/providers/tavily";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const OPS: TavilyOperation[] = ["search", "extract", "crawl", "map"];

export async function POST(req: Request) {
  let body: {
    operation?: string;
    query?: string;
    url?: string;
    urls?: string[];
  };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "INVALID_JSON" }, { status: 400 });
  }

  const operation = body.operation as TavilyOperation;
  if (!OPS.includes(operation)) {
    return NextResponse.json({ error: "UNKNOWN_OPERATION", allowed: OPS }, { status: 400 });
  }

  const result = await tavilyRetrieve({
    operation,
    query: typeof body.query === "string" ? body.query : undefined,
    url: typeof body.url === "string" ? body.url : undefined,
    urls: Array.isArray(body.urls) ? body.urls.filter((u) => typeof u === "string") : undefined,
  });

  return NextResponse.json({
    ...result,
    quarantine: result.quarantine ? publicQuarantine(result.quarantine) : null,
  });
}

export async function GET() {
  return NextResponse.json({
    provider: "Tavily",
    operations: OPS,
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
    custody_state: "QUARANTINED",
    fcg_append: "NOT_APPENDED",
    seedgraph_canonical_write: false,
    note: "POST with operation=search|extract|crawl|map. Results never mutate canonical SeedGraph or FCG.",
  });
}
