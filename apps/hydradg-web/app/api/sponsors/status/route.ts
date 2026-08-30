import { NextResponse } from "next/server";
import path from "node:path";
import { sponsorStatusPayload } from "@/lib/sponsors/registry";

function repoRootFromCwd(): string {
  // apps/hydradg-web -> hydradg root
  return path.resolve(process.cwd(), "..", "..");
}

export async function GET() {
  const payload = sponsorStatusPayload(repoRootFromCwd());
  return NextResponse.json(payload);
}
