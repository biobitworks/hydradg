export type ProjectSource = {
  name: string;
  url: string;
  status: "verified-doc" | "reference-only" | "unresolved-share";
  role: string;
};

export const projectSources: ProjectSource[] = [
  {
    name: "HydraDB upstream",
    url: "https://github.com/hydra-db/hydradb",
    status: "verified-doc",
    role: "graph database and Track 03 runtime",
  },
  {
    name: "Minimal Gibbs free energy in IFT",
    url: "https://arxiv.org/abs/1004.2868",
    status: "reference-only",
    role: "theory source for the claim-bounded information-state G* abstraction",
  },
  {
    name: "BioCustody",
    url: "https://github.com/biobitworks/biocustody",
    status: "verified-doc",
    role: "cross-device custody, agent/model/device lineage, and optional voice-interface precedent",
  },
  {
    name: "Protein Hinge",
    url: "https://github.com/biobitworks/protein-hinge",
    status: "reference-only",
    role: "recompute-or-reject, first-divergence, and mutation/record-repair test precedent",
  },
  {
    name: "Exa Search API",
    url: "https://exa.ai/docs/reference/search-api-guide",
    status: "verified-doc",
    role: "optional external retrieval and source discovery",
  },
  {
    name: "GMI Cloud API",
    url: "https://docs.gmicloud.ai/api-reference/introduction",
    status: "verified-doc",
    role: "optional compute provider; not required for MVP",
  },
  {
    name: "Daytona API",
    url: "https://www.daytona.io/docs/en/tools/api/#daytona",
    status: "verified-doc",
    role: "optional isolated sandbox execution",
  },
  {
    name: "Mitosis CLI",
    url: "https://mitosislabs.ai/developers/cli/overview",
    status: "verified-doc",
    role: "optional Cortex memory / office agents via mi CLI; not canonical FCG",
  },
  {
    name: "Modal",
    url: "https://modal.com/docs",
    status: "verified-doc",
    role: "optional remote compute/model endpoint",
  },
  {
    name: "Google AI Mode share 1",
    url: "https://share.google/aimode/dB1xIMC0Y9HReGket",
    status: "unresolved-share",
    role: "user-supplied external evidence pending retrieval",
  },
  {
    name: "Google AI Mode share 2",
    url: "https://share.google/aimode/rNGo3bA2XPIffZ6rN",
    status: "unresolved-share",
    role: "user-supplied external evidence pending retrieval",
  },
  {
    name: "Google AI Mode share 3",
    url: "https://share.google/aimode/g9NbUbcDzDreuYryc",
    status: "unresolved-share",
    role: "user-supplied external evidence pending retrieval",
  },
];
