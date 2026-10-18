# SPEC.md: compressor-health-agent

## 1. One-page overview (read this first)

WHAT IT IS
A program that reads a metro train's compressor sensors and warns a human
when the compressor starts behaving abnormally, then records why.

THE DATA
MetroPT-3 (UCI Machine Learning Repository, DOI 10.24432/C5VW3R): one real
train's Air Production Unit (compressor) at Metro do Porto, Portugal,
roughly Feb-Aug 2020, described as logged at 1 Hz, about 1.5M rows, 15
signals. Ground truth failures come from the operator's maintenance
reports. EVERY detail here, including the sampling rate and row count, is
to be checked against the CSV, the UCI page and the paper (Veloso, Ribeiro,
Gama, Pereira, Scientific Data 9, 764, 2022). Note: 1.5M rows at 1 Hz is
only about 17 days, so either the rate differs or there are large gaps.
Stage 1 settles this.

HOW IT WORKS
1. Cut the data into time windows (for example 10 minutes).
2. Turn each window into a few numbers (features).
3. Learn what "normal" looks like from a clean period.
4. Compare new windows to normal with three checks:
   A. outside the normal range for a sustained time
   B. drifting steadily away from normal
   C. an unusual combination of values
5. If a check fires, look up in a small graph which component and failure
   type it may relate to.
6. Sort by severity:
   Tier 1: flag a named human; the system takes no action
   Tier 2: wait for a human to approve or reject with a reason
   Tier 3: log it
7. Write a short report from the evidence and save a permanent record.

HOW WE KNOW IT WORKS
For each documented failure: did it warn first, by how many hours, and how
many false alarms per day? None of this is measured yet.

THREE ASSURANCE QUESTIONS
Q1 Before go-live, how do we know it detects correctly and stays within
   policy? -> offline evaluation and the red team in CI
Q2 Can we explain any alert to an auditor? -> GET /audit/{alert_id}
Q3 Do we find out about degradation before the failure does? -> the monitor

WHAT IT IS NOT
It does not control the train. It sends no real page or SMS. It does not
schedule maintenance. It has not yet run on the real data.

BUSINESS PROBLEM
Metro maintenance teams need earlier, explainable warning of compressor
degradation without being flooded by false alarms. This system flags
sustained departures from normal, links them to a documented failure type,
and leaves every decision to a named human with an audit record.
TODO: cite the problem's motivation from the MetroPT paper after reading
it. Do not cite other operators' case studies as if they covered
compressors.

VALUE (formula, not numbers)
Value = hours of warning before a documented failure, plus false alarms per
day. Money = (failures caught early x the operator's cost of an unplanned
withdrawal) minus (false alarms x cost of one inspection). The operator's
figures are unknown and not assumed. Do not invent cost, downtime or
savings numbers anywhere.

STATUS LINE (update from measured results only)
Architecture: production-grade. Real-data evaluation: pending.

## 2. Glossary (plain words)

Window: a fixed span of time of readings, reduced to a few numbers.
Feature: one number computed from a window, such as a slope.
Baseline: the feature values seen in a clean "normal" period.
Envelope: the lower-upper range of normal for one feature.
Sustained breach: outside the envelope for N windows in a row.
Z-score: how many standard deviations a value is from normal.
Isolation forest: a model that flags unusual combinations of values.
Failure window: start and end of a failure documented by the operator.
Alert episode: alerts less than 30 minutes apart, merged into one.
Lead time: hours between the first alert in the episode connected to a
  failure and the reported start of that failure.
False alarm: an alert episode outside every failure window plus margins.
Tier: severity level that decides who acts.
Audit record: permanent record of one alert and why it happened.
Knowledge graph (KG): a small lookup: feature -> component -> failure type.
Silent feed: no readings arriving; with no data there are no alerts, so a
  dead system looks the same as a healthy one unless it is checked.
Fixture: a small hand-made data series used by tests, with a known answer.

## 3. Decisions

3a. ALREADY MADE (do not re-ask)
- Project: compressor-health-agent, a fresh repo, package compressor_agent.
- Claim wording: production-grade architecture, real-data results pending.
  Never "prototype", never "enterprise". Nothing unmeasured is claimed.
- Stack: section 8. No TypeScript, Rust, Tailwind or UI.
- The LLM is OFF by default. The deterministic template report is the
  baseline. The LLM only explains; it never decides or acts.
- Decision models (Jev, Laya) are not used. Tiers are code rules, so an
  auditor can inspect them. Revisit only via notes.md.
- Notifier is a log file only. Tier 2 recommends an inspection; it does not
  schedule anything.
- Tier rules are the Stage 6 defaults, revisited after Stage 4 numbers.
- ROI is the formula in section 1. No invented figures.
- Audit log, API-key auth, red-team cases and CI without secrets are as
  specified below.
- DEFERRED until their path exists (recorded in notes.md, not built):
  injection defence (the data has no free-text field), separate database
  roles, rate limiting, kill switch.
- Working style: stages, predictions, "I WRITE" functions, one PR per stage.
- Demo hosting is not decided. Local run plus a screen recording first;
  record anything further in notes.md.

3b. OPEN, DATA-DEPENDENT (decide at the stage shown, with numbers from my
data; record my choice and reason in PLAN.md)
- Real sampling interval and gap pattern: Stage 1, from the CSV.
- Which signals are continuous and which on/off: Stage 1, from the UCI page.
- Missing-seconds threshold X for skipping a window: Stage 2, after the gap
  report.
- Window length (default 600 s): Stage 2.
- Which features, and which are critical: Stages 2 and 6.
- Smoothing and sustain N (defaults 3 and 5): Stage 3, after the chart.
- Envelope quantiles (default 0.5% and 99.5%): Stage 3.
- Baseline period: Stage 3. It must end before the first failure window,
  with a margin proposed from the data.
- Silent-feed timeout T: Stage 9, from the real sampling interval.
- CI gate thresholds: after Stage 4. I decide.
- ALERT_OWNER (a named human): I decide before Stage 9.
- Groq model IDs: I check console.groq.com/docs/models before enabling the
  LLM in Stage 7.

## 4. Data rules

- Record source, DOI, licence, download date and sha256 in
  data/provenance.json.
- Before any modelling: read the real CSV header and first rows, record
  observed min/max, report the real sampling interval, missing seconds
  overall and per day, and state the timestamp timezone assumption in
  PLAN.md. Do NOT convert timezones. Failure windows and data must be
  compared in the same zone.
- Report any mismatch between the CSV and expectations to me BEFORE
  changing anything. Do not silently reconcile it.
- Column meanings and units come from the UCI page, not memory.
- data/failure_windows.json stays EMPTY until I paste windows from the
  paper (Stage 1). Each entry has start, end, type, citation and verified
  (false until I confirm).
- Never invent a failure window, a unit, a threshold or a benchmark number.
- No real data is committed to the repo.
- README says plainly: one train, one asset type, Porto; results may not
  generalise.

## 5. Stages (the build order)

Every stage ends with: the report format from the session rules, then ONE
comprehension question from the agent.

STAGE 0: Setup
  Empty repo. git init and a first commit. Python 3.12.10 via uv, src
  layout, package compressor_agent. ruff, mypy strict, pytest. .gitignore
  for data/raw, .env and audit files.
  AGENTS.md: at most 10 lines, only the rules that change behaviour (never
  fill in facts from memory; every test must be able to fail; verify.py
  before any claim; one branch and PR per stage; no machinery the spec does
  not ask for; keep code beginner-readable). SPEC.md section 8 remains the
  full reference.
  A PLAN.md with headings for each open decision in 3b. A notes.md that
  starts with a section "Deferred: build when the path exists" listing:
  injection defence for free-text input, separate database roles, rate
  limiting, kill switch, decision models. A small scripts/verify.py that
  runs ruff, mypy and pytest and prints one pass/fail table with times (it
  grows as stages land, see section 8). SKIPPED is never a pass.
  GitHub: I create an empty GitHub repository named compressor-health-agent
  myself (no README, no licence) and give you its URL; you add it as origin
  and push main. Until I do, use local branches and merge locally only
  after I review `git diff main`.
  Done when: verify.py prints a real table on the empty project.

STAGE 1: Look at the data (read-only)
  Print header, first rows, row count, time range, the real sampling
  interval and its distribution. Min/max per column. Missing-seconds
  percentage overall and per day. Plot one day of the main pressure signal.
  With me, decide from the UCI page which columns are continuous and which
  are on/off, and write data/signals.json with verified:false. I paste the
  failure windows from the paper into data/failure_windows.json,
  verified:false, so later stages keep the baseline clean.
  Create data/provenance.json with the source, DOI, download date and
  sha256 that I give you, and the licence text I read off the UCI page. Do
  not fill in the licence yourself.
  Done when: I can describe in my own words what one day of the signal
  looks like and what the real sampling interval is.

STAGE 2: Validation, windows and features
  Validate every reading before windowing: values within the physical
  ranges in signals.json, on/off signals only 0 or 1, no NaN or infinity,
  no duplicate timestamps. Rejected readings are counted by reason and
  never silently dropped.
  Windows are defined by TIME (for example 600 s), not row count: real logs
  have gaps and counting rows would silently stretch a window. A window
  with more than X% missing seconds is skipped and counted, never
  evaluated.
  I WRITE: window_features(). Candidate features, chosen after Stage 1:
  average pressure, pressure slope per minute, fraction of time the
  compressor is loaded, motor-current mean and spread.
  Unit tests with known answers on hand-made data (a straight line has a
  known slope). Propose the test plan first and wait for my OK.
  Create docs/feature-map.md. At the end of EVERY stage, add a short
  section with: what the stage does (two sentences), the files and entry
  point, how to run it, MY prediction vs what happened (I write this line),
  and what is not yet verified.
  Done when: the hand-made tests pass, a bad reading is rejected and
  counted, and a gapped window is skipped and counted.

STAGE 3: Baseline, check A and the end-to-end test
  Baseline period decided here (3b). I WRITE: envelope bounds from
  quantiles of the baseline, and the sustained-breach rule with smoothing
  so one spike does not alert. Show one chart of a feature with its
  envelope.
  Create tests/fixtures/make_fixture.py: it generates a small hand-made
  series (a healthy sawtooth pressure pattern with a slow drift injected
  at a known time). Add ONE end-to-end test: the series runs through
  validation, windows, baseline and check A, and an alert fires before the
  injected failure time. Wire it into verify.py.
  Done when: I can predict which windows alert on a hand-made example, and
  the end-to-end test passes.

STAGE 4: Evaluate on real failures
  Use the failure windows from Stage 1. Metrics: detection rate, lead time,
  false alarms per day. NO accuracy headline: failures are a tiny fraction
  of rows. I WRITE: the lead-time function using alert episodes.
  verify.py runs the evaluation on the hand-made series, and on the real
  data when given --csv.
  Write a short README.md now: the status line, the data source with DOI
  and caveats, how to run verify.py, and the Stage 4 numbers (or "not yet
  measured"). Stage 11 extends it.
  Report the numbers whatever they are. Do not tune. I set CI gates after
  seeing them. Compare with a published benchmark only if I supply the
  number and its citation. SPEC.md unfreezes after this stage.

STAGE 5: Checks B and C
  Z-score drift. Isolation forest fitted on the baseline only. Evaluate
  each check alone and combined. Report what each one adds.

STAGE 6: Knowledge graph, diagnosis and tiers
  KG from verified sources. Only failure types documented in the paper
  (expect one). Component-to-failure links start verified:false. Diagnosis
  is deterministic traversal, no LLM.
  Tier defaults:
    Tier 1: sustained breach on a critical feature AND another check agrees
            AND the KG reaches a documented failure type
    Tier 2: any sustained breach, or drift on a derived feature
    Tier 3: anything else
  I WRITE: the tier assignment function.
  CHECKPOINT: after this stage, STOP. With real numbers from Stage 4 in
  hand, I decide whether Stages 7-11 are worth building. Do not start
  Stage 7 unless I say so.

STAGE 7: Report and output filter
  Template report first (deterministic). Optional LLM through LiteLLM,
  default OFF, model names in config. Every report is checked by
  evidence_consistency_check: components and failure types must be in the
  KG and in the evidence; every number must match a MEASURED value (a
  report's own citations never vouch for its numbers); certainty language
  ("will fail") is rejected, because reports state evidence and likelihood
  only. A failed report is regenerated once, then replaced by the template.
  Every report carries fallback_reason:
  none | llm_error | filter_rejected | llm_disabled. When the LLM is on,
  the exact evidence bundle sent to it is stored.

STAGE 8: Storage, audit log, API, logging
  In-memory store first, TimescaleDB later. The audit log is written from
  the pipeline layer (so evals and replays are audited too), as JSONL and
  in the database, tagged run_type (production/eval/redteam/replay).
  Append-only by design; the database also refuses UPDATE and DELETE via a
  trigger, proven by a slow test. A human decision is a NEW record. The
  audit record also stores the evidence bundle given to the report writer,
  so a wrong report can be traced back to its inputs.
  API: key auth on every route except /health. Routes: POST /readings,
  GET /asset/status, GET /alerts, GET /alerts/{id},
  POST /alerts/{id}/decision, GET /audit/{alert_id}, GET /health,
  GET /metrics.
  Logging: structured JSON logs; every pipeline log line carries alert_id
  (or window_end) so one alert can be followed across stages. LangSmith
  tracing is optional: on only when LANGSMITH_API_KEY is set, covers the LLM
  report path, and CI never needs it. With the LLM off, the audit record's
  per-stage latencies are the trace.

STAGE 9: Notifier and monitor
  Notifier interface with a log-file implementation only. "Flagged to a
  named human" means a Notifier call plus an audit record. The monitor runs
  on an interval, with SEPARATE counters for LLM failures, filter
  rejections and config-disabled templates; it alerts on any llm_error when
  the LLM is enabled; it reports P50/P95/P99 latency, Tier 2 rejection rate
  and cost per alert. Cache hit rate shows n/a when unused. It never
  auto-adjusts thresholds.
  The monitor also reports alerts per hour and tier mix compared with the
  baseline period, the same split by compressor loaded vs idle, and the
  time since the last reading arrived. It alerts the named owner if no
  reading has arrived for T minutes (T decided from the real sampling
  interval found in Stage 1). A silent feed must never look like a healthy
  one.

STAGE 10: Red team and CI
  Cases (exit 1 if any fails): impossible reading rejected and counted; NaN
  or missing signal rejected; duplicate timestamps rejected and counted;
  spliced normal data over a failure window still flagged or reported as a
  gap; report citing something outside the KG blocked; wrong value blocked;
  certainty language blocked; bad LLM twice falls back with
  fallback_reason=filter_rejected; LLM error falls back with llm_error;
  Tier 2 stays pending without a human decision; no API key returns 401; a
  gapped window is skipped and counted; no readings for T minutes raises
  the silent-feed alert. LLM cases use a fake LLM client.
  CI runs ruff, mypy, fast tests, red team and the synthetic evaluation
  with LLM disabled and NO secrets. The synthetic evaluation uses
  tests/fixtures/make_fixture.py from Stage 3; no real data is committed.
  LLM paths are tested with a fake client. A separate job runs slow tests
  with a TimescaleDB container. Branch protection is enabled by me in
  GitHub settings; document that step and never claim it is enforced.
  Enable ruff S rules on src. Add a test that every model is frozen and
  that list, dict or set fields are allowlisted with a reason.

STAGE 11: Load test, Docker, README
  locust at rates chosen after Stage 1 confirms the real sampling rate
  (assume 1, 10 and 100 readings per second), plus 1000 labelled "fleet
  simulation, optional". Report P50/P95/P99 and what broke in LOAD_TEST.md
  with real numbers only. Dockerfile and compose. The detector warms up
  from stored readings after a restart; document the single-replica limit.
  Extend the README per section 9.

## 6. Design reference

Pipeline: reading -> validate -> store -> window -> detect -> diagnose ->
tier -> report -> audit -> notify. Normal readings never touch an LLM. The
LLM only explains an anomaly code already found.
No agent can execute code, write to equipment or issue control commands.

Guardrails (as built):
  1. Input validation (Stage 2): schema, physical ranges from
     signals.json, on/off signals only 0 or 1, NaN/inf, duplicate
     timestamps. Rejected readings are counted by reason. Stale and future
     timestamp checks apply only to a live feed; this data is historical.
  2. Policy (Stages 6 and 7): tier authority; reports state evidence and
     likelihood, never certainty.
  3. Tools and permissions (Stage 10): the system is read-only toward the
     asset, with no code path that writes to equipment; no subprocess, exec
     or eval in src (dev scripts may use subprocess), enforced by ruff S
     rules.
  4. Output filter (Stage 7): evidence_consistency_check (named honestly,
     not "faithfulness"). It does real work only when the LLM is on.
  Deferred until the path exists (see notes.md): injection defence for
  free-text input, separate DB roles, rate limiting, kill switch.

Audit record fields: alert_id, timestamp, run_type, derived values,
triggered checks, KG path, components and failure types, tier, human
decision with reason and who, report text, fallback_reason, evidence
consistency result, evidence bundle, model, cost, stage latencies.

## 7. Evaluation rules

- Time-ordered split. Baseline and training only from periods before the
  failure being evaluated. No leakage.
- Lead time is measured from the start of the alert EPISODE connected to
  the failure. An isolated early blip that ends long before the failure is
  NOT early warning.
- Segments: compressor loaded vs idle, and time of day.
- evaluation/gates.json starts null. Measure first; I decide the gates.
  Never tune thresholds to flatter a result. If it is poor, say so and stop.
- Refuse to gate CI on unverified failure windows.
- Any synthetic result is labelled "pipeline check", never a model result.
- Evidence consistency pass rate on generated reports must be 100%.
- Tag every evaluation run with the git commit and the version (or hash) of
  failure_windows.json it used, so results can be compared across changes.
- If a result looks wrong, check the metric and lead-time code before
  blaming the detector.
- Always report how many failure windows were evaluated. With few events,
  give counts (for example "3 of 4 caught"), never bare percentages, and
  say the sample is too small for strong claims.

What I most want measured, in priority order:
  1. detection rate, lead time and false alarms per day on real failures
  2. missing seconds, readings rejected by reason, and windows skipped
  3. Tier 2 human rejection rate
  4. LLM failures counted apart from filter rejections
  5. P50/P95/P99 latency and cost per alert
  6. fast-suite time against the 60 s budget, and the 10 slowest tests
  7. alerts per hour vs baseline, and time since the last reading
     (silent feed)
Measures that cannot apply yet (no LLM, no API) are reported "n/a", never
zero.

## 8. Engineering rules (full reference), environment, stack

AGENTS.md carries only the short list from Stage 0. This section is the
full reference.

- Prefer the simplest design that meets this spec. No machinery the spec
  does not ask for. No backwards-compatibility layers.
- Core modules (Stages 0-6): load, validate, windows, baseline, detect,
  evaluate, kg, tiers. Ask me before adding any other module.
- Make impossible states unrepresentable (frozen Pydantic models).
- Never share one mutable object between concurrent tasks.
- Never name a metric something it does not measure.
- Count LLM failures separately from filter rejections.
- Never fill in facts from a source you have not read.
- Every test must be able to fail. Do not add a test I cannot explain;
  delete tests that duplicate others or test only names.
- Test levels, each kept small:
  Unit (most): known-answer hand-made data for validate, windows, envelope,
  lead time and tiers.
  Property (two or three only, via hypothesis): a straight line's slope
  equals its true slope for any slope; the validator never crashes on any
  number; no window contains a reading outside its span.
  Integration (from Stage 8): the database store and the audit-log trigger.
  End-to-end (one): the Stage 3 hand-made series with an injected drift
  runs through the whole pipeline and an alert fires before the injected
  failure.
- scripts/verify.py grows as stages land: the end-to-end test (Stage 3),
  the evaluation on the hand-made series (Stage 4), the red team (Stage
  10). With --csv it also runs the evaluation on the real data. SKIPPED is
  never reported as a pass.
- When a PR removes or changes behaviour, delete or update the tests that
  protected it in the same PR, and list them in the PR description.
- For a bug fix, first write a test that fails, show it failing, then fix
  and show it passing.
- Before building a new module, propose how to test it (known-answer
  hand-made data, property-based, end-to-end) and wait for my OK.
- Never claim a change works without running scripts/verify.py and pasting
  its actual output. If you did not run it, say so.
- One branch and PR per stage, revertable alone. After each stage run a
  maintenance pass: list tests that cannot fail, turn any repeated mistake
  into a lint rule or test, update docs/feature-map.md, and record the fast
  suite time against the 60 s budget.
- At each maintenance pass, re-read AGENTS.md and propose deleting any rule
  that has not changed behaviour. Shorter beats longer.
- Before calling the MVP done, and whenever I switch to a newer model, run
  a holistic review: "What decisions in this codebase no longer fit what it
  has become?" List stale decisions, dead code and over-specified rules,
  and wait for me to choose what to change.
- When a mistake recurs, prefer a type change or lint rule over a note.
- If the fast suite exceeds the 60 s budget: first run
  `pytest --durations=10`, then delete or fix tests that cannot fail or
  duplicate others, then run in parallel with pytest-xdist (tests must not
  share files or state). Never filter which tests run to save time.

Environment: Windows 11, PowerShell, 8 GB RAM, no GPU. Use pathlib. Paths
may contain spaces. No bash-only scripts. The dev loop works without
Docker, using the in-memory store. Process the large CSV in chunks.

Stack: Python 3.12.10, uv, pandas, numpy, scikit-learn, FastAPI,
SQLAlchemy 2 async, PostgreSQL with TimescaleDB, NetworkX, Pydantic v2,
LiteLLM as the only LLM gateway, LangSmith (optional), prometheus-client,
pytest with hypothesis, locust, ruff, mypy, Docker, GitHub Actions. No
frontend.

Out of scope: TypeScript, Rust, Tailwind, a UI, a real paging channel,
maintenance scheduling, decision models (Jev, Laya), remote test
offloading, injection defence, separate DB roles, rate limiting, kill
switch (these four deferred, see notes.md), other assets (a bearing
dataset is Phase 2).

## 9. README and repo metadata

Repo name: compressor-health-agent.
GitHub description: Governed predictive-maintenance agent on real
compressor sensor data: deterministic detection, knowledge-graph
diagnosis, tiered human authority, full audit trail.
Topics: predictive-maintenance, anomaly-detection, langgraph, fastapi,
timescaledb, knowledge-graph.

README top line: "Governed predictive-maintenance agent on real
metro-train compressor data: deterministic detection, knowledge-graph
diagnosis, tiered human authority, full audit trail. LLM only explains; it
never decides or acts." Then the status line.
README contents: business problem and the value formula; data source with
DOI and honest caveats (one train, one asset type, Porto); ingestion
design (historical load plus simulated replay, because there is no live
train); architecture diagram; the guardrails as built; how Q1, Q2 and Q3
are answered; REAL evaluation numbers, or the plain statement that they are
not yet measured; real load-test numbers; known gaps, including the
deferred controls from notes.md; and a "demo vs real use" note (real use
needs real-data results, review by a rail maintenance engineer, a real
notification channel and a security review). Synthetic results are labelled
"pipeline check". A short version is written in Stage 4 and extended in
Stage 11.

## 10. Done when

CORE (after Stage 6):
1. Real data runs end to end and the numbers are in the README.
2. scripts/verify.py passes locally, including the end-to-end test.
3. docs/feature-map.md matches the code, and I can explain every file.

FULL SCOPE (only if I choose to continue at the Stage 6 checkpoint):
4. CI is green on GitHub with no secrets.
5. An auditor can pull any alert and see evidence, KG path, tier, human
   decision and report.
6. The monitor runs on its own schedule, reports LLM failures separately
   from filter rejections, and alerts on a silent feed.
7. A load test is documented with real numbers.
Only then start Phase 2.