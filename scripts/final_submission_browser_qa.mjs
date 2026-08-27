#!/usr/bin/env node
/** Cursor independent public browser QA — metadata only, no secrets. */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const urls = [
  { name: "hydralamp_prod", url: "https://hydralamp.vercel.app/", expect: 200 },
  { name: "hydralamp_health", url: "https://hydralamp.vercel.app/api/health", expect: 200 },
  { name: "hydralamp_media", url: "https://hydralamp.vercel.app/api/media-custody", expect: [200, 404] },
  { name: "codex_exact_sha_preview", url: "https://hydralamp-polmh5v8x-biobitworks.vercel.app/", expect: "sso_or_200" },
  { name: "hydradg_prod_root", url: "https://hydradg.vercel.app/", expect: 200 },
  { name: "hydradg_prod_hydralamp", url: "https://hydradg.vercel.app/hydralamp", expect: [200, 404] },
];

async function check(entry) {
  const res = await fetch(entry.url, { redirect: "manual" });
  const code = res.status;
  let pass = false;
  if (entry.expect === "sso_or_200") {
    pass = code === 200 || code === 302;
  } else if (Array.isArray(entry.expect)) {
    pass = entry.expect.includes(code);
  } else {
    pass = code === entry.expect;
  }
  let bodySnippet = "";
  if (code === 200 && entry.url.includes("/api/")) {
    const t = await res.text();
    bodySnippet = t.slice(0, 120);
  }
  return {
    name: entry.name,
    url: entry.url,
    http_status: code,
    pass,
    sso_redirect: code === 302,
    body_snippet: bodySnippet || undefined,
  };
}

async function main() {
  const results = await Promise.all(urls.map(check));
  const out = {
    schema: "hydradg.final_submission.public_browser_qa.v1",
    recorded_at_utc: new Date().toISOString(),
    actor: "cursor_independent_cold_fetch",
    results,
    hydralamp_prod_anonymous_pass: results.find((r) => r.name === "hydralamp_prod")?.pass ?? false,
    codex_exact_sha_sso_blocked: results.find((r) => r.name === "codex_exact_sha_preview")?.sso_redirect ?? false,
    PUBLIC_BROWSER_PASS: results.find((r) => r.name === "hydralamp_prod")?.pass ? "PASS" : "BLOCKED",
    note: "Cold fetch QA — not full Playwright gauntlet. Codex receipt overrides when present.",
  };
  const outDir = path.join(__dirname, "..", "eval", "final_submission_20260827");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "PUBLIC_VERCEL_BROWSER_RECEIPT.json"), JSON.stringify(out, null, 2) + "\n");
  console.log(JSON.stringify(out, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
