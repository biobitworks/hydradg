import Link from "next/link";

const LANES = [
  {
    label: "Primary Track 03 K=5",
    model: "NONE",
    runtime: "heuristic extractor · model=null · ollarma_url=null",
    evidence: "DETERMINISTIC / EXECUTED",
    body: "The published full500 retrieval ablation does not depend on a language model. This is the primary submitted empirical result.",
  },
  {
    label: "Local diagnostic M1",
    model: "qwen2.5-coder:7b",
    runtime: "Ollama/Ollarma loopback",
    evidence: "PROBABILISTIC_MODEL_OUTPUT_ONLY",
    body: "Approved local reference for bounded mechanism diagnosis and prospective prediction after deterministic science output is frozen.",
  },
  {
    label: "Local diagnostic M2",
    model: "qwen2.5:7b",
    runtime: "Ollama/Ollarma loopback",
    evidence: "PROBABILISTIC_MODEL_OUTPUT_ONLY",
    body: "Independent local reference using the same frozen packet and prompt. It does not mutate HydraDB or promote scientific claims.",
  },
  {
    label: "Vithia companion lane",
    model: "Pythia-14M / Vithia artifacts",
    runtime: "separate training experiment",
    evidence: "SUPPLEMENTARY_TRAINING_EVIDENCE",
    body: "A small-model reproducibility/provenance lane. It is not the model driving Track 03 retrieval and is not a capability-superiority claim.",
  },
] as const;

const CARDS = [
  { name: "Biobitworks · fco-vithia-fmo-076", href: "https://huggingface.co/biobitworks/fco-vithia-fmo-076", note: "Gated Biobitworks research artifact; FCO/FCG + Vithia custody/provenance model card." },
  { name: "Qwen · Qwen2.5-7B-Instruct", href: "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct", note: "Upstream 7.61B instruction model card · Apache-2.0. Reference card for the local Qwen family; exact Ollama weight identity still requires a runtime digest receipt." },
  { name: "Qwen · Qwen2.5-Coder-7B-Instruct", href: "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct", note: "Upstream 7.61B code-instruction model card · Apache-2.0. Reference card for the local coder family; exact Ollama weight identity still requires a runtime digest receipt." },
  { name: "EleutherAI · pythia-14m", href: "https://huggingface.co/EleutherAI/pythia-14m", note: "Current 14.1M GPT-NeoX model card · Apache-2.0. The card notes a Feb. 27, 2026 correction: this URL now identifies the standard-Pile model; the older deduplicated model moved to a separate repository." },
] as const;

export default function ModelsPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow goldText">Golden path · Models used</p>
          <h1>Know when a model is in the loop.</h1>
          <p className="lede">HydraDG separates deterministic graph evidence from probabilistic model interpretation. The submitted Track 03 K=5 result used no LLM. Local open-weight models are an optional diagnostic lane after experiment freeze.</p>
          <div className="actions"><Link className="primary goldenCta" href="/track03">Read executed result</Link><Link className="secondary" href="/custody">Verify custody boundary</Link></div>
        </div>
      </header>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">01 / MODEL INVOLVEMENT</span>
        <h2 className="displayTitle">Deterministic core first. Model interpretation second.</h2>
        <div className="grid twoCol">
          {LANES.map((lane) => <article className="panel" key={lane.label}><p className="eyebrow">{lane.label}</p><h2>{lane.model}</h2><p className="mono small">{lane.runtime}</p><p>{lane.body}</p><p className="small muted"><strong>Evidence class:</strong> {lane.evidence}</p></article>)}
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">02 / LOCAL JUDGE SERVER</span>
        <h2 className="displayTitle">The core demo survives if the local model is offline.</h2>
        <div className="statusGrid">
          <article className="statusCard gold"><p className="eyebrow">HydraDB + deterministic engine</p><strong>Required for graph operations</strong><p className="muted">Executed evidence, receipts and the read-only judge walkthrough remain inspectable without an LLM.</p></article>
          <article className="statusCard"><p className="eyebrow">Local analyst</p><strong>Optional · Qwen 2.5 7B family</strong><p className="muted">The browser calls a server-side route; Ollama/Ollarma remains loopback-only. Model output is probabilistic and cannot mutate canonical custody.</p></article>
          <article className="statusCard"><p className="eyebrow">External frontier API</p><strong>Not required</strong><p className="muted">No frontier-cloud API is required to reproduce the submitted K=5 result.</p></article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">03 / CONTROLLED FRONTIER COMPARISON</span>
        <h2 className="displayTitle">Not run. No superiority claim.</h2>
        <div className="panel goldenPanel"><p className="sectionLead">HydraDG has not established a controlled local-vs-frontier comparison under the same frozen dataset, retrieved evidence, prompt, context budget, provider snapshot, sampling configuration and scoring protocol. Any synthetic matrix rows or development-assistant usage are not model-execution evidence.</p><p className="mono small">FUTURE_FRONTIER_COMPARISON_NOT_RUN</p></div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">04 / HUGGING FACE MODEL CARDS</span>
        <h2 className="displayTitle">Link the model identity; do not assume the runtime digest.</h2>
        <div className="grid twoCol">{CARDS.map((card) => <article className="panel" key={card.href}><h3><a className="goldLink" href={card.href}>{card.name}</a></h3><p className="muted">{card.note}</p></article>)}</div>
        <p className="small muted note">A model-card URL is bibliographic/runtime-family context. Exact execution identity requires the actual local tag/digest, configuration, prompt and response receipt for the run being claimed.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">05 / NEXT</span>
        <div className="actions"><Link className="primary goldenCta" href="/custody">Verify custody</Link><Link className="secondary" href="/evidence">Open evidence ledger</Link><Link className="secondary" href="/judge">Return to judge walkthrough</Link></div>
      </section>
    </main>
  );
}
