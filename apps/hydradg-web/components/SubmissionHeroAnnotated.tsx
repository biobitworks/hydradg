"use client";

import Link from "next/link";
import { useState } from "react";
import { GOLDEN_PATH_STEPS } from "@/components/GoldenPathStep";
import { HERO_REGIONS, SUBMISSION_HERO, type HeroRegion } from "@/lib/submissionHeroFco";

function pct(value: number, axis: "x" | "y" | "w" | "h") {
  const base = axis === "x" || axis === "w" ? 1000 : 1000;
  return `${(value / base) * 100}%`;
}

function regionStyle(region: HeroRegion, active: boolean) {
  const isSponsor = region.kind === "sponsor";
  const isTrack = region.kind === "track";
  return {
    left: pct(region.bbox.x, "x"),
    top: pct(region.bbox.y, "y"),
    width: pct(region.bbox.w, "w"),
    height: pct(region.bbox.h, "h"),
    borderColor: active ? "#fff1c7" : isSponsor || isTrack ? "#e2c375" : "rgba(226,195,117,0.55)",
    background: active ? "rgba(226,195,117,0.22)" : isSponsor ? "rgba(226,195,117,0.10)" : isTrack ? "rgba(226,195,117,0.14)" : "rgba(226,195,117,0.06)",
    boxShadow: active ? "0 0 0 2px rgba(242,217,149,0.35), 0 8px 28px rgba(0,0,0,0.35)" : "none",
  } as const;
}

export default function SubmissionHeroAnnotated() {
  const [activeId, setActiveId] = useState<string | null>("hydralamp-core");
  const active = HERO_REGIONS.find((r) => r.id === activeId) ?? HERO_REGIONS[0];

  return (
    <section className="submissionHeroStage" aria-label="HydraLamp submission hero with sponsor and judge-path annotations">
      <div className="submissionHeroCanvas">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={SUBMISSION_HERO.imagePath}
          alt="HydraLamp submission hero — cosmic custody navigation chart with Hydra lamp centerpiece"
          className="submissionHeroImage"
        />
        <div className="submissionHeroFade" aria-hidden="true" />
        <svg className="submissionHeroJudgeArc" viewBox="0 0 1000 1000" preserveAspectRatio="none" aria-hidden="true">
          <path
            d="M 540 940 C 620 720, 760 520, 900 120"
            fill="none"
            stroke="rgba(226,195,117,0.55)"
            strokeWidth="3"
            strokeDasharray="10 8"
          />
        </svg>
        {HERO_REGIONS.map((region) => (
          <button
            key={region.id}
            type="button"
            className={`submissionHeroBox submissionHeroBox--${region.kind}`}
            style={regionStyle(region, activeId === region.id)}
            aria-pressed={activeId === region.id}
            aria-label={`${region.label}. ${region.detail}`}
            onClick={() => setActiveId(region.id)}
          >
            <span className="submissionHeroBoxLabel">{region.label}</span>
          </button>
        ))}
      </div>

      <aside className="submissionHeroAside">
        <p className="eyebrow" style={{ color: "#e2c375" }}>Annotated region · {active.kind.replace("_", " ")}</p>
        <h2 className="submissionHeroAsideTitle">{active.label}</h2>
        <p className="muted">{active.detail}</p>
        {active.priority ? <span className="pill pillWarn">{active.priority} sponsor</span> : null}

        <div className="submissionHeroGoldenRail" aria-label="Golden path steps for judges">
          <p className="eyebrow" style={{ color: "#e2c375", marginTop: "18px" }}>Golden path · judge steps</p>
          <div className="submissionHeroStepGrid">
            {GOLDEN_PATH_STEPS.map((step) => (
              <Link key={step.number} href={step.href} className="submissionHeroStepChip">
                <span>{step.number}</span>
                <span>{step.short}</span>
              </Link>
            ))}
          </div>
        </div>
      </aside>
    </section>
  );
}
