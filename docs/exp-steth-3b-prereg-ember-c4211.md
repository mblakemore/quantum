# Exp-STETH §3(b) PRE-REGISTRATION (Ember, C4211) — committed BEFORE submit

**Creator directive (2026-07-21, general#476):** "Fly the §3(b) retrofit (two-copy overlap replacing
a tomography block)." Whisper's stethoscope annex §3(b) fallback; my STETH tolerance curve (C4210,
quantum@339eb47) fed the §3(a) gate. This is the §3(b) FLIGHT.

## Estimand (frozen)
Tr[rho^2] (purity) of a FIXED entangled mixed state rho on n=1,2,3 system qubits (state_seed=3210:
shallow entangler on system+bath, bath traced out; true purity 0.6363/0.3806/0.2985 — verified by
statevector). Entangled-not-product BY DESIGN so the 3^n tomography baseline cannot be factorized.

## Two arms + estimators (frozen, both UNBIASED — exactness-gated noiseless)
- TWO-COPY: two independent copies, transversal destructive SWAP (Cincio et al.); per-shot
  P2=(-1)^(sum_i u_i&v_i), E[P2]=Tr[rho^2]. ONE measurement setting for any n.
- TOMOGRAPHY: 3^n Pauli-basis settings; UNBIASED variance-subtracted purity
  Tr[rho^2]=(1/2^n) sum_P (<P_hat>^2 - Var_hat). (Naive <P_hat>^2 is biased high — advisor.)

## Deliverable + metric (frozen)
MEASURED shot-bill delta = M_tomo / M_twocopy to reach a MATCHED SE on Tr[rho^2], from the EMPIRICAL
per-shot variances of each arm (measured, not assumed). Report the n=1,2,3 SCALING TREND (settings
3^n -> O(1)).

## Pre-committed calls (no forced positive)
- The shot-bill delta MAY be modest or NEGATIVE at small n (two-copy pays an entangling layer + 2x
  qubits + a longer circuit; tomography arm is shallower). The deliverable is the TREND, not a win at
  every rung. An honest-negative is a valid landing (matches the week's honest-null discipline).
- FRAME: RESOURCE comparison (two-copy primitive vs the tomography BLOCK it replaces), NOT a
  quantum-advantage claim — classical shadows/randomized measurements estimate purity with no 2nd
  copy. Confidence cap <=0.6 (quantum behavioral cap; not sim-replicated on hardware yet).
- SCOPE (stated): primitive-level head-to-head with a fair standalone tomography block, NOT a retrofit
  of a named existing grader.

## Config (frozen)
Backend ibm_marrakesh (least busy, Heron-r2), 4000 shots/circuit, 42 circuits (3 two-copy + 3+9+27
tomography), seed_transpiler=3211. Exactness gate PASSED n=1,2,3 (noiseless arms recover purity within
<0.004). ps aux checked (no duplicate). 

## Kill / abort
Exactness gate is the pre-submit kill (passed). If decode shows either arm disagreeing with true
purity beyond plausible hardware error, report the discrepancy as the finding (not a swept result).
