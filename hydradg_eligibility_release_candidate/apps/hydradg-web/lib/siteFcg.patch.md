# siteFcg.ts patch instructions

In `SECTION_SPECS`, change the `/eligibility` entry to:

```ts
{
  route: "/eligibility",
  label: "Eligibility + Award Case",
  role: "final-track-fit-gap-matrix-award-case-and-release-gate",
  claim: "SUBMISSION_ELIGIBILITY_AUDIT_AND_BOUNDED_TRACK_AWARD_FIT"
},
```

Change Golden Path edges from:

```ts
["/custody", "GOLDEN_PATH_NEXT", "/evidence"],
```

to:

```ts
["/custody", "GOLDEN_PATH_NEXT", "/evidence"],
["/evidence", "GOLDEN_PATH_NEXT", "/eligibility"],
["/eligibility", "SUMMARIZES", "/best-use"],
["/eligibility", "SUMMARIZES", "/track03"],
["/eligibility", "BOUNDED_BY", "/custody"],
```

Change the site artifact `golden_path` to:

```ts
[
  "/",
  "/judge",
  "/track03",
  "/best-use",
  "/graph",
  "/models",
  "/custody",
  "/evidence",
  "/eligibility",
]
```

Do not claim this site FCG is signed or Merkle-committed unless an actual operation occurs.
