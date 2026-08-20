import Link from "next/link";

export default function KnowledgeTermLink({ slug, children }: { slug: string; children: React.ReactNode }) {
  return (
    <Link
      href={`/knowledge#${slug}`}
      title="Open this term in the HydraDG terminology matrix"
      style={{
        color: "inherit",
        textDecoration: "underline",
        textDecorationColor: "rgba(182,156,255,0.75)",
        textDecorationThickness: "2px",
        textUnderlineOffset: "3px",
        background: "rgba(182,156,255,0.10)",
        borderRadius: 4,
        padding: "0 3px",
      }}
    >
      {children}
    </Link>
  );
}
