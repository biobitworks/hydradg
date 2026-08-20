export type PreprintedPaper = {
  id: string;
  title: string;
  authors: string;
  journal_or_arxiv: string;
  doi_or_url: string;
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

export const PREPRINTS: readonly PreprintedPaper[] = [
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
  {
    id: "friston-2010",
    title: "The free-energy principle: a unified brain theory?",
    authors: "Friston, K.",
    journal_or_arxiv: "Nat. Rev. Neurosci. 11, 127–138 (2010)",
    doi_or_url: "https://doi.org/10.1038/nrn2787",
    knowledge_fco_id: "fco:friston_2010_free_energy_principle_atom",
    summary: "Cognitive state field theory and free-energy minimisation under context perturbations.",
  },
] as const;

export const HUGGINGFACE_MODELS: readonly HuggingFaceModelCard[] = [
  {
    id: "hydradg-vithia-cfmo-v1",
    model_name: "HydraDG VITHIA CFMO Baseline v0.1",
    hf_repo_url: "https://huggingface.co/biobitworks/hydradg-vithia-cfmo-v0.1",
    task: "Context Field Memory Optimization / FCG Traversal",
    license: "CC-BY-NC-ND-4.0",
    knowledge_fco_id: "fco:f9d8af4c6aca40241dddb6b2a459ce0eaceb4663f6ac50d23e336f140172b707",
    description: "Pinned model identity record for the Track 03 LongMemEval FCG graph traversal experiment.",
  },
  {
    id: "hydradg-anticube-classifier-v1",
    model_name: "Anticube Safety & Contradiction Classifier",
    hf_repo_url: "https://huggingface.co/biobitworks/hydradg-anticube-classifier",
    task: "Context Perturbation & Contradiction Classification",
    license: "CC-BY-NC-ND-4.0",
    knowledge_fco_id: "fco:atom_classification_anticube_receipt_v1",
    description: "Anticube classifier model assigning SAFE/ADMIT vs NONSAFE/QUARANTINE labels to graph edges.",
  },
] as const;
