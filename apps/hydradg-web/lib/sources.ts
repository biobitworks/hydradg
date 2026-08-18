export type ProjectSource = {
  name: string;
  url: string;
  status: "verified-doc" | "unresolved-share";
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
    name: "Exa Search API",
    url: "https://exa.ai/docs/reference/search-api-guide",
    status: "verified-doc",
    role: "external retrieval and source discovery",
  },
  {
    name: "GMI Cloud API",
    url: "https://docs.gmicloud.ai/api-reference/introduction",
    status: "verified-doc",
    role: "optional compute/container provider",
  },
  {
    name: "Daytona API",
    url: "https://www.daytona.io/docs/en/tools/api/#daytona",
    status: "verified-doc",
    role: "isolated sandbox execution",
  },
  {
    name: "Modal",
    url: "https://modal.com/docs",
    status: "verified-doc",
    role: "bounded remote compute and model endpoints",
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
