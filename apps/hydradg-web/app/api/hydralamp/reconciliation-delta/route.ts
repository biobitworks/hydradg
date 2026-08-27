import { readFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";

export async function GET() {
  const publicPath = path.join(process.cwd(), "public", "demo", "reconciliation-delta-use-case.json");
  try {
    const raw = readFileSync(publicPath, "utf8");
    const data = JSON.parse(raw);
    return NextResponse.json({
      ...data,
      custody_note: "PROJECTION_ONLY_DERIVED_EVIDENCE — not canonical FCG membership.",
    });
  } catch {
    return NextResponse.json({ error: "RECONCILIATION_DELTA_NOT_AVAILABLE" }, { status: 503 });
  }
}
