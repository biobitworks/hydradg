import Link from "next/link";

import { buildReleaseManifest } from "@/lib/releaseMeta";

function compact(value: string, left = 10, right = 8) {
  if (value.length <= left + right + 1) return value;
  return `${value.slice(0, left)}…${value.slice(-right)}`;
}

export default function ReleaseStamp() {
  const release = buildReleaseManifest();
  const git = release.git_sha === "LOCAL_UNRESOLVED" ? "local build" : release.git_sha.slice(0, 12);
  const identityPass = release.fco_identity_validation.status === "PASS";

  return (
    <footer className="computeSection curatedFooter" aria-label="HydraDG deployed release identity">
      <div>
        <p className="eyebrow">Deployed release identity</p>
        <p className="small muted">
          Version <strong>{release.version}</strong> · Git <span className="mono">{git}</span> · FCO identity {identityPass ? "PASS" : "FAIL"}
        </p>
      </div>
      <div>
        <p className="small muted">
          Release FCO <Link className="mono compact" href={`/fco/${encodeURIComponent(release.release_fco.id)}`}>{compact(release.release_fco.id)}</Link>
        </p>
        <p className="small muted">
          SHA-256 is one canonical identity per FCO; identity does not establish correctness. {release.signature_state} · {release.merkle_state}.
        </p>
      </div>
    </footer>
  );
}
