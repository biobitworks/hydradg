import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "HydraDG — Custody-Aware Memory Graph",
  description: "Hack Hydra Track 03 web application for temporal memory, provenance, divergence, and recovery.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <nav aria-label="HydraDG">
          <Link href="/">HydraDG</Link>
          {" · "}
          <Link href="/eligibility">Submission custody</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
