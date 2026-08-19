#!/usr/bin/env python3
"""Fail closed when a registered HydraDG project term lacks a knowledge anchor.

This is a static release check. It does not establish that every possible
unknown term in English is covered; it enforces the declared project-term set.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMS = ROOT / "apps/hydradg-web/lib/projectTerms.ts"
KNOWLEDGE = ROOT / "apps/hydradg-web/lib/knowledgeLinks.ts"

term_text = TERMS.read_text(encoding="utf-8")
knowledge_text = KNOWLEDGE.read_text(encoding="utf-8")
slugs = re.findall(r'slug:\s*"([^"]+)"', term_text)
missing = [slug for slug in slugs if f'slug: "{slug}"' not in knowledge_text]

print(f"DECLARED_PROJECT_TERMS={len(slugs)}")
print(f"MISSING_KNOWLEDGE_TERMS={len(missing)}")
for slug in missing:
    print(f"MISSING={slug}")

if missing:
    raise SystemExit(1)
print("TERM_KNOWLEDGE_COVERAGE=PASS")
