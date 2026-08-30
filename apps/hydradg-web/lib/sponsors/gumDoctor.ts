/**
 * GUM Doctor discovery — secret injection authority only when interface is established.
 * Never prints secret values.
 */
import { createHash } from "node:crypto";
import { writeFileSync, readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import os from "node:os";

const TRUSTED_SEARCH_PATHS = [
  "/Users/byron/projects/bin",
  "/Users/byron/projects/active/ollarma/bin",
  "/opt/homebrew/bin",
  "/usr/local/bin",
];

export type GumDoctorDiscovery = {
  schema: "sponsor.gum_doctor_discovery_receipt.v1";
  recorded_at_utc: string;
  host: string;
  GUM_DOCTOR_STATE: "DEPENDENCY_UNRESOLVED" | "CONFIGURED";
  SPONSOR_SECRET_INJECTION: "BLOCKED" | "GUM_DOCTOR";
  GUM_DOCTOR_PATH: string | null;
  GUM_DOCTOR_VERSION: string | null;
  GUM_DOCTOR_INTERFACE_SHA256: string | null;
  discovery: {
    command_v_gum_doctor: boolean;
    command_v_gum_doctor_alt: boolean;
    command_v_gum: boolean;
    command_v_ollarma: boolean;
    command_v_ollama: boolean;
    trusted_path_scan: string[];
  };
  note: string;
  signature_state: "NOT_SIGNED";
};

function commandExists(name: string): boolean {
  const r = spawnSync("command", ["-v", name], { encoding: "utf8", shell: true });
  return r.status === 0;
}

function scanTrustedPaths(exeNames: string[]): string | null {
  for (const dir of TRUSTED_SEARCH_PATHS) {
    for (const exe of exeNames) {
      const p = path.join(dir, exe);
      if (existsSync(p)) return p;
    }
  }
  return null;
}

function sha256Text(text: string): string {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

export function discoverGumDoctor(repoRoot: string): GumDoctorDiscovery {
  const gumDoctorPath =
    scanTrustedPaths(["gum-doctor", "gum_doctor"]) ||
    (commandExists("gum-doctor") ? "gum-doctor" : null) ||
    (commandExists("gum_doctor") ? "gum_doctor" : null);

  let version: string | null = null;
  let interfaceSha: string | null = null;

  if (gumDoctorPath) {
    const ver = spawnSync(gumDoctorPath, ["--version"], { encoding: "utf8" });
    if (ver.status === 0) version = ver.stdout.trim().slice(0, 120);
    const help = spawnSync(gumDoctorPath, ["--help"], { encoding: "utf8" });
    if (help.status === 0 && help.stdout) {
      interfaceSha = sha256Text(help.stdout);
    }
  }

  const configured = Boolean(gumDoctorPath && version && interfaceSha);
  const receipt: GumDoctorDiscovery = {
    schema: "sponsor.gum_doctor_discovery_receipt.v1",
    recorded_at_utc: new Date().toISOString(),
    host: os.hostname(),
    GUM_DOCTOR_STATE: configured ? "CONFIGURED" : "DEPENDENCY_UNRESOLVED",
    SPONSOR_SECRET_INJECTION: configured ? "GUM_DOCTOR" : "BLOCKED",
    GUM_DOCTOR_PATH: gumDoctorPath,
    GUM_DOCTOR_VERSION: version,
    GUM_DOCTOR_INTERFACE_SHA256: interfaceSha,
    discovery: {
      command_v_gum_doctor: commandExists("gum-doctor"),
      command_v_gum_doctor_alt: commandExists("gum_doctor"),
      command_v_gum: commandExists("gum"),
      command_v_ollarma: commandExists("ollarma"),
      command_v_ollama: commandExists("ollama"),
      trusted_path_scan: TRUSTED_SEARCH_PATHS,
    },
    note: configured
      ? "GUM Doctor found with help interface hash recorded."
      : "GUM Doctor executable or secret-injection interface not established on host.",
    signature_state: "NOT_SIGNED",
  };

  const outPath = path.join(
    repoRoot,
    "eval",
    "agent_native_sponsors_20260827",
    "GUM_DOCTOR_DISCOVERY_RECEIPT.json",
  );
  writeFileSync(outPath, JSON.stringify(receipt, null, 2) + "\n");
  return receipt;
}

export function loadGumDoctorReceipt(repoRoot: string): GumDoctorDiscovery | null {
  const p = path.join(repoRoot, "eval", "agent_native_sponsors_20260827", "GUM_DOCTOR_DISCOVERY_RECEIPT.json");
  if (!existsSync(p)) return null;
  return JSON.parse(readFileSync(p, "utf8")) as GumDoctorDiscovery;
}
