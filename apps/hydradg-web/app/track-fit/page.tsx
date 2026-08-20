import Link from "next/link";

import KnowledgeTermLink from "@/components/KnowledgeTermLink";
import { buildReleaseManifest } from "@/lib/releaseMeta";

const TRACK03 = {
  cases: 500,
  sessions: 23867,
  facts: 3506,
  entities: 4776,
  scored: 470,
  abstentions: 30,
  hitA: 0.9638297872,
  hitB: 0.9468085106,
  hitC: 0.9468085106,
  hitD: 0.94468085,
};

const CONTEXT_ENTROPY = { raw: 18567, classified: 18555, abstentions: 12 };
const HOSTED = { fcos: 36, edges: 24, fcoDelta: 0, edgeDelta: 0, hashDelta: 0 };

function pct(numerator: number, denominator: number) {
  return (100 * numerator) / denominator;
}

function pp(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(4)} pp`;
}

export default function TrackFitPage() {
  const release = buildReleaseManifest();
  const canonicalFcoCount = release.fco_identity_validation.unique_fco_count;
  const coverage = pct(CONTEXT_ENTROPY.classified, CONTEXT_ENTROPY.raw);
  const abstentionRate = pct(CONTEXT_ENTROPY.abstentions, CONTEXT_ENTROPY.raw);
  const bDelta = 100 * (TRACK03.hitB - TRACK03.hitA);
  const cDelta = 100 * (TRACK03.hitC - TRACK03.hitA);
  const dDelta = 100 * (TRACK03.hitD - TRACK03.hitA);

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Final judge step · Why graph?</p>
          <h1>HydraDG fits the graph problem at the point where similarity alone stops being enough.</h1>
          <p className="lede">
            The primary submission lane is <KnowledgeTermLink slug="hydramemory">Track 03 / HydraMemory</KnowledgeTermLink> because it has the completed full500 experiment. Tracks 01 and 02 show how the same <KnowledgeTermLink slug="fcg">FCG</KnowledgeTermLink> custody/traversal primitive transfers to ontology and dependency reasoning without promoting unfinished benchmark lanes.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Replay judge walkthrough</Link>
            <Link className="secondary" href="/knowledge">Terminology matrix</Link>
            <Link className="secondary" href="/how-to">How to use</Link>
            <Link className="secondary" href="/evidence">Evidence ledger</Link>
          </div>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">PRIMARY FIT · TRACK 03</span>
          <span className="pill pillMuted">TRACK 01/02 · BOUNDED TRANSFER LANES</span>
        </div>
      </header>

      <section className="computeSection">
        <span className="sectionNumber">01 / WHAT HYDRA IS LOOKING FOR</span>
        <h2 className="displayTitle">Four judging signals, each tied to something inspectable.</h2>
        <div className="grid twoCol">
          <article className="panel" style={{ borderTop: "3px solid #b69cff" }}>
            <p className="eyebrow">1 · Graph data model</p>
            <h2><KnowledgeTermLink slug="fcg">Typed state is in the relationships.</KnowledgeTermLink></h2>
            <p>Source, Evidence, KnowledgeAtom, SeedOfTruth, StateSnapshot, current state, contradiction, supersession and custody are different object/relation roles rather than one flattened text record.</p>
          </article>
          <article className="panel" style={{ borderTop: "3px solid #5aa9ff" }}>
            <p className="eyebrow">2 · Novel retrieval / reasoning</p>
            <h2><KnowledgeTermLink slug="hydramemory">Retrieve paths and state, not only nearest chunks.</KnowledgeTermLink></h2>
            <p>Temporal, entity/provenance, contradiction and supersession treatments are explicit retrieval lanes. The completed experiment preserved the result even when they did not beat the flat reference route.</p>
          </article>
          <article className="panel" style={{ borderTop: "3px solid #ff8a3d" }}>
            <p className="eyebrow">3 · Relationships / traversal / context</p>
            <h2><KnowledgeTermLink slug="superseded-by">History stays traversable after change.</KnowledgeTermLink></h2>
            <p>A judge can move Reference → Poison → Antidote while following <KnowledgeTermLink slug="contradicts">CONTRADICTS</KnowledgeTermLink>, <KnowledgeTermLink slug="superseded-by">SUPERSEDED_BY</KnowledgeTermLink>, provenance and state-transition edges.</p>
          </article>
          <article className="panel" style={{ borderTop: "3px solid #f6c85f" }}>
            <p className="eyebrow">4 · Hard to flatten</p>
            <h2>“What is true now, why, and what changed?” is a path question.</h2>
            <p>A vector index can retrieve similar passages and a relational table can store rows, but HydraDG's load-bearing question requires chronology + provenance + contradiction + supersession + exact custody identity to be traversed together.</p>
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / TRACK FIT</span>
        <h2 className="displayTitle">One graph primitive, three bounded applications.</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Track</th><th align="left">Graph-native question</th><th align="left">Why relationships matter</th><th align="left">Evidence state</th><th align="left">Open</th></tr></thead>
            <tbody>
              <tr><td><strong>01 · Enterprise Context + Ontology</strong></td><td>Which identity/current claim should an enterprise agent use?</td><td>Alias resolution, ABOUT, provenance, conflicting and superseded claims.</td><td>Model + downloaded/hashed sources; real benchmark ingestion/evaluation remains bounded.</td><td><Link href="/track01">Track 01</Link></td></tr>
              <tr><td><strong>02 · Repos + Dependencies</strong></td><td>Which services are exposed through which dependency paths at time T?</td><td>Reverse dependency closure, exact path explanation, partial vs complete repair.</td><td>Synthetic structural canary/design lane; no production vulnerability claim.</td><td><Link href="/track02">Track 02</Link></td></tr>
              <tr><td><strong>03 · Memory + Context Retrieval</strong></td><td>What is current after a long history of changing and conflicting facts?</td><td>NEXT/PREV, ASSERTS, DERIVED_FROM, ABOUT, SUPERSEDED_BY, CONTRADICTS.</td><td><strong>Executed full500 retrieval ablation; primary submission lane.</strong></td><td><Link href="/track03">Track 03</Link></td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / SHOW THE REAL MATH</span>
        <h2 className="displayTitle">Measured project quantities are recomputed from integer counts or frozen outputs.</h2>
        <div className="grid twoCol">
          <article className="panel" style={{ background: "rgba(127,209,185,0.07)" }}>
            <p className="eyebrow">Hosted migration · measured</p>
            <h2>{HOSTED.fcos} FCOs · {HOSTED.edges} edges · zero canonical delta</h2>
            <pre className="result">{`FCO_SET_DELTA = ${HOSTED.fcoDelta}\nEDGE_SET_DELTA = ${HOSTED.edgeDelta}\nCONTENT_HASH_DELTA = ${HOSTED.hashDelta}\nCANONICAL_PARITY = PASS`}</pre>
            <p className="small muted">Interpretation: canonical custody identity was preserved across the recorded projection/readback scope. This is not a claim that deployment context did not change.</p>
            <Link className="secondary" href="/evolution">Open migration state</Link>
          </article>

          <article className="panel" style={{ background: "rgba(246,200,95,0.07)" }}>
            <p className="eyebrow">Context vs Entropy · measured</p>
            <h2>{coverage.toFixed(4)}% context-classified</h2>
            <pre className="result">{`coverage = 100 × ${CONTEXT_ENTROPY.classified} / ${CONTEXT_ENTROPY.raw}\n         = ${coverage.toFixed(6)}%\n\nabstention_rate = 100 × ${CONTEXT_ENTROPY.abstentions} / ${CONTEXT_ENTROPY.raw}\n                = ${abstentionRate.toFixed(6)}%\n\n18428 + 126 + 1 + 12 = 18567  // PASS`}</pre>
            <Link className="secondary" href="/results/context-vs-entropy">Open experiment</Link>
          </article>

          <article className="panel" style={{ background: "rgba(90,169,255,0.07)" }}>
            <p className="eyebrow">Track 03 full500 · measured</p>
            <h2>Graph treatments did not establish a Hit@5 advantage.</h2>
            <pre className="result">{`B − A = ${TRACK03.hitB.toFixed(10)} − ${TRACK03.hitA.toFixed(10)} = ${pp(bDelta)}\nC − A = ${TRACK03.hitC.toFixed(10)} − ${TRACK03.hitA.toFixed(10)} = ${pp(cDelta)}\nD − A = ${TRACK03.hitD.toFixed(10)} − ${TRACK03.hitA.toFixed(10)} = ${pp(dDelta)}\n\nretrieval_scored = ${TRACK03.scored}\nabstentions = ${TRACK03.abstentions}\ncases = ${TRACK03.cases}`}</pre>
            <p className="small muted">Negative/null evidence is retained. Claim ceiling: retrieval ablation only, not end-to-end QA superiority.</p>
            <Link className="secondary" href="/track03">Open exact A/B/C/D table</Link>
          </article>

          <article className="panel" style={{ background: "rgba(182,156,255,0.07)" }}>
            <p className="eyebrow">Release custody · measured</p>
            <h2>One canonical SHA-256 identity per FCO.</h2>
            <pre className="result">{`canonical_address = "fco:" + object_sha256\nrelease_gate = every(node.id === canonical_address)\n\ncurrent release manifest:\nunique canonical FCOs = ${canonicalFcoCount}\nidentity problems = []\nidentity validation = ${release.fco_identity_validation.status}`}</pre>
            <p className="small muted"><KnowledgeTermLink slug="fco">Hash identity</KnowledgeTermLink> establishes retained object identity, not correctness. Signature and Merkle states remain separate.</p>
            <a className="secondary" href="/api/release">Open live release JSON</a>
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / WORKED GRAPH EXAMPLES</span>
        <h2 className="displayTitle">The same operation changes meaning by track.</h2>
        <div className="grid threeCol">
          <article className="panel">
            <p className="eyebrow">Track 01 · illustrative structural math</p>
            <h2><KnowledgeTermLink slug="hydraontology">Identity resolution</KnowledgeTermLink></h2>
            <pre className="result">{`alias_coverage = resolved_aliases / expected_aliases\nreference: 2 / 2 = 100%\npoison:    1 / 2 = 50%\nantidote:  2 / 2 = 100%`}</pre>
            <p className="small muted">Worked example only; this is not presented as an executed EnterpriseRAG/HERB benchmark result.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Track 02 · declared synthetic canary</p>
            <h2><KnowledgeTermLink slug="hydrablast">Reverse closure</KnowledgeTermLink></h2>
            <pre className="result">{`exposed = |reverse_closure(vulnerable_version) ∩ Services|\nreference → poison → partial repair → full repair\n    0     →   2    →       1        →     0`}</pre>
            <p className="small muted">Structural canary/design lane only; no real npm exposure or exploitability claim.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Track 03 · executed data model</p>
            <h2><KnowledgeTermLink slug="hydramemory">Temporal evidence paths</KnowledgeTermLink></h2>
            <pre className="result">{`Session -NEXT/PREV→ Session\nSession -ASSERTS→ Fact\nFact -DERIVED_FROM→ Session\nFact -ABOUT→ Entity\nFact -SUPERSEDED_BY→ Fact\nFact -CONTRADICTS→ Fact`}</pre>
            <p className="small muted">These relationship types were materialized in the full500 graph lane.</p>
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">05 / EXAMPLE CODE</span>
        <h2 className="displayTitle">The judge can see what the application actually checks.</h2>
        <pre className="result">{`// canonical migration parity\nconst canonicalParity =\n  fcoSetDelta === 0 &&\n  edgeSetDelta === 0 &&\n  contentHashDelta === 0 &&\n  localFcoRoot === hostedFcoRoot &&\n  localEdgeRoot === hostedEdgeRoot;\n\n// context-classification coverage\nconst coverage = 100 * classifiedFindings / rawFindings;\nconst abstentionRate = 100 * abstentions / rawFindings;\n\n// graph retrieval stays path-aware\nconst query = {\n  database: "hydradg",\n  query: "what changed and why?",\n  graph_context: true,\n  query_apps: true\n};`}</pre>
        <p className="small muted">Example code mirrors the checked project contracts; credentials are server-side and are never printed here.</p>
        <div className="actions"><Link className="secondary" href="/how-to#hosted-hydradb">Hosted path</Link><Link className="secondary" href="/knowledge#hydradb">KB: HydraDB</Link><Link className="secondary" href="/graph">Inspect FCG</Link></div>
      </section>

      <section className="panel architecture" style={{ border: "2px solid rgba(246,200,95,0.45)" }}>
        <p className="eyebrow">Final chain</p>
        <h2>Every answer should be able to resolve backward.</h2>
        <div className="flow mono"><span>source</span><b>→</b><span>evidence</span><b>→</b><span>KnowledgeAtom</span><b>→</b><span>SeedOfTruth</span><b>→</b><span>state</span><b>→</b><span>retrieval / reasoning path</span><b>→</b><span>claim ceiling</span><b>→</b><span>FCO / FCG custody</span></div>
        <p className="muted">That final graph/custody step is what lets a judge ask not only “what was retrieved?” but “which state, through which relationships, from which evidence, under what claim boundary?”</p>
      </section>
    </main>
  );
}
