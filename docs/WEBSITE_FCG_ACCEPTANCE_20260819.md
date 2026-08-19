# Website FCG acceptance criteria — 2026-08-19

A judge-facing website release may be called `WEBSITE_FCG_NAVIGATION_GREEN` only when:

- all primary routes build and return 200;
- the declared project-term knowledge coverage check passes;
- `/api/site-fcg` returns a valid graph;
- `/api/release-status` returns the conservative state object;
- every displayed project SHA is either linked to its evidence/FCO context or deliberately marked as a raw identity;
- the static fallback smoke check passes;
- local-only controls fail closed when their backend is absent;
- internal link crawler reports zero broken required links;
- mobile and desktop browser checks pass.

This gate is website/navigation evidence only; it does not raise a scientific claim ceiling.
