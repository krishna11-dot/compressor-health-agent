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
- SPEC.md section 8 says Windows 11; this machine is Windows 10 Home
  (build 19045). Noted in Stage 0; no change made because SPEC.md is frozen.
- ruff runs with the default rule set of ruff 0.17.1 (407 rules, no
  [tool.ruff] section). A ruff upgrade can change the rules without any code
  change. Decide in Stage 10, when the S rules are added, whether to list the
  rules explicitly in pyproject.toml.
