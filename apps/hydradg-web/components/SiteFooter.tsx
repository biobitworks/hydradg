import Link from "next/link";

import { CUSTODY_SEAL } from "@/lib/custodySeal";
import { buildSiteFcg } from "@/lib/siteFcg";

const PUBLICATIONS = [
  ["FCO v1", "https://doi.org/10.5281/zenodo.21210575"],
  ["FCO v3", "https://doi.org/10.5281/zenodo.21420906"],
  ["FCO v4/v5 + Vithia", "https://doi.org/10.5281/zenodo.21829929"],
  ["Self/Non-Self × Safe/Unsafe", "https://doi.org/10.5281/zenodo.21830287"],
  ["Shadow Dogma", "https://doi.org/10.5281/zenodo.21830361"],
  ["XenoDisorder", "https://doi.org/10.5281/zenodo.21830386"],
] as const;

const MODEL_CARDS = [
  ["Biobitworks Vithia FMO-076", "https://huggingface.co/biobitworks/fco-vithia-fmo-076"],
  ["Qwen2.5 7B Instruct", "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct"],
  ["Qwen2.5 Coder 7B Instruct", "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct"],
  ["EleutherAI Pythia-14M", "https://huggingface.co/EleutherAI/pythia-14m"],
] as const;

export default function SiteFooter() {
  const site = buildSiteFcg();
  const deployedSha = process.env.VERCEL_GIT_COMMIT_SHA ?? "LOCAL_OR_UNAVAILABLE";

  return (
    <footer className="siteFooter" aria-label="HydraDG release, licensing, citations and custody">
      <div className="siteFooterGrid">
        <section>
          <p className="footerHeading">HydraDG</p>
          <p className="small muted">Graph-native governed context on HydraDB. Primary Hack Hydra submission: Track 03 · Memory + Context Retrieval.</p>
          <nav className="footerLinks" aria-label="Footer project navigation">
            <Link href="/">Home MVP</Link><Link href="/judge">Judge</Link><Link href="/track03">Results</Link><Link href="/best-use">Why HydraDB</Link><Link href="/graph">Graph</Link><Link href="/models">Models</Link><Link href="/custody">Custody</Link><Link href="/evidence">Evidence</Link><a href="/backup/hydradg.html">Static</a>
          </nav>
        </section>

        <section>
          <p className="footerHeading">Custody status</p>
          <dl className="footerFacts">
            <div><dt>FCO identity</dt><dd>SHA-256</dd></div>
            <div><dt>Project signature</dt><dd>{CUSTODY_SEAL.hydradg_project.signature_state}</dd></div>
            <div><dt>Project Merkle/MMR</dt><dd>{CUSTODY_SEAL.hydradg_project.merkle_state}</dd></div>
            <div><dt>Private key</dt><dd>EXTERNAL · NEVER SHIPPED</dd></div>
            <div><dt>Deployed Git SHA</dt><dd className="mono compact">{deployedSha}</dd></div>
          </dl>
          <p className="small muted">Publication key fingerprint (publication FCG scope only): <span className="mono compact">{CUSTODY_SEAL.fco_publication_v1.public_key_sha256_fingerprint}</span></p>
          <Link className="footerAction" href="/custody">Inspect signing boundary →</Link>
        </section>

        <section>
          <p className="footerHeading">Research citations</p>
          <div className="footerLinks stacked">
            {PUBLICATIONS.map(([label, href]) => <a key={href} href={href} rel="noreferrer">{label}</a>)}
          </div>
          <p className="small muted">Current project-supplied publication links are preserved as citations; cryptographic scope is shown separately from bibliographic identity.</p>
        </section>

        <section>
          <p className="footerHeading">Model cards</p>
          <div className="footerLinks stacked">
            {MODEL_CARDS.map(([label, href]) => <a key={href} href={href} rel="noreferrer">{label}</a>)}
          </div>
          <p className="small muted">Track 03's retained K=5/K=10 deterministic retrieval matrix used no language model. Local model outputs remain a separate probabilistic diagnostic lane; model benefit is not established.</p>
        </section>
      </div>

      <div className="siteFooterBottom">
        <p className="small muted"><strong>Software / website / scripts:</strong> Apache License 2.0. <strong>Designated FCO/FCG research content:</strong> CC BY-NC-ND 4.0. Third-party datasets, models and sources retain upstream rights.</p>
        <div className="footerLinks">
          <a href="https://github.com/biobitworks/hydradg/blob/main/LICENSE">Apache-2.0</a>
          <a href="https://github.com/biobitworks/hydradg/blob/main/LICENSING.md">Licensing scope</a>
          <a href="https://github.com/biobitworks/hydradg/blob/main/THIRD_PARTY_NOTICES.md">Third-party notices</a>
          <a href="/api/site-fcg">Site FCG JSON</a>
        </div>
        <p className="small muted">{site.nodes.length} site-section FCOs · {site.edges.length} application-level FCG edges. A hash is identity, not truth. A publication signature is not inherited by the HydraDG project graph.</p>
      </div>
    </footer>
  );
}
