<!-- notes.md: ideas, deferred work and observations that do not belong in SPEC.md.
SPEC.md is frozen until Stage 4 produces real numbers, so new ideas land here.
Nothing in this file is a decision; decisions go in PLAN.md. -->
# Notes

## Deferred: build when the path exists
- Injection defence for free-text input (the data has no free-text field).
- Separate database roles.
- Rate limiting.
- Kill switch.
- Decision models (Jev, Laya); tiers stay code rules an auditor can inspect.

## Observations
- SPEC.md section 1 says the data is "logged at 1 Hz" and covers "roughly
  Feb-Aug 2020". The CSV shows a nominal 10 s interval (88.2% of gaps exactly
  10 s, 99.98% within 9-13 s) and runs from 2020-02-01 00:00:00 to
  2020-09-01 03:59:50. Found in Stage 1 (PLAN.md decision 1). SPEC.md stays
  frozen until Stage 4; correct it then.
- Oil_level is 1 in 90% of rows (100% in Feb, about 45% in Aug); UCI says
  active = oil low, so check whether active means 0 or the description is
  wrong (paper/UCI). Note for Stage 2: Oil_level is constant in Feb, the
  suggested training month, so normalization must handle zero variance.
- MPG = 0 at TP3 < 8.2 at 08:21:35; COMP is also 0 and the UCI page says COMP
  follows MPG, so the polarity is unresolved, not necessarily a mismatch.

## Failure windows (data/failure_windows.json, Stage 1)
- Source is the UCI page's Failure Information table. A failure table for the
  2020 data was not found in the paper; other papers found cover 2022
  datasets and were not used. Open: SPEC section 1 names the paper as Veloso
  et al., Scientific Data 9, 764 (2022), while _about names "the Davari 2021
  paper"; settle which paper was checked.
- The UCI table has two rows labelled #1.
- Page row 1 spells the type "Air leak"; all four are normalized to
  "Air Leak" in the JSON.
- Window #2's maintenance note says "30Apr at 12:00"; probably a typo for
  30 May. Kept as on the page.
- Window #1 ends at 23:59 as given; Stage 4 should treat the last minute
  (23:59:00-23:59:59) as inside the window.
- For Stage 4: the 24 h before #1 is 27.1% missing (largest gap 14,092 s,
  3.9 h) and before #4 is 28.4% missing (largest gap 25,085 s, 7.0 h), so lead
  time there can be cut short by holes. Window #3 itself has a 13,622 s
  (3.8 h) gap inside it.
- SPEC.md section 8 says Windows 11; this machine is Windows 10 Home
  (build 19045). Noted in Stage 0; no change made because SPEC.md is frozen.
- ruff runs with the default rule set of ruff 0.17.1 (407 rules, no
  [tool.ruff] section). A ruff upgrade can change the rules without any code
  change. Decide in Stage 10, when the S rules are added, whether to list the
  rules explicitly in pyproject.toml.
