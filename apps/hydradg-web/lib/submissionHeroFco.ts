import { makeFcoNode } from "@/lib/fco";

export const SUBMISSION_HERO = {
  captureId: "hydralamp-submission-hero-20260827",
  imagePath: "/submission/HYDRALAMP_SUBMISSION_HERO.png",
  evalPath: "eval/immersive_commons_submission_20260827/assets/HYDRALAMP_SUBMISSION_HERO.png",
  sha256: "a5d558ab914b08da7373f858fbe79f60871315740e2abe06c39c31367c392b09",
  fcoId: "fco:c39e474cfb598c86ba66b288403850aec57e65573f31342bc9644487e4a40ddc",
  license: {
    researchContent: "CC-BY-NC-ND-4.0",
    software: "Apache-2.0",
    authority: "/LICENSING.md",
    superseded: "CC-BY-4.0 metadata is SUPERSEDED_METADATA_ERROR — historical custody only",
  },
  pointers: {
    hydradg: {
      branch: "hack-hydra/hydralamp-20260826",
      sha: "5b4bc20f0d20da96fe0e24090bafdeb3874280a4",
      url: "https://github.com/biobitworks/hydradg",
    },
    hydralamp: {
      branch: "prototype/deterministic-local-20260826",
      sha: "d3d928aae47e12afa99c25bd5d1cd94ef74c3da7",
      url: "https://github.com/biobitworks/hydralamp",
      demo: "https://hydralamp.vercel.app/",
    },
    immersiveCommonsIntegration: {
      branch: "main",
      sha: "8cc82a2",
      url: "https://github.com/biobitworks/immersivecommons-integration",
    },
  },
  submissionState: "AWAITING_HUMAN_APPROVAL",
} as const;

export type HeroRegion = {
  id: string;
  label: string;
  kind: "custody_anchor" | "judge_concept" | "sponsor" | "track";
  priority?: "P0" | "P1" | "P2";
  bbox: { x: number; y: number; w: number; h: number };
  detail: string;
};

export const HERO_REGIONS: HeroRegion[] = [
  { id: "hydralamp-core", label: "HydraLamp FCO Core", kind: "custody_anchor", bbox: { x: 380, y: 180, w: 240, h: 520 }, detail: "46-event golden lane · reference → poison → antidote → restoration" },
  { id: "ship-of-theseus", label: "Ship of Theseus", kind: "judge_concept", bbox: { x: 180, y: 120, w: 220, h: 280 }, detail: "Identity continuity under custody repair without erasing divergent history" },
  { id: "sponsor-runtype", label: "Runtype · P0", kind: "sponsor", priority: "P0", bbox: { x: 720, y: 60, w: 180, h: 90 }, detail: "Agent product voyage · flows + evals · preserved ERROR lane" },
  { id: "sponsor-tavily", label: "Tavily · P0", kind: "sponsor", priority: "P0", bbox: { x: 640, y: 160, w: 170, h: 85 }, detail: "External retrieval · golden-path source lane · PASS" },
  { id: "sponsor-cortex", label: "Cortex · P0", kind: "sponsor", priority: "P0", bbox: { x: 560, y: 260, w: 160, h: 80 }, detail: "Mitosis memory roundtrip · external only · not canonical FCG" },
  { id: "sponsor-cotal", label: "Cotal · P1", kind: "sponsor", priority: "P1", bbox: { x: 500, y: 360, w: 150, h: 75 }, detail: "Bounded A2A mesh transaction · BOUNDED_TX_PASS" },
  { id: "sponsor-aisa", label: "AIsa · P1", kind: "sponsor", priority: "P1", bbox: { x: 460, y: 460, w: 140, h: 70 }, detail: "qwen-flash proposal lane · composed golden path" },
  { id: "sponsor-ic", label: "Immersive Commons · P1", kind: "sponsor", priority: "P1", bbox: { x: 420, y: 560, w: 200, h: 80 }, detail: "Event host · MCP surface · submission AWAITING_HUMAN_APPROVAL" },
  { id: "sponsor-yappy", label: "Yappy.biz · P1", kind: "sponsor", priority: "P1", bbox: { x: 380, y: 660, w: 150, h: 70 }, detail: "Public product API · PASS · distinct from Mitosis Yappy" },
  { id: "sponsor-tenki", label: "Tenki · P2", kind: "sponsor", priority: "P2", bbox: { x: 340, y: 750, w: 130, h: 65 }, detail: "Sandbox microVM · deterministic exec receipt" },
  { id: "track-golden-path", label: "Composed Golden Path", kind: "track", bbox: { x: 600, y: 680, w: 320, h: 100 }, detail: "Tavily → AIsa → verify → quarantine · PARTIAL_P0_WITH_COMPOSED_FIXTURE" },
  { id: "track-ufa", label: "Ultimate Fighting Agents", kind: "track", bbox: { x: 680, y: 800, w: 260, h: 90 }, detail: "Submission-only track · perturbation receipts preserved" },
  { id: "track-judge-strip", label: "Judge Strip · 8 metrics", kind: "track", bbox: { x: 720, y: 880, w: 240, h: 80 }, detail: "PRIVATE_LEAK=0 · UNAUTHORIZED_WRITE=0 · RESTORATION_PASS · BROWSER_VERIFY_PASS" },
];

export function buildSubmissionHeroFcoProjection() {
  const hero = makeFcoNode("SubmissionHeroMediaFCO", {
    capture_id: SUBMISSION_HERO.captureId,
    image_sha256: SUBMISSION_HERO.sha256,
    public_path: SUBMISSION_HERO.imagePath,
    eval_path: SUBMISSION_HERO.evalPath,
    license_research_content: SUBMISSION_HERO.license.researchContent,
    license_software: SUBMISSION_HERO.license.software,
    evidence_class: "DETERMINISTIC_RAW_MEDIA_BYTES",
    claim_ceiling: "SUBMISSION_HERO_NAVIGATION_AND_CUSTODY_RECEIPT_ONLY",
    event_id: "anb-hack-01",
    repository_pointers: SUBMISSION_HERO.pointers,
    submission_write_state: SUBMISSION_HERO.submissionState,
    annotation_region_count: HERO_REGIONS.length,
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_COMMITTED",
    fcg_append_state: "NOT_APPENDED",
  });

  const index = makeFcoNode("SubmissionHeroIndex", {
    hero_fco_id: hero.id,
    sponsor_region_ids: HERO_REGIONS.filter((r) => r.kind === "sponsor").map((r) => r.id),
    track_region_ids: HERO_REGIONS.filter((r) => r.kind === "track").map((r) => r.id),
    judge_path_steps: 8,
    knowledge_href: "/submission",
    graph_href: `/fco/${encodeURIComponent(hero.id)}`,
    license_authority: "LICENSING.md",
  });

  return { hero, index, regions: HERO_REGIONS };
}
