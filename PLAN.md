<!-- PLAN.md: the open, data-dependent decisions from SPEC.md section 3b.
Each one is decided at the stage shown, using numbers from the real data.
The owner records the choice and the reason under its heading; nothing is pre-filled. -->
# PLAN: open decisions

## 1. Real sampling interval and gap pattern (Stage 1)
Not decided yet.
Observation (step 1.1, first 5 data rows only): gaps of 10, 9, 10, 10 s, which
suggests about 10 s sampling, not the 1 Hz in SPEC. To be confirmed in step 1.2
over the whole file.

## Timestamp timezone assumption (SPEC section 4, Stage 1)
Fact: timestamps carry no timezone (e.g. 2020-02-01 00:00:00).
Choice (decided 2026-10-19): take timestamps exactly as recorded, naive, with
no timezone conversion. The paper's failure windows are compared in the same
untouched form.
Reason: SPEC section 4 forbids conversion, and data and failure windows must be
in the same zone. Open: the owner checks the paper for which zone it uses.

## 2. Continuous vs on/off signals (Stage 1)
Not decided yet.

## 3. Missing-seconds threshold X for skipping a window (Stage 2)
Not decided yet.

## 4. Window length, default 600 s (Stage 2)
Not decided yet.

## 5. Features, and which are critical (Stages 2 and 6)
Not decided yet.

## 6. Smoothing and sustain N, defaults 3 and 5 (Stage 3)
Not decided yet.

## 7. Envelope quantiles, default 0.5% and 99.5% (Stage 3)
Not decided yet.

## 8. Baseline period and margin before the first failure (Stage 3)
Not decided yet.

## 9. Silent-feed timeout T (Stage 9)
Not decided yet.

## 10. CI gate thresholds (after Stage 4)
Not decided yet.

## 11. ALERT_OWNER, a named human (before Stage 9)
Not decided yet.

## 12. Groq model IDs, checked on console.groq.com/docs/models (Stage 7)
Not decided yet.

# Other decisions (not in SPEC 3b)

## Stage 1 code location (decided 2026-10-19)
Choice: CSV reading goes in src/compressor_agent/load.py; the Stage 1 report
is printed by scripts/explore_data.py, a small dev script (about 40 lines).
Reason: load is a core module allowed by SPEC section 8; the report is a
one-off look at the data, so it is a dev script, not package code.

## Plotting library (decided 2026-10-19)
Choice: matplotlib, as a dev-only dependency.
Reason: Stage 1 asks for a plot of one day of the main pressure signal, and
the SPEC section 8 stack has no plotting library.

## pandas type checking under mypy strict (decided 2026-10-19)
Choice: option A, pandas-stubs as a dev dependency (installed 3.0.5.260914,
for pandas 3.0.6).
Reason: mypy then really checks our pandas calls. Rejected: B (ignore missing
imports) and C (type: ignore per file), which make every pandas value
unchecked. Fallback if the stubs clash with pandas 3: option B.
