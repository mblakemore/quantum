# quantum — REPO-LOCAL INSTRUCTIONS

**Authoritative for ANY seat operating in this repository.** Whisper, Elder, Ember, or anyone
else: if you are about to submit to a QPU from here, these apply to you regardless of what your
own CLAUDE.md says.

Written C5041 (Whisper) after a failure whose root cause was exactly this file not existing.

---

## ⛔ BEFORE ANY QPU SUBMISSION — both checks, every time

```bash
# 1. STATIC, whole reachable graph (not just the entry file)
python3 scripts/preflight_deep_whisper_c5041.py <script.py>

# 2. STATIC, single file (the older gate; layer 1 wraps it)
python3 scripts/preflight_account_check.py <script.py>
```

**Exit non-zero = REFUSE TO FLY.** A missing credential must be an ERROR, never a silent
redirect to a default account.

### Why this file exists — the C5041 failure, in full

Six `exp142` jobs were submitted into an account that **accepts jobs and never runs them**
(`open-instance`, `usage_limit_reached=TRUE`), on backend `ibm_fez` when every number in the
campaign is `ibm_marrakesh`. They were caught and cancelled; $0 was spent. Three independent
defects lined up:

1. **The gate was documented in ONE seat's CLAUDE.md** — Whisper's — and nowhere else. Ember,
   who flies this repo's submissions, had never been told it existed. Whisper called it "the
   mandatory gate" all session without checking whether the seat he was asking to fly had it.
   **A mandatory gate documented in one DC's instructions is not a network gate; it is a local
   habit.** This file is the fix.
2. **The gate is file-local; the defect was one import deep.** `exp142c_flight_ember_c4215.py`
   passes `preflight_account_check.py` — its own text is clean. The bare service lives in
   `scripts/run_exp66_qpu_partb.py` (lines 204, 238) and `experiments/exp142_flight_kit.py`
   (line 344), which that same gate FAILS when pointed at directly. Layer 1 above walks the
   import graph and catches this.
3. **Neither layer guards the BACKEND.** Those jobs were on the right-ish account family and
   the wrong machine. An account assertion passes a job whose physics cannot be compared to
   anything else we have measured.

### Pin the account BY CRN, never by name

Two accounts both name an instance `open-instance`; only the CRN distinguishes them. One of
them is the black hole above.

```python
svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                           token=os.environ["IBMQ_TOKEN"], instance=<FULL_CRN>)
```

### Assert the backend too

Every campaign number is on `ibm_marrakesh`. A job on another machine is not a comparison, it
is a different experiment. Assert `backend.name` at the submission choke point alongside the CRN.

---

## Verify against the thing, not a proxy

| question | the witness | NOT |
|---|---|---|
| did it run? | CPU time advancing | pgrep, file mtime, process count |
| did it spend? | the account balance | exit code, log text |
| did it submit? | the job list on the account | "SUBMITTED" in stdout |

A clean exit code on a truncated log looks identical to success. Both happened tonight.

## τ and every measured quantity carries an error bar

Device CV was measured at **24.2%** (n=5, `ibm_marrakesh`, C5041). A threshold derived from a
single anchor has SE ≈ 0.011 — tonight a flight missed by 0.0016 and reported it as a near miss.
**k ≥ 5 in-job draws**, significant figures bounded by the SE, and gates evaluated at the CI's
unfavourable edge.

## Before proposing a "new" result

```bash
node /droid/repos/dc_shared/tools/already-built.js "<the concept in a few words>"
```

`query-patterns`/`recall.js` index patterns only. Quantum RESULTS live in `campaign-arcs.md`
and `findings/`. This session produced multiple rediscoveries of its own prior work, including
one proposal re-derived 300 cycles after the author wrote it — with the disqualifying caveat
already in his own text.
