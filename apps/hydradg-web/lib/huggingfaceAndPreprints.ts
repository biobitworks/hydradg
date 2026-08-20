export type PreprintedPaper = {
  id: string;
  title: string;
  authors: string;
  journal_or_arxiv: string;
  doi_or_url: string;
  version_note?: string;
  knowledge_fco_id: string;
  summary: string;
};

export type HuggingFaceModelCard = {
  id: string;
  model_name: string;
  hf_repo_url: string;
  task: string;
  license: string;
  knowledge_fco_id: string;
  description: string;
};

export type CommunityProject = {
  name: string;
  url: string;
  category: "Community" | "Hackathon Demo" | "Active Event" | "My Project" | "Previous Work";
  description: string;
};

export const PREPRINTS: readonly PreprintedPaper[] = [
  {
    id: "zenodo-21829929",
    title: "Fractal Custody Objects — v4/v5 publication-version package with Vithia companion evidence",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo / BioBitWorks (Aug 2026)",
    doi_or_url: "https://doi.org/10.5281/zenodo.21829929",
    version_note: "Publication Version v4/v5 Package",
    knowledge_fco_id: "fco:zenodo_21829929_fractal_custody_objects_v4_v5",
    summary: "Publication-version package establishing Fractal Custody Objects, FCG roots, and Vithia companion execution evidence.",
  },
  {
    id: "zenodo-21830287",
    title: "Custody-Verified Classification of AI Model Outputs in a Self/Non-Self × Safe/Unsafe Matrix",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo / BioBitWorks (Aug 2026)",
    doi_or_url: "https://doi.org/10.5281/zenodo.21830287",
    version_note: "August 2026 Release Version",
    knowledge_fco_id: "fco:zenodo_21830287_custody_verified_anticube_matrix",
    summary: "Grounding for Anticube classification matrix mapping model outputs across Self/Non-Self and Safe/Unsafe categories.",
  },
  {
    id: "zenodo-21830361",
    title: "The Shadow Dogma: hypothesis and governed computational evidence package for fragment-inheritance aging models",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo / BioBitWorks (Aug 2026)",
    doi_or_url: "https://doi.org/10.5281/zenodo.21830361",
    version_note: "August 2026 Evidence Release",
    knowledge_fco_id: "fco:zenodo_21830361_shadow_dogma_aging_evidence",
    summary: "Governed computational evidence package for fragment-inheritance aging models.",
  },
  {
    id: "zenodo-21830386",
    title: "XenoDisorder: bounded PTM-aware disorder scoring with exact modified-row evidence and a standalone local software surface",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo / BioBitWorks (Aug 2026)",
    doi_or_url: "https://doi.org/10.5281/zenodo.21830386",
    version_note: "August 2026 Package Release",
    knowledge_fco_id: "fco:zenodo_21830386_xenodisorder_ptm_scoring",
    summary: "PTM-aware protein disorder scoring surface with exact modified-row evidence tracking.",
  },
  {
    id: "zenodo-21210575",
    title: "Governed Data Pipeline & FCG Provenance Protocol v1",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo (2026)",
    doi_or_url: "https://doi.org/10.5281/zenodo.21210575",
    version_note: "Protocol Specification v1",
    knowledge_fco_id: "fco:zenodo_21210575_governed_pipeline_protocol",
    summary: "Data pipeline governance and cryptographic hash verification rules.",
  },
  {
    id: "zenodo-21421298",
    title: "HydraDB Graph Memory & Context Iceberg Architecture",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo (2026)",
    doi_or_url: "https://doi.org/10.5281/zenodo.21421298",
    version_note: "Architecture Release",
    knowledge_fco_id: "fco:zenodo_21421298_hydradb_context_iceberg",
    summary: "Graph memory model and Context Iceberg visualization layers.",
  },
  {
    id: "zenodo-21421000",
    title: "Vithia Companion Evidence & Model Verification Protocol",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo (2026)",
    doi_or_url: "https://doi.org/10.5281/zenodo.21421000",
    version_note: "Companion Verification Protocol",
    knowledge_fco_id: "fco:zenodo_21421000_vithia_model_verification",
    summary: "Model verification protocol and turn log execution receipts.",
  },
  {
    id: "zenodo-21382831",
    title: "BioBridge Pipeline & Custody Verification Foundations",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo (2026)",
    doi_or_url: "https://doi.org/10.5281/zenodo.21382831",
    version_note: "BioBridge Baseline Version",
    knowledge_fco_id: "fco:zenodo_21382831_biobridge_foundations",
    summary: "Foundational verification methods for bio-computational execution chains.",
  },
  {
    id: "zenodo-18109862",
    title: "Self/Non-Self Context Perturbation Dynamics in Graph Memory",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo (2025)",
    doi_or_url: "https://doi.org/10.5281/zenodo.18109862",
    version_note: "Early Dynamics Release",
    knowledge_fco_id: "fco:zenodo_18109862_context_perturbation_dynamics",
    summary: "Initial formulation of self/non-self context dynamics under memory perturbations.",
  },
  {
    id: "zenodo-17992450",
    title: "Fractal Knowledge Representation in Bio-AI Systems",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo (2025)",
    doi_or_url: "https://doi.org/10.5281/zenodo.17992450",
    version_note: "Initial Concept Preprint",
    knowledge_fco_id: "fco:zenodo_17992450_fractal_knowledge_representation",
    summary: "Foundational preprint establishing fractal structures for content-addressed knowledge trees.",
  },
  {
    id: "ensslin-weig-2010",
    title: "Inference with minimal Gibbs free energy in information field theory",
    authors: "Enßlin, T. A., & Weig, C.",
    journal_or_arxiv: "Phys. Rev. E 82, 051112 (2010)",
    doi_or_url: "https://doi.org/10.1103/PhysRevE.82.051112",
    knowledge_fco_id: "fco:3ed1f288ac8b3f48f4bf239f15a133fcdca36cd2ad8d3a9bb73a3f5a0be5349e",
    summary: "Grounds HydraDG's dimensionless G* diagnostic as an application-defined free-energy surrogate.",
  },
  {
    id: "lin-1991",
    title: "Divergence measures based on the Shannon entropy",
    authors: "Lin, J.",
    journal_or_arxiv: "IEEE Trans. Inf. Theory 37(1), 145–151 (1991)",
    doi_or_url: "https://doi.org/10.1109/18.61115",
    knowledge_fco_id: "fco:jensen_shannon_1991_lin_canonical_knowledge_atom",
    summary: "Grounds Jensen-Shannon Cloud Drift (0–100) as a symmetric, bounded divergence measure derived from Shannon entropy.",
  },
  {
    id: "shannon-1948",
    title: "A Mathematical Theory of Communication",
    authors: "Shannon, C. E.",
    journal_or_arxiv: "Bell System Technical Journal, 27(3), 379–423 (1948)",
    doi_or_url: "https://doi.org/10.1002/j.1538-7305.1948.tb01338.x",
    knowledge_fco_id: "fco:shannon_1948_entropy_canonical_knowledge_atom",
    summary: "Establishes information-theoretic entropy H = -sum(p log2 p) in bits.",
  },
] as const;

export const HUGGINGFACE_MODELS: readonly HuggingFaceModelCard[] = [
  {
    id: "fco-vithia-fmo-076",
    model_name: "fco-vithia-fmo-076",
    hf_repo_url: "https://huggingface.co/biobitworks/fco-vithia-fmo-076",
    task: "Fractal Custody & Vithia Field Memory Optimization",
    license: "CC-BY-NC-ND-4.0",
    knowledge_fco_id: "fco:huggingface_fco_vithia_fmo_076_canonical_model",
    description: "Official publication model weights and companion FCG execution weights for HydraDG.",
  },
  {
    id: "hydradg-vithia-cfmo-v1",
    model_name: "HydraDG VITHIA CFMO Baseline v0.1",
    hf_repo_url: "https://huggingface.co/biobitworks/hydradg-vithia-cfmo-v0.1",
    task: "Context Field Memory Optimization / FCG Traversal",
    license: "CC-BY-NC-ND-4.0",
    knowledge_fco_id: "fco:f9d8af4c6aca40241dddb6b2a459ce0eaceb4663f6ac50d23e336f140172b707",
    description: "Pinned model identity record for Track 03 LongMemEval FCG graph traversal experiment.",
  },
  {
    id: "hydradg-anticube-classifier",
    model_name: "Anticube Safety & Contradiction Classifier",
    hf_repo_url: "https://huggingface.co/biobitworks/hydradg-anticube-classifier",
    task: "Context Perturbation & Contradiction Classification",
    license: "CC-BY-NC-ND-4.0",
    knowledge_fco_id: "fco:atom_classification_anticube_receipt_v1",
    description: "Anticube classifier model assigning SAFE/ADMIT vs NONSAFE/QUARANTINE labels to graph edges.",
  },
] as const;

export const HACKATHON_AND_COMMUNITY_PROJECTS: readonly CommunityProject[] = [
  { name: "Glasswork", url: "https://glasswork.butterbase.dev/#demo", category: "Hackathon Demo", description: "Glasswork interactive demo surface." },
  { name: "BioBridge Pipeline", url: "https://biobridge-pipeline.kylon.app/final-demo", category: "Hackathon Demo", description: "BioBridge pipeline final demo." },
  { name: "VoiceWorks", url: "https://voiceworks-ygitm4zl.sauna.new", category: "Hackathon Demo", description: "VoiceWorks interactive web app." },
  { name: "BioCustody", url: "https://biocustody-n6iqdjsn.sauna.new", category: "Hackathon Demo", description: "BioCustody verification demo." },
  { name: "FoldSense AI Studio", url: "https://foldsense.ai.studio/", category: "Hackathon Demo", description: "FoldSense protein structural AI environment." },
  { name: "Cellico.Bio", url: "https://cellico.bio/", category: "My Project", description: "Building Bio x AI and Bay Area community lab infrastructure." },
  { name: "Infinite Velocity", url: "https://infinitevelocity.bioviz.tech/", category: "My Project", description: "BioViz visualization platform." },
  { name: "BioViz Tech", url: "https://bioviz.tech/", category: "My Project", description: "Bio-computational rendering and analytics." },
  { name: "BioViz Luma", url: "https://luma.com/bioviz", category: "Active Event", description: "BioViz events on Luma." },
  { name: "Biopunk S26 Showcase", url: "https://luma.com/biopunk-s26-showcase", category: "Active Event", description: "Biopunk Summer 2026 Showcase." },
  { name: "Biopunk Fireside Chat", url: "https://luma.com/biopunk-fireside-chat", category: "Active Event", description: "Biopunk Fireside Chat event." },
  { name: "Edison Scientific", url: "https://edisonscientific.com/", category: "Previous Work", description: "Scientific platform development." },
  { name: "Walter Lab (UCSF)", url: "https://walterlab.ucsf.edu/", category: "Previous Work", description: "UCSF Walter Lab research." },
] as const;

export const AUTHOR_AUTHORITY = {
  name: "Byron Lee",
  role: "Founder, Cellico.Bio | Bio x AI & Bay Area Community Infrastructure",
  orcid: "https://orcid.org/0000-0002-4925-4795",
  github: "https://github.com/biobitworks",
  huggingface: "https://huggingface.co/biobitworks",
  linkedin: "https://www.linkedin.com/in/biobitworks/",
  substack: "https://biobitworks.substack.com/",
  lesswrong: "https://www.lesswrong.com/users/byron-lee",
} as const;
