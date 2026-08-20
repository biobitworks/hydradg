import type { Metadata } from "next";

import JudgeBreadcrumbs from "@/components/JudgeBreadcrumbs";
import ReleaseStamp from "@/components/ReleaseStamp";
import SiteNav from "@/components/SiteNav";
import "./globals.css";

export const metadata: Metadata = {
  title: "HydraDG — Verifiable Graph Memory",
  description: "Hack Hydra 2026: graph-native memory, ontology and dependency experiments with explicit FCO/FCG evidence custody.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <SiteNav />
        <JudgeBreadcrumbs />
        {children}
        <ReleaseStamp />
      </body>
    </html>
  );
}
