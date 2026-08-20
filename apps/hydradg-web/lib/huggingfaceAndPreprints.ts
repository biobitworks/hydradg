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
    journal_or_arxiv: "Zenodo / Biobitworks",
    doi_or_url: "https://doi.org/10.5281/zenodo.21829929",
    version_note: "Current project-supplied publication link · Aug 2026",
    knowledge_fco_id: "fco:zenodo_21829929_fractal_custody_objects_v4_v5",
    summary: "Current project citation for the FCO/FCG publication-version package and Vithia companion evidence.",
  },
  {
    id: "zenodo-21830287",
    title: "Custody-Verified Classification of AI Model Outputs in a Self/Non-Self × Safe/Unsafe Matrix",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo / Biobitworks",
    doi_or_url: "https://doi.org/10.5281/zenodo.21830287",
    version_note: "Current project-supplied publication link · Aug 2026",
    knowledge_fco_id: "fco:zenodo_21830287_custody_verified_matrix",
    summary: "Current project citation for custody-governed Self/Non-Self × Safe/Unsafe classification work.",
  },
  {
    id: "zenodo-21830361",
    title: "The Shadow Dogma: hypothesis and governed computational evidence package for fragment-inheritance aging models",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo / Biobitworks",
    doi_or_url: "https://doi.org/10.5281/zenodo.21830361",
    version_note: "Current project-supplied publication link · Aug 2026",
    knowledge_fco_id: "fco:zenodo_21830361_shadow_dogma",
    summary: "Current project citation for the governed fragment-inheritance aging hypothesis/evidence package.",
  },
  {
    id: "zenodo-21830386",
    title: "XenoDisorder: bounded PTM-aware disorder scoring with exact modified-row evidence and a standalone local software surface",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo / Biobitworks",
    doi_or_url: "https://doi.org/10.5281/zenodo.21830386",
    version_note: "Current project-supplied publication link · Aug 2026",
    knowledge_fco_id: "fco:zenodo_21830386_xenodisorder",
    summary: "Current project citation for bounded PTM-aware disorder scoring and exact modified-row evidence.",
  },
  {
    id: "zenodo-21210575",
    title: "Fractal Custody Objects: route-comparable chain-of-custody for deterministic computational biology and AI-agent provenance",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo · v1 · published 2026-07-05",
    doi_or_url: "https://doi.org/10.5281/zenodo.21210575",
    version_note: "Externally verified Zenodo v1 record",
    knowledge_fco_id: "fco:zenodo_21210575_fco_v1",
    summary: "FCO v1 publication record. The publication FCG root is described as Ed25519-signed with a separately published public-key fingerprint; that signing scope does not automatically cover HydraDG project objects.",
  },
  {
    id: "zenodo-21420906",
    title: "Fractal Custody Objects: route-comparable chain-of-custody for deterministic computational biology and AI-agent provenance",
    authors: "Lee, Byron",
    journal_or_arxiv: "Zenodo · v3 · published 2026-07-17",
    doi_or_url: "https://doi.org/10.5281/zenodo.21420906",
    version_note: "Externally verified Zenodo v3 record",
    knowledge_fco_id: "fco:zenodo_21420906_fco_v3",
    summary: "FCO v3 publication record covering content-addressed custody, training-interior provenance, and custody-versus-trajectory complementarity under explicit claim ceilings.",
  },
  {
    id: "ensslin-weig-2010",
    title: "Inference with minimal Gibbs free energy in information field theory",
    authors: "Enßlin, T. A., & Weig, C.",
    journal_or_arxiv: "Phys. Rev. E 82, 051112 (2010)",
    doi_or_url: "https://doi.org/10.1103/PhysRevE.82.051112",
    knowledge_fco_id: "fco:3ed1f288ac8b3f48f4bf239f15a133fcdca36cd2ad8d3a9bb73a3f5a0be5349e",
    summary: "Design-lineage source for the nonphysical, application-defined HydraDG G* abstraction.",
  },
  {
    id: "lin-1991",
    title: "Divergence measures based on the Shannon entropy",
    authors: "Lin, J.",
    journal_or_arxiv: "IEEE Trans. Inf. Theory 37(1), 145–151 (1991)",
    doi_or_url: "https://doi.org/10.1109/18.61115",
    knowledge_fco_id: "fco:jensen_shannon_1991_lin_canonical_knowledge_atom",
    summary: "Source lineage for Jensen-Shannon divergence used in the separate Cloud Drift lane.",
  },
  {
    id: "shannon-1948",
    title: "A Mathematical Theory of Communication",
    authors: "Shannon, C. E.",
    journal_or_arxiv: "Bell System Technical Journal 27(3), 379–423 (1948)",
    doi_or_url: "https://doi.org/10.1002/j.1538-7305.1948.tb01338.x",
    knowledge_fco_id: "fco:shannon_1948_entropy_canonical_knowledge_atom",
    summary: "Information-theoretic entropy lineage used by HydraDG's declared diagnostic equations.",
  },
] as const;

export const HUGGINGFACE_MODELS: readonly HuggingFaceModelCard[] = [
  {
    id: "fco-vithia-fmo-076",
    model_name: "biobitworks/fco-vithia-fmo-076",
    hf_repo_url: "https://huggingface.co/biobitworks/fco-vithia-fmo-076",
    task: "Biobitworks FCO/FCG + Vithia research artifact",
    license: "CC-BY-NC-ND-4.0",
    knowledge_fco_id: "fco:huggingface_fco_vithia_fmo_076",
    description: "Gated Biobitworks model repository verified through the connected Hugging Face metadata surface; tagged for FCO/FCG, Vithia, LoRA, custody and provenance.",
  },
  {
    id: "qwen2.5-7b-instruct",
    model_name: "Qwen/Qwen2.5-7B-Instruct",
    hf_repo_url: "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct",
    task: "Upstream reference card for the local qwen2.5:7b diagnostic family",
    license: "Apache-2.0",
    knowledge_fco_id: "fco:huggingface_qwen2_5_7b_instruct_reference",
    description: "Official Qwen 7.61B instruction model card. A family/card link does not prove exact equivalence to an Ollama runtime tag; execution identity requires the local digest receipt.",
  },
  {
    id: "qwen2.5-coder-7b-instruct",
    model_name: "Qwen/Qwen2.5-Coder-7B-Instruct",
    hf_repo_url: "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct",
    task: "Upstream reference card for the local qwen2.5-coder:7b diagnostic family",
    license: "Apache-2.0",
    knowledge_fco_id: "fco:huggingface_qwen2_5_coder_7b_instruct_reference",
    description: "Official Qwen 7.61B coder-instruction model card. Runtime identity remains digest-bound rather than inferred from the model-family name.",
  },
  {
    id: "eleutherai-pythia-14m",
    model_name: "EleutherAI/pythia-14m",
    hf_repo_url: "https://huggingface.co/EleutherAI/pythia-14m",
    task: "Upstream architecture/reference card for the separate Pythia-14M/Vithia training lane",
    license: "Apache-2.0",
    knowledge_fco_id: "fco:huggingface_eleutherai_pythia_14m_reference",
    description: "Current 14.1M GPT-NeoX reference card. Hugging Face notes that on 2026-02-27 this URL was corrected to the standard-Pile model and the older deduplicated model moved to EleutherAI/pythia-14m-deduped.",
  },
] as const;

export const HACKATHON_AND_COMMUNITY_PROJECTS: readonly CommunityProject[] = [
  { name: "Glasswork", url: "https://glasswork.butterbase.dev/#demo", category: "Hackathon Demo", description: "Glasswork interactive demo surface." },
  { name: "BioBridge Pipeline", url: "https://biobridge-pipeline.kylon.app/final-demo", category: "Hackathon Demo", description: "BioBridge pipeline final demo." },
  { name: "VoiceWorks", url: "https://voiceworks-ygitm4zl.sauna.new", category: "Hackathon Demo", description: "VoiceWorks interactive web app." },
  { name: "BioCustody", url: "https://biocustody-n6iqdjsn.sauna.new", category: "Hackathon Demo", description: "BioCustody verification demo." },
  { name: "Cellico.Bio", url: "https://cellico.bio/", category: "My Project", description: "Bio x AI research project." },
  { name: "BioViz Tech", url: "https://bioviz.tech/", category: "My Project", description: "Bio-computational visualization and analytics." },
] as const;

export const AUTHOR_AUTHORITY = {
  name: "Byron Lee",
  orcid: "https://orcid.org/0000-0002-4925-4795",
  github: "https://github.com/biobitworks",
  huggingface: "https://huggingface.co/biobitworks",
  linkedin: "https://www.linkedin.com/in/biobitworks/",
  lesswrong: "https://www.lesswrong.com/users/byron-lee",
} as const;
