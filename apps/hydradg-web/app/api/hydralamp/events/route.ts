import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const EVENTS_PATH = path.join(
  process.cwd(),
  "..",
  "..",
  "eval",
  "hydralamp_20260826",
  "HYDRALAMP_EVENTS.jsonl",
);

export async function GET() {
  try {
    const raw = await readFile(EVENTS_PATH, "utf8");
    const events = raw
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line));
    const statusPath = path.join(path.dirname(EVENTS_PATH), "HYDRALAMP_STATUS.json");
    const statusRaw = await readFile(statusPath, "utf8").catch(() => "{}");
    const status = JSON.parse(statusRaw);
    return NextResponse.json({ events, status, event_count: events.length });
  } catch {
    return NextResponse.json({ events: [], status: {}, event_count: 0, error: "EVENTS_NOT_FOUND" });
  }
}
