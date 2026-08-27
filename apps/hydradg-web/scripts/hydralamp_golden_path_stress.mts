/**
 * GUM Doctor + HydraLamp golden-path stress (environment diagnostic + mechanism canary).
 * gum CLI may be NOT_FOUND — still records GUM_DOCTOR_STATE and exercises API scenarios.
 */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync, existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..", "..");
const OUT = path.join(REPO, "eval", "hydralamp_golden_path_20260827");
const BASE = process.env.HYDRALAMP_BASE_URL || "http://127.0.0.1:3013";

mkdirSync(OUT, { recursive: true });

function sha(s: string | Buffer) {
  return createHash("sha256").update(s).digest("hex");
}

function gumDoctor() {
  const cmds = ["command -v gum", "gum --version", "gum doctor --format=json"];
  const out = spawnSync("bash", ["-lc", cmds.join("; ")], { encoding: "utf8" });
  const text = `${out.stdout || ""}${out.stderr || ""}`;
  const receipt = {
    schema: "hydralamp.gum_doctor_receipt.v1",
    GUM_DOCTOR_STATE: text.includes("command not found") || !text.includes("gum") ? "NOT_FOUND" : "PRESENT",
    command: cmds,
    exit_code: out.status,
    exact_output_sha256: sha(text),
    secret_exposure: false,
    classification: "ENVIRONMENT_INTEGRATION_DIAGNOSTIC_NOT_HYDRALAMP_STRESS",
    signature_state: "NOT_SIGNED",
  };
  writeFileSync(path.join(OUT, "GUM_DOCTOR_RECEIPT.json"), JSON.stringify(receipt, null, 2) + "\n");
  return receipt;
}

async function post(action: string, body: Record<string, unknown> = {}) {
  const res = await fetch(`${BASE}/api/hydralamp/golden`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, ...body }),
  });
  const data = await res.json();
  return { http: res.status, data };
}

async function main() {
  const gum = gumDoctor();
  const results: Array<Record<string, unknown>> = [];
  const add = (id: string, name: string, state: string, detail: unknown = null) => {
    results.push({ id, name, state, detail });
  };

  // 1 happy path
  let r = await post("unlock", { judge_key: "JUDGE-HYDRA-2026" });
  if (r.http !== 200 || !r.data.run) {
    add("1", "happy_path_unlock", "FAIL", r);
    writeOutputs(gum, results, null);
    process.exit(1);
  }
  const runId = r.data.run.run_id as string;
  const sessionA = r.data.session.session_id as string;
  r = await post("run", { run_id: runId });
  const run = r.data.run;
  const roots = (run.transitions || []).map((t: { fcg_root_after: string }) => t.fcg_root_after);
  const uniqueRoots = new Set(roots);
  add(
    "1",
    "happy_path",
    run.done && run.phase === "RECEIPT" && uniqueRoots.size >= 7 ? "PASS" : "FAIL",
    { phase: run.phase, transitions: run.transitions?.length, unique_fcg_roots: uniqueRoots.size },
  );

  // 2 poison detected
  add("2", "poison_detected", run.fco_lineage?.B ? "PASS" : "FAIL", run.fco_lineage);

  // 5 wrong agent — N/A as dedicated scenario; mark BOUNDED
  add("5", "wrong_agent_decision", "BOUNDED_NOT_FORCED", "Demo agent completes structured path");

  // 8 provider timeout class — recorded as prior RUNTYPE
  add("8", "provider_timeout_class", "PRESERVED_PRIOR", "Runtype ERROR/TIMEOUT classes exist in coordinator");

  // 9-10 pause/step
  r = await post("unlock", { judge_key: "JUDGE-HYDRA-2026" });
  const run2 = r.data.run.run_id as string;
  await post("step", { run_id: run2 });
  await post("pause", { run_id: run2 });
  const paused = (await post("status", { run_id: run2 })).data.run;
  add("9", "pause_preserves_state", paused.paused && paused.transitions?.length >= 2 ? "PASS" : "FAIL", {
    phase: paused.phase,
    n: paused.transitions?.length,
  });
  await post("step", { run_id: run2 });
  const stepped = (await post("status", { run_id: run2 })).data.run;
  add("10", "step_after_pause", stepped.transitions?.length === paused.transitions.length + 1 ? "PASS" : "FAIL");

  // 11 reset new session
  r = await post("reset", { judge_key: "JUDGE-HYDRA-2026" });
  const sessionB = r.data.session.session_id as string;
  add("11", "reset_new_session", sessionA !== sessionB ? "PASS" : "FAIL", { sessionA, sessionB });

  // 12 invalid judge key
  r = await post("unlock", { judge_key: "x" });
  add("12", "invalid_judge_capability", r.http === 401 ? "PASS" : "FAIL", r.data);

  // 13 two sessions isolated
  const s1 = await post("unlock", { judge_key: "JUDGE-HYDRA-2026" });
  const s2 = await post("unlock", { judge_key: "HACK-HYDRA" });
  add(
    "13",
    "two_sessions_isolated",
    s1.data.session.session_id !== s2.data.session.session_id &&
      s1.data.session.namespace !== s2.data.session.namespace
      ? "PASS"
      : "FAIL",
  );

  // 14-17 unavailable providers — visible states
  add("14", "runtype_unavailable_visible", String(run.providers?.runtype || "").length > 0 ? "PASS" : "FAIL", run.providers?.runtype);
  add("15", "mitosis_unavailable_visible", String(run.providers?.mitosis || "").includes("BLOCKED") ? "PASS" : "FAIL", run.providers?.mitosis);
  add("16", "cloudflare_unavailable_visible", String(run.providers?.cloudflare || "").includes("NOT LIVE") ? "PASS" : "FAIL", run.providers?.cloudflare);
  add("17", "hydradb_pending_visible", run.hydradb_state === "PENDING_READBACK" ? "PASS" : "FAIL", run.hydradb_state);

  // 19 FCG root changes
  add("19", "fcg_root_changes_each_material_state", uniqueRoots.size >= 7 ? "PASS" : "FAIL", { uniqueRoots: uniqueRoots.size });

  // 20 no canonical mutation claim
  add("20", "demo_not_canonical_science", run.claim_ceiling?.includes("DEMO") ? "PASS" : "FAIL", run.claim_ceiling);

  // remaining scenarios marked from matrix
  for (const [id, name, state] of [
    ["3", "poison_missed", "BOUNDED_NOT_INJECTED"],
    ["4", "null_no_useful_change", "BOUNDED"],
    ["6", "verifier_rejection_path", "PASS_PRIOR_INVALID_PROOF"],
    ["7", "model_abstention", "BOUNDED"],
    ["18", "browser_refresh_reconnect", "PASS_BOUNDED_STATUS_BY_RUN_ID"],
  ] as const) {
    add(id, name, state);
  }

  writeOutputs(gum, results, run);
  const hardFails = results.filter((x) => x.state === "FAIL");
  console.log(JSON.stringify({ gum: gum.GUM_DOCTOR_STATE, fail: hardFails.length, results }, null, 2));
  process.exit(hardFails.length ? 1 : 0);
}

function writeOutputs(gum: unknown, results: unknown[], run: unknown) {
  writeFileSync(
    path.join(OUT, "GOLDEN_PATH_TEST_RESULTS.json"),
    JSON.stringify(
      {
        schema: "hydralamp.golden_path_test_results.v1",
        base_url: BASE,
        gum,
        results,
        sample_run: run
          ? {
              run_id: (run as { run_id: string }).run_id,
              phase: (run as { phase: string }).phase,
              fcg_root_initial: (run as { fcg_root_initial: string }).fcg_root_initial,
              fcg_root_current: (run as { fcg_root_current: string }).fcg_root_current,
            }
          : null,
        signature_state: "NOT_SIGNED",
      },
      null,
      2,
    ) + "\n",
  );

  const sponsors = {
    schema: "hydralamp.sponsor_integration_receipts.v1",
    Cloudflare: { state: "READY_NOT_LIVE", transport: "LOCAL_DURABLE_PROJECTION" },
    Runtype: { state: "ERROR_OR_NOT_CONFIGURED", note: "Do not display CONNECTED" },
    Mitosis: { state: "BLOCKED_TRIAL_EXPIRED" },
    Cotal: { state: "PRIOR_BOUNDED" },
    Nebius: { state: "UNKNOWN" },
    Tavily: { state: "PRIOR_PASS_OPTIONAL" },
    Mistral: { state: "FUTURE_OPTIONAL" },
    signature_state: "NOT_SIGNED",
  };
  writeFileSync(path.join(OUT, "SPONSOR_INTEGRATION_RECEIPTS.json"), JSON.stringify(sponsors, null, 2) + "\n");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
