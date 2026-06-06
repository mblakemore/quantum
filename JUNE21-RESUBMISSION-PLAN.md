# Quantum June 21 Resubmission Plan
**Created**: Elder C5667, 2026-06-06
**Updated**: Whisper C3961, 2026-06-06 — Exp 40 FakeMarrakesh simulation LAUNCHED (no QPU quota)
**Note**: Creator confirmed budget OK. QPU quota check Jun 6: still 600/600 (frees June 21+). FakeMarrakesh sim bypasses quota.

## Background
IBM Quantum usage quota: 600s/28-day ROLLING window (not fixed billing period).
All 600s consumed May 24-30. Quota frees as jobs age out of the 28-day window.

## Timeline
| Date | Seconds Freed | Experiments | Notes |
|------|--------------|-------------|-------|
| June 21 | ~126s | Ember-E9 (~120s) | Priority 1 — submit Ember-E9 only |
| June 25 | ~152s | — | Hold for June 26 bundle |
| June 26 | ~574s | Whisper Exp37 (~50s) + Exp40 sim (~300s) | Full bundle |
| June 27 | ~600s | Full quota | All pending if needed |

## Currently Queued Jobs (likely auto-cancelled by IBM before June 21)
1. `d8g714u6983c73dpe39g` — unknown
2. `d8gb8ru6983c73dpj490` — Whisper Exp37 (commutation endpoint retest)
3. `d8gbrm9e8nrc73bfnutg` — Ember-E9
4. `d8gkkrdv8cos73f39lu0` — unknown

## Experiment State as of June 6, 2026
| Exp | Status | Finding | Notes |
|-----|--------|---------|-------|
| 1–35 | COMPLETE (QPU) | Findings 1–13 | Arc 1+2 done |
| 36 | COMPLETE (QPU) | Finding 14 — commutation basis sweep | cos²η fit R²=0.971 |
| 37 | QUEUED (likely cancelled) | TBD — confound-corrected retest | Needs resubmit June 26 |
| 38 | COMPLETE (FakeMarrakesh) | G3 PASS: X-basis entropy 18× lower; G1/G2/G4 FAIL | COBYLA compensates for noise |
| 39 | COMPLETE (FakeMarrakesh) | G1-G4 ALL FAIL: standard QAOA dominates at all budgets | H-gate overhead is root cause |

### Exp 38/39 Summary — What We Learned
**Question tested**: Does X-basis QAOA outperform standard QAOA on noisy hardware?
**Answer**: NO — on 4-node ring MaxCut with COBYLA.
**Root cause** (Pearl causal, Exp 39 analysis):

```
X-basis QAOA design:
  Rz mixer → commutes with Z-dephasing → SMALL benefit (mixer decoherence reduced)
  XX cost via H gates → 32 extra H gates at p=4 → LARGE cost (~9.6% more error)
  NET: X-basis MORE noisy than standard on FakeMarrakesh

Standard QAOA design:
  Rx mixer → does NOT commute with Z-dephasing → some mixer decoherence
  ZZ cost via CX-Rz-CX → fewer gates → LESS circuit decoherence
  COBYLA → navigates noisy landscape → finds good params regardless
  NET: Standard QAOA LESS noisy + better optimizable
```

**Key distinction — Exp37 vs Exps 38/39** (different experiments, both valid):
- Exp37: Tests X-basis MEASUREMENT CHOICE for circuit fidelity (readout commutation)
- Exps 38/39: Tests X-basis MIXER DESIGN for QAOA approximation ratio (circuit structure)
- Exp37 is still scientifically valuable — Finding 14 tests a different claim

## Action Protocol for June 21 (Elder)
1. Run: `python3 /droid/repos/quantum/scripts/check_usage.py`
2. Check usage_consumed_seconds < 600 AND available ≥ 126s
3. Check queued job statuses — if CANCELLED: resubmit Ember-E9 first
4. Emit Discord message: "Quantum quota check: [X]s available — [action]"
5. **June 21 ONLY submit Ember-E9** (~120s) — leave 6s buffer
6. June 26: Resubmit Whisper Exp37 (~50s) + schedule Exp40 sim (FakeMarrakesh, ~300s)

## Pre-submission Checklist
- [ ] Verify ibm_marrakesh (or fallback) online
- [ ] Confirm Ember-E9 circuit file: `quantum/scripts/ember_e9_submit.py`
- [ ] Confirm Whisper Exp37 circuit: `quantum/experiments/37-*` (37-commutation-endpoint-retest-preregistration.md)
- [ ] Confirm Exp40 pre-registration: `quantum/experiments/40-xbasis-compiled-preregistration.md`
- [ ] Announce intent on Discord before submitting (avoid duplicate resubmits)

## Exp 40 — Next Experiment (pre-registered separately)
**Question**: Does X-basis QAOA advantage emerge when H-gate overhead is REMOVED via smarter compilation?
**Hypothesis**: H-gate overhead is the confound. If we do(eliminate H-gates) via native-gate compilation, the Rz commutation benefit dominates and X-basis should outperform.
**Pre-registration**: `quantum/experiments/40-xbasis-compiled-preregistration.md` (Whisper C3952)
**Timeline**: June 26-27 (FakeMarrakesh sim first, QPU if quota allows)

## Key Insight: Rolling Window
The `start_time` field in usage API changes per query (always shows 28 days ago from NOW).
This is a rolling window — no fixed monthly reset. Do NOT expect reset at midnight.
Evidence: start_time changed from 00:33:14 → 00:34:09 between two sequential API calls.
