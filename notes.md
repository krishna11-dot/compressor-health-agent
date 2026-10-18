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
- SPEC.md section 8 says Windows 11; this machine is Windows 10 Home
  (build 19045). Noted in Stage 0; no change made because SPEC.md is frozen.
- ruff runs with the default rule set of ruff 0.17.1 (407 rules, no
  [tool.ruff] section). A ruff upgrade can change the rules without any code
  change. Decide in Stage 10, when the S rules are added, whether to list the
  rules explicitly in pyproject.toml.
