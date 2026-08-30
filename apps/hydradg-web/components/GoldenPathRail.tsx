import Link from "next/link";

const GOLDEN_PATH = [
  ["HOME", "/"],
  ["CHANGE STATE", "/judge"],
  ["READ RESULT", "/track03"],
  ["WHY HYDRADB", "/best-use"],
  ["TRACE FCO", "/graph"],
  ["MODELS USED", "/models"],
  ["VERIFY CUSTODY", "/custody"],
  ["EVIDENCE", "/evidence"],
] as const;

export default function GoldenPathRail() {
  return (
    <div className="goldenPathShell" aria-label="Golden path judge walkthrough">
      <div className="goldenPathRail">
        <span className="goldenPathLabel">GOLDEN PATH</span>
        <div className="goldenPathLinks">
          {GOLDEN_PATH.map(([label, href], index) => (
            <span className="goldenPathStep" key={href}>
              {index > 0 ? <span className="goldenPathArrow" aria-hidden="true">→</span> : null}
              <Link href={href}>{label}</Link>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
