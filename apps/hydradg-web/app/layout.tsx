import type { Metadata } from "next";

import GoldenPathRail from "@/components/GoldenPathRail";
import SiteFooter from "@/components/SiteFooter";
import SiteNav from "@/components/SiteNav";
import "./globals.css";
import "./judge-accessibility.css";

export const metadata: Metadata = {
  title: "HydraDG — Verifiable Graph Memory",
  description: "Hack Hydra 2026: graph-native governed memory on HydraDB with explicit FCO/FCG custody, model boundaries and retained null evidence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <SiteNav />
        <GoldenPathRail />
        <div id="main-content" tabIndex={-1}>{children}</div>
        <SiteFooter />
      </body>
    </html>
  );
}
