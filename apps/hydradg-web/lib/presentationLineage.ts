export type PresentationState = {
  id: string;
  label: string;
  commit: string;
  date: string;
  state: "CURRENT" | "HISTORICAL";
  presentation_priority: "PRIMARY" | "HISTORICAL";
  github_url: string;
  deployment_url?: string;
  superseded_by?: string;
  reason: string;
  measured_context_metrics: "AVAILABLE_VIA_CURRENT_ICEBERG_API" | "NOT_MEASURED_UNDER_CURRENT_CONTRACT";
};

export const PRESENTATION_HISTORY: readonly PresentationState[] = [
  {
    id: "hydradg-web-mvp-20260818",
    label: "Original web MVP",
    commit: "e84afb8fafa3494d274edb0bfbfa9ab02b800a96",
    date: "2026-08-18",
    state: "HISTORICAL",
    presentation_priority: "HISTORICAL",
    github_url: "https://github.com/biobitworks/hydradg/tree/e84afb8fafa3494d274edb0bfbfa9ab02b800a96/apps/hydradg-web",
    deployment_url: "https://hydradg-jyybrnio5-biobitworks.vercel.app",
    superseded_by: "hydradg-judge-freeze-20260820",
    reason: "Architecture-first MVP retained as custody evidence; later judge surfaces reduced setup friction and made evidence/claim boundaries easier to reach.",
    measured_context_metrics: "NOT_MEASURED_UNDER_CURRENT_CONTRACT",
  },
  {
    id: "hydradg-judge-freeze-20260820",
    label: "Final judge freeze",
    commit: "35d1d6a530f8fb73b215d218f203b20ae4ebbdc0",
    date: "2026-08-20",
    state: "HISTORICAL",
    presentation_priority: "HISTORICAL",
    github_url: "https://github.com/biobitworks/hydradg/tree/35d1d6a530f8fb73b215d218f203b20ae4ebbdc0/apps/hydradg-web",
    superseded_by: "hydradg-vithia-extension-20260820",
    reason: "Exact green submission state remains frozen; subsequent work added Vithia/CFMO evidence and therefore required a successor presentation state rather than mutation of the frozen release record.",
    measured_context_metrics: "NOT_MEASURED_UNDER_CURRENT_CONTRACT",
  },
  {
    id: "hydradg-vithia-extension-20260820",
    label: "Vithia + Context Iceberg source state",
    commit: "abccbd3695f6f1a81d10bc352631beba009b3ce1",
    date: "2026-08-20",
    state: "HISTORICAL",
    presentation_priority: "HISTORICAL",
    github_url: "https://github.com/biobitworks/hydradg/tree/abccbd3695f6f1a81d10bc352631beba009b3ce1/apps/hydradg-web",
    superseded_by: "hydradg-curated-vercel-current",
    reason: "Scientific/custody scope expanded, but the homepage accumulated too many equally weighted sections. The curated successor keeps the interactive state field while moving deep detail behind dedicated routes.",
    measured_context_metrics: "NOT_MEASURED_UNDER_CURRENT_CONTRACT",
  },
  {
    id: "hydradg-curated-vercel-current",
    label: "Curated judge presentation",
    commit: process.env.VERCEL_GIT_COMMIT_SHA || process.env.GITHUB_SHA || "CURRENT_WORKTREE",
    date: "2026-08-20",
    state: "CURRENT",
    presentation_priority: "PRIMARY",
    github_url: "https://github.com/biobitworks/hydradg/tree/hack-hydra/curated-vercel-lineage-20260820/apps/hydradg-web",
    reason: "Reduce judge cognitive load, make the heat-map semantics visible, and expose presentation evolution without deleting prior UI states.",
    measured_context_metrics: "AVAILABLE_VIA_CURRENT_ICEBERG_API",
  },
] as const;

export const CURRENT_PRESENTATION = PRESENTATION_HISTORY[PRESENTATION_HISTORY.length - 1];

export const PRESENTATION_CLAIM_BOUNDARY =
  "Presentation supersession lowers default UI priority only. It does not invalidate historical evidence, establish scientific correctness, or prove that lower delta G-star means better accuracy.";
