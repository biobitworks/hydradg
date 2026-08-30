import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const turnsPath = path.join(
      process.cwd(),
      "../../eval/hosted_migration_20260820/CONVERSATION_TURNS_FCO.jsonl",
    );
    if (!fs.existsSync(turnsPath)) {
      return NextResponse.json({ error: "CONVERSATION_TURNS_FCO.jsonl receipt not found" }, { status: 404 });
    }

    const fileContent = fs.readFileSync(turnsPath, "utf-8");
    const lines = fileContent.split("\n").filter((line) => Boolean(line.trim()));
    const nodes = lines.map((line) => JSON.parse(line));

    return NextResponse.json({
      conversation_id: "eee59322-9ae9-4eb7-a286-acc43ba20a29",
      agent_identity: "Antigravity/Gemini Pro",
      total_turn_fcos: nodes.length,
      license: "CC-BY-NC-ND-4.0",
      ingestion_status: "SEEDGRAPH_ADMITTED_HASHED",
      nodes: nodes.slice(0, 50),
    });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
