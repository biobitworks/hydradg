# HydraDG licensing policy

Status: ACTIVE_PROJECT_POLICY
Human directive source: Byron P. Lee, 2026-08-18

## Base license

The base license selected by the project owner for Biobitworks-authored research and publication material is:

**Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)**

Canonical license reference: https://creativecommons.org/licenses/by-nc-nd/4.0/

This policy applies by default to copyrightable Biobitworks-authored material where CC licensing is appropriate, including research prose, preprints, documentation, figures, explanatory diagrams, reports, notebooks as authored works, and project-generated data/database material to the extent the project has the rights to license it.

## Software exception

CC BY-NC-ND 4.0 is **not used to overwrite software licenses**.

Creative Commons recommends using software-specific licenses rather than CC licenses for computer software. Code therefore carries its own applicable software license. Any code copied, modified, linked, or derived from an upstream project retains all upstream license obligations.

HydraDB upstream is licensed under GNU AGPL v3; HydraDB-derived covered code must retain the applicable AGPL-3.0 obligations. Merely using HydraDB as a separate service does not authorize relicensing HydraDB itself.

Biobitworks-authored software that is independent of AGPL-covered code requires an explicit software-license decision before public release. Until that decision is made, do not infer that CC BY-NC-ND 4.0 is a suitable software license merely from this base policy.

## Per-object license custody

Every admitted FCO/FCG object must preserve licensing provenance instead of flattening it to the project default.

Required fields:

- `upstream_license_id`
- `upstream_license_url`
- `upstream_license_evidence`
- `upstream_rights_holder`
- `project_output_license_id`
- `project_output_license_url`
- `license_compatibility_state`
- `license_transform_state`
- `license_review_receipt`

A KnowledgeAtom must cite the exact license associated with its source/version. A downstream Seed of Truth must retain the licenses of all load-bearing source atoms even when the synthesized project-authored prose is distributed under CC BY-NC-ND 4.0.

## License compatibility states

Use one of:

- `COMPATIBLE_FOR_CURRENT_USE`
- `ATTRIBUTION_REQUIRED`
- `SOURCE_CODE_OBLIGATION`
- `NONCOMMERCIAL_RESTRICTION`
- `NO_DERIVATIVES_RESTRICTION`
- `PUBLIC_DOMAIN`
- `PERMISSION_REQUIRED`
- `LICENSE_CONFLICT`
- `LICENSE_UNRESOLVED`

No atom with `LICENSE_CONFLICT`, `PERMISSION_REQUIRED`, or `LICENSE_UNRESOLVED` may be promoted into a distributable final artifact without review.

## NoDerivatives handling

CC BY-NC-ND 4.0 permits sharing the licensed material but does not permit distribution of adapted material under the license without separate permission from the rights holder. Therefore:

1. Do not treat CC BY-NC-ND source material as freely transformable publication input solely because it is public.
2. Distinguish quotation/excerpting or uses permitted by law from adaptations requiring permission.
3. Record whether an atom is verbatim evidence, factual extraction, deterministic metadata extraction, or a transformed expression.
4. Never apply the Biobitworks CC BY-NC-ND 4.0 notice to third-party material in a manner suggesting Biobitworks owns or relicenses that material.

## Public-domain material

Public-domain source material remains public domain. A downstream original selection, arrangement, annotation, analysis, figure, or other independently copyrightable Biobitworks contribution may carry the project license, but the underlying public-domain source is not converted into CC BY-NC-ND material.

## Models, agents, prompts, and generated artifacts

For every model/agent-derived object store:

- source/input licenses;
- model/provider and version when known;
- agent/session identity;
- prompt/tool transformation receipt;
- authorship/contribution classification;
- rights/license status of the generated output;
- project output license if the project has authority to apply it.

Do not infer output ownership or relicensing rights merely from model provenance.

## Publication rule

For each public preprint/release, produce a license manifest that separates:

1. Biobitworks-authored CC BY-NC-ND 4.0 material;
2. software and its software-specific licenses;
3. third-party sources and their original licenses;
4. public-domain material;
5. quoted/reproduced material governed by permission or applicable legal exception;
6. unresolved material excluded from the distributable artifact.

## Claim ceiling

This policy records project licensing intent and operational rules. It is not a legal opinion and does not establish that every contemplated reuse is legally permissible. License compatibility and downstream distribution claims must remain bounded by the exact upstream terms and, where needed, qualified legal review.
