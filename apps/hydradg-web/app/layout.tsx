import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HydraDG — Custody-Aware Memory Graph",
  description: "Hack Hydra Track 03 web application for temporal memory, provenance, divergence, and recovery.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
