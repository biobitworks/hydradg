import { NextResponse } from "next/server";
import path from "node:path";
import { executeGatewayTool, type GatewayToolName } from "@/lib/sponsors/evidenceGateway";

function repoRootFromCwd(): string {
  return path.resolve(process.cwd(), "..", "..");
}

const ALLOWED: GatewayToolName[] = [
  "discover_capabilities",
  "query_evidence",
  "propose_external_evidence",
  "verify_custody_receipt",
];

export async function POST(req: Request) {
  let body: { tool?: string; args?: Record<string, unknown> };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "INVALID_JSON" }, { status: 400 });
  }
  const tool = body.tool as GatewayToolName;
  if (!ALLOWED.includes(tool)) {
    return NextResponse.json({ error: "UNKNOWN_TOOL", allowed: ALLOWED }, { status: 400 });
  }
  const result = executeGatewayTool(tool, repoRootFromCwd(), body.args || {});
  return NextResponse.json({ tool, result, custody_note: "Not canonical FCG state." });
}

export async function GET() {
  return NextResponse.json(executeGatewayTool("discover_capabilities", repoRootFromCwd()));
}
