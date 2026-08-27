#!/usr/bin/env node
/**
 * Local website route + judge metric stress (fetch-based; no frozen source mutation).
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "eval", "ollarma_measurement_review_20260827");
const BASE = process.env.LOCAL_URL || "http://127.0.0.1:3011";
const FROZEN_SHA = "44e9d3dc7014b9b2c410a9e1e2c9b35a72cd269e4e561eba40414081ca81690d";

const ROUTES = [
  "/",
  "/hydralamp",
  "/judge",
  "/evidence",
  "/how-to",
  "/knowledge",
  "/demo/judge-metric-surface.json",
  "/demo/reconciliation-delta-use-case.json",
  "/api/hydralamp/reconciliation-delta",
  "/api/agent-native/evidence-gateway",
  "/api/status",
];

function sha256File(p) {
  const h = crypto.createHash("sha256");
  h.update(fs.readFileSync(p));
  return h.digest("hex");
}

async function checkRoute(route) {
  const url = `${BASE.replace(/\/$/, "")}${route}`;
  try {
    const res = await fetch(url, { redirect: "manual" });
    const body = res.status === 200 ? await res.text() : "";
    return { route, url, status: res.status, pass: res.status >= 200 && res.status < 400, bytes: body.length };
  } catch (e) {
    return { route, url, status: 0, pass: false, error: String(e) };
  }
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const routeResults = await Promise.all(ROUTES.map(checkRoute));
  const judgeRes = await fetch(`${BASE}/demo/judge-metric-surface.json`);
  const judgeJson = judgeRes.ok ? await judgeRes.json() : null;
  const judgeEquality =
    judgeJson?.FROZEN_46_EVENT_SHA256 === FROZEN_SHA &&
    judgeJson?.FROZEN_EVENT_COUNT === 46 &&
    judgeJson?.metrics?.length === 8;

  const eventsPath = path.join(ROOT, "eval/hydralamp_20260826/HYDRALAMP_EVENTS.jsonl");
  const eventsSha = fs.existsSync(eventsPath) ? sha256File(eventsPath) : "MISSING";
  const freezeViolation = eventsSha !== FROZEN_SHA;

  const stress = {
    schema: "hydradg.ollarma_measurement_review.local_website_stress.v1",
    recorded_at_utc: new Date().toISOString(),
    LOCAL_URL: BASE,
    FROZEN_46_EVENT_SHA256: eventsSha,
    FROZEN_EVENT_COUNT: 46,
    SUBMISSION_FREEZE_VIOLATION: freezeViolation,
    JUDGE_METRIC_EQUALITY: judgeEquality ? "PASS" : "FAIL",
    route_matrix: routeResults,
    ROUTE_PASS_COUNT: routeResults.filter((r) => r.pass).length,
    ROUTE_FAIL_COUNT: routeResults.filter((r) => !r.pass).length,
    BROWSER_STRESS: routeResults.every((r) => r.pass) && judgeEquality && !freezeViolation ? "PASS" : "PARTIAL",
    note: "Fetch-based stress; Playwright gauntlet optional separately.",
  };

  const matrix = {
    schema: "hydradg.ollarma_measurement_review.local_website_route_matrix.v1",
    recorded_at_utc: stress.recorded_at_utc,
    routes: routeResults,
  };

  const manifest = {
    schema: "hydradg.ollarma_measurement_review.local_website_screenshot_manifest.v1",
    recorded_at_utc: stress.recorded_at_utc,
    screenshots: [],
    note: "Screenshot capture deferred; route matrix + judge JSON hash recorded.",
    judge_metric_surface_sha256: fs.existsSync(
      path.join(ROOT, "apps/hydradg-web/public/demo/judge-metric-surface.json"),
    )
      ? sha256File(path.join(ROOT, "apps/hydradg-web/public/demo/judge-metric-surface.json"))
      : null,
  };

  fs.writeFileSync(path.join(OUT, "LOCAL_WEBSITE_STRESS_RECEIPT.json"), JSON.stringify(stress, null, 2) + "\n");
  fs.writeFileSync(path.join(OUT, "LOCAL_WEBSITE_ROUTE_MATRIX.json"), JSON.stringify(matrix, null, 2) + "\n");
  fs.writeFileSync(path.join(OUT, "LOCAL_WEBSITE_SCREENSHOT_MANIFEST.json"), JSON.stringify(manifest, null, 2) + "\n");
  console.log(JSON.stringify({ stress: stress.BROWSER_STRESS, judgeEquality, freezeViolation }, null, 2));
  if (freezeViolation) process.exit(2);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
