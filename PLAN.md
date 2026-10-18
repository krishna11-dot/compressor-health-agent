<!-- PLAN.md: the open, data-dependent decisions from SPEC.md section 3b.
Each one is decided at the stage shown, using numbers from the real data.
The owner records the choice and the reason under its heading; nothing is pre-filled. -->
# PLAN: open decisions

## 1. Real sampling interval and gap pattern (Stage 1)
Choice (decided 2026-10-19): option A, nominal interval 10 s.
Basis (step 1.2b, whole CSV, 1,516,947 gaps): 1,337,521 gaps (88.2%) are
exactly 10 s; 99.98% are 9-13 s; smallest gap 8 s. This contradicts the
"1 Hz" in SPEC section 1 (SPEC is frozen; not edited).
Gap pattern: 331 gaps over 60 s, 37 days 21:31:03 in total, largest
172,918 s (about 48 h). Data runs 2020-02-01 00:00:00 to 2020-09-01 03:59:50.
Big gaps are spread over every month (36 to 64 per month, Feb-Aug).
Per day (step 1.3b, missing % = 1 - readings/8,640, clipped at 0; 212 full
days): 0%: 49, 0-5%: 23, 5-25%: 97, 25-50%: 21, 50-75%: 14, 75-<100%: 6,
100%: 2. Median 13.9%, mean 17.8%. 49 days exceed 8,640 readings (max 8,717).
Missing readings: span-based 324,812; gap-based 327,095 (difference explained
by 9-13 s jitter in the small gaps).

## Timestamp timezone assumption (SPEC section 4, Stage 1)
Fact: timestamps carry no timezone (e.g. 2020-02-01 00:00:00).
Choice (decided 2026-10-19): take timestamps exactly as recorded, naive, with
no timezone conversion. The paper's failure windows are compared in the same
untouched form.
Reason: SPEC section 4 forbids conversion, and data and failure windows must be
in the same zone. Open: the owner checks the paper for which zone it uses.

## 2. Continuous vs on/off signals (Stage 1)
Not decided yet.
Observation only (step 1.3b): COMP, DV_eletric, Towers, MPG, LPS,
Pressure_switch, Oil_level, Caudal_impulses each hold exactly two distinct
values, 0.0 and 1.0, over the whole file. Meanings come from the UCI page.

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
