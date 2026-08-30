#!/usr/bin/env npx tsx
/**
 * End-to-end anonymous link verification before Hacker Bob / judge handoff.
 * HydraLamp /api/health sha is the canonical deployed-version check.
 */
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const HYDRALAMP_BASE = process.env.HYDRALAMP_PUBLIC_URL || "https://hydralamp.vercel.app";
const HYDRADG_BASE = process.env.HYDRADG_PUBLIC_URL || "https://hydradg.vercel.app";
const EXPECTED_HYDRALAMP_SHA =
  process.env.EXPECTED_HYDRALAMP_SHA || "c6dcadfeff0fa31e63e7865b04e1bef07511edaf";
const EXPECTED_HYDRADG_SHA =
  process.env.EXPECTED_HYDRADG_SHA || "56efebd10a8e206f3bc60937dd6e629beea60302";

const OUT = join(process.cwd(), "eval/vercel_public_closeout_20260827");
mkdirSync(OUT, { recursive: true });

type Check = {
  name: string;
  url: string;
  pass: boolean;
  http_status: number | null;
  detail: string;
  category: "hydralamp" | "hydradg" | "media" | "sha" | "manifest";
};

const checks: Check[] = [];

async function fetchStatus(url: string, init?: RequestInit): Promise<{ status: number; body: Buffer; headers: Headers }> {
  const res = await fetch(url, { ...init, redirect: "follow" });
  const buf = Buffer.from(await res.arrayBuffer());
  return { status: res.status, body: buf, headers: res.headers };
}

function record(
  name: string,
  url: string,
  pass: boolean,
  http_status: number | null,
  detail: string,
  category: Check["category"],
) {
  checks.push({ name, url, pass, http_status, detail, category });
}

async function verifyRoute(name: string, url: string, category: Check["category"] = "hydralamp") {
  try {
    const { status } = await fetchStatus(url);
    record(name, url, status === 200, status, `http=${status}`, category);
  } catch (err) {
    record(name, url, false, null, String(err), category);
  }
}

async function verifyMediaSha(name: string, url: string, expectedSha: string) {
  try {
    const { status, body } = await fetchStatus(url);
    if (status !== 200) {
      record(name, url, false, status, `http=${status}`, "media");
      return;
    }
    const got = createHash("sha256").update(body).digest("hex");
    const pass = got === expectedSha;
    record(name, url, pass, status, `sha=${got.slice(0, 16)}… expected=${expectedSha.slice(0, 16)}…`, "media");
  } catch (err) {
    record(name, url, false, null, String(err), "media");
  }
}

async function main() {
  const hydralampRoutes: Array<[string, string]> = [
    ["ROOT_200", `${HYDRALAMP_BASE}/`],
    ["GOLDEN_200", `${HYDRALAMP_BASE}/golden`],
    ["STATIC_200", `${HYDRALAMP_BASE}/demo/index.html`],
    ["AGENT_CARD_200", `${HYDRALAMP_BASE}/.well-known/agent.json`],
    ["HEALTH_200", `${HYDRALAMP_BASE}/api/health`],
    ["MANIFEST_200", `${HYDRALAMP_BASE}/submission_media/MEDIA_SUBMISSION_MANIFEST.json`],
    ["VIDEO_20S_200", `${HYDRALAMP_BASE}/submission_media/HYDRALAMP_DEMO_20S.mp4`],
    ["VIDEO_3MIN_200", `${HYDRALAMP_BASE}/submission_media/HYDRALAMP_DEMO_3MIN.mp4`],
  ];

  for (const [name, url] of hydralampRoutes) {
    await verifyRoute(name, url, name.startsWith("VIDEO") ? "media" : "hydralamp");
  }

  for (const png of ["00_reference", "01_poison", "02_denied", "03_repair", "04_restored"]) {
    await verifyRoute(`PNG_${png.toUpperCase()}_200`, `${HYDRALAMP_BASE}/submission_media/${png}.fco.png`, "media");
  }

  try {
    const healthUrl = `${HYDRALAMP_BASE}/api/health`;
    const { status, body } = await fetchStatus(healthUrl);
    const json = JSON.parse(body.toString("utf8"));
    const sha = String(json.sha ?? "MISSING");
    const shaPass = sha === EXPECTED_HYDRALAMP_SHA;
    record(
      "HYDRALAMP_PRODUCTION_SHA",
      healthUrl,
      status === 200 && shaPass,
      status,
      `sha=${sha} expected=${EXPECTED_HYDRALAMP_SHA}`,
      "sha",
    );
  } catch (err) {
    record("HYDRALAMP_PRODUCTION_SHA", `${HYDRALAMP_BASE}/api/health`, false, null, String(err), "sha");
  }

  let manifest: { artifacts?: Array<{ path: string; sha256: string }> } | null = null;
  try {
    const manifestUrl = `${HYDRALAMP_BASE}/submission_media/MEDIA_SUBMISSION_MANIFEST.json`;
    const { status, body } = await fetchStatus(manifestUrl);
    if (status === 200) manifest = JSON.parse(body.toString("utf8"));
    record("MANIFEST_PARSE", manifestUrl, status === 200 && !!manifest?.artifacts?.length, status, `artifacts=${manifest?.artifacts?.length ?? 0}`, "manifest");
  } catch (err) {
    record("MANIFEST_PARSE", `${HYDRALAMP_BASE}/submission_media/MEDIA_SUBMISSION_MANIFEST.json`, false, null, String(err), "manifest");
  }

  if (manifest?.artifacts) {
    for (const art of manifest.artifacts) {
      if (!art.path.startsWith("submission_media/") || art.path.includes("golden-path")) continue;
      const url = `${HYDRALAMP_BASE}/${art.path.replace(/^submission_media\//, "submission_media/")}`;
      await verifyMediaSha(`MEDIA_SHA_${art.path.split("/").pop()}`, url, art.sha256);
    }
    const allMediaSha = checks.filter((c) => c.name.startsWith("MEDIA_SHA_"));
    record(
      "MEDIA_SHA_VERIFY",
      `${HYDRALAMP_BASE}/submission_media/`,
      allMediaSha.length > 0 && allMediaSha.every((c) => c.pass),
      200,
      `${allMediaSha.filter((c) => c.pass).length}/${allMediaSha.length} match manifest`,
      "manifest",
    );
  }

  const hydradgRoutes: Array<[string, string]> = [
    ["HYDRADG_ROOT_200", `${HYDRADG_BASE}/`],
    ["FULL_SUBMISSION_200", `${HYDRADG_BASE}/submission`],
    ["HYDRADG_HYDRALAMP_200", `${HYDRADG_BASE}/hydralamp`],
    ["HYDRADG_JUDGE_200", `${HYDRADG_BASE}/judge`],
    ["HYDRADG_PROVIDERS_200", `${HYDRADG_BASE}/providers`],
    ["HYDRADG_GRAPH_200", `${HYDRADG_BASE}/graph`],
    ["HYDRADG_KNOWLEDGE_200", `${HYDRADG_BASE}/knowledge`],
    ["HYDRADG_HOWTO_200", `${HYDRADG_BASE}/how-to`],
    ["HYDRADG_ELIGIBILITY_200", `${HYDRADG_BASE}/eligibility`],
  ];

  for (const [name, url] of hydradgRoutes) {
    await verifyRoute(name, url, "hydradg");
  }

  const pass = checks.every((c) => c.pass);
  const receipt = {
    schema: "hydradg.public_links_e2e_receipt.v1",
    recorded_at_utc: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    execution_host: "magicSTUDIObox.local",
    hydralamp_base: HYDRALAMP_BASE,
    hydradg_base: HYDRADG_BASE,
    expected_hydralamp_sha: EXPECTED_HYDRALAMP_SHA,
    expected_hydradg_source_sha: EXPECTED_HYDRADG_SHA,
    version_check_policy: "HydraLamp /api/health sha is canonical deployed-version gate; redeployment anomalies recorded in FCG not overwritten.",
    fresh_context: true,
    auth_cookies: false,
    pass,
    PUBLIC_LINKS_E2E: pass ? "PASS" : "FAIL",
    checks,
    hacker_bob_prerequisite: pass ? "READY" : "BLOCKED_LINK_FAILURE",
    signature_state: "NOT_SIGNED",
    fcg_append_state: "NOT_APPENDED",
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
  };

  writeFileSync(join(OUT, "PUBLIC_LINKS_E2E_RECEIPT.json"), JSON.stringify(receipt, null, 2) + "\n");
  console.log(
    JSON.stringify(
      {
        PUBLIC_LINKS_E2E: pass ? "PASS" : "FAIL",
        HYDRALAMP_SHA_CHECK: checks.find((c) => c.name === "HYDRALAMP_PRODUCTION_SHA")?.pass ?? false,
        failing: checks.filter((c) => !c.pass).map((c) => c.name),
      },
      null,
      2,
    ),
  );
  process.exit(pass ? 0 : 1);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
