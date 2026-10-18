<!-- AGENTS.md: the few rules that change how a coding agent works in this repo.
SPEC.md section 8 is the full reference; this file is only the short list.
Re-read at each maintenance pass and delete any rule that no longer changes behaviour. -->
- Never fill in facts (units, column meanings, failure windows, rates, benchmarks) from memory; unverified stays verified:false.
- Every test must be able to fail.
- Run scripts/verify.py and paste its real output before claiming anything works.
- One branch and one PR per stage, revertable on its own.
- Build no machinery the spec does not ask for.
- Keep code beginner-readable: plain functions, small files, descriptive names.
