# Exp183b — THE PERMUTATION COURT: pre-registration (FROZEN before flight)

**Author**: Whisper (DC15W), C5065 (2026-08-13) · **Substrate**: claude-fable-5
**Arc**: H14 Deck A, cell A3 (exp183 cold case) — the corrected form of the C5057 check (a) + check (b) composed into one job
**Authorization**: Creator, this session: "fly on alt4 if you can" — **single-use GO, consumed by this flight**. Account: `IBMQ_ALT4` (registry: state up, authorization *open*, billing *free*, balance 361 s of 600 s limit — reading 33 h stale per board #126's known staleness; the per-job fit gate at submit remains the wall).
**Genre fence**: mechanism discrimination on a recorded anomaly. **No advantage claim; no new-physics claim.** `attack_preflight` not applicable (nothing here is an advantage-flavored claim); account preflights mandatory and run.

## The anomaly on trial

Exp183 (ibm_fez, 2026-07-19, job `d9e3cqsjeosc73fi9lqg`): the sift-discard sectors read E₃(XXY) = +0.0955 and E₃(YYY) = −0.10075 against a pre-registered |E₃| < 0.05 band (~9σ each). C5057's mechanistic pass proposed ONE coherent GHZ-prep phase error: |000⟩ + e^{iφ}|111⟩ with V·sinφ appearing as +s in every single-Y sector and −s in YYY; fit φ = 6.64°, V = 0.848 (this cycle re-verified: forward model reproduces banked M = 3.3695 exactly).

**C5065 correction to the C5057 spec, recorded first**: check (a) as written ("per-permutation decode from banked counts") was **inexecutable — a false premise**. The manifest's own circuit order shows XXY was the *only* single-Y sector ever flown; XYX and YXX do not exist in any banked job. What was $0-verifiable (and passes) is the weaker consistency test: |E₃(XXY)| = |E₃(YYY)| opposite-sign at z = 0.33, and one (φ, V) pair reproducing M. The discriminating test requires flight. This is that flight.

## What flies (14 circuits, one job, ibm_fez required — abort if ALT4 cannot see fez)

Prep (all circuits): `h(0); cx(0,1); cx(1,2)` — qubits (q0,q1,q2) = (Alice, Bob, Charlie). Basis: X → `h`, Y → `sdg; h`. Measure qᵢ → cᵢ. 8000 shots per circuit.

- **Arm A (base)**, 8 circuits: XXX, XYY, YXY, YYX (Mermin set → in-window M_A) + **XXY, XYX, YXX** (the three single-Y permutations — Y on Charlie / Bob / Alice respectively) + YYY.
- **Arm B (corrected)**, 6 circuits: XXX, XYY, YXY, YYX + XXY, YYY — identical except `rz(−φ̂)` on q2 immediately after prep, with **φ̂ derived in code** from the frozen banked inputs (s = (0.0955 − (−0.10075))/2, M = 3.3695 → φ̂ = atan2(s, M/4) ≈ 0.11597 rad = 6.644°; derived identifiers, never transcribed).

**Layout pinned and shared**: one linear physical triple (a–b–c connected), chosen at submit from live backend properties (min Σ readout-err + 2q-err over connected triples), passed as `initial_layout` to **every** circuit with `optimization_level=1` and a frozen `seed_transpiler=1837`. Pinning is load-bearing: the discriminand is "does it matter *which qubit* carries Y" — physical qubits must be constant across the three permutations. Layout recorded in the manifest.

**Custody upgrade over exp183**: the decode dumps **raw counts to disk** (the no-raw-counts-banked gap both cold cases just hit).

## Frozen decision rules (all constants sealed here)

- **G1 — health gate (whole flight)**: M_A ≥ 3.0 (se_M = 2/√8000 = 0.0224). Below → NO-TEST, publish anyway.
- **G2 — anomaly-present premise (validity gate for D3 only)**: mean(|E₃_A(XXY)|, |E₃_A(YYY)|) ≥ 0.05. Below → the July anomaly has drifted away in-window; D3 is NO-TEST and the drift itself is filed as an A1-census datapoint (weather evidence for the sector residual).
- **D1 — PRIMARY, permutation symmetry**: χ² = Σᵢ ((E₃_A,i − Ē)/se)² over the three single-Y sectors, se = 1/√8000 = 0.01118, df = 2, **α = 0.01 (crit 9.210)**. χ² ≤ crit → **SYMMETRIC** (supports the single coherent phase error). χ² > crit → **QUBIT-SPECIFIC** (readout-crosstalk / ZZ class; per-sector deviations reported, largest named with its qubit).
- **D2 — sign structure (secondary)**: all three single-Y sectors share one sign AND E₃_A(YYY) is opposite-signed with |E₃_A(YYY)| within 3·se·√2 of the single-Y mean magnitude. Reported PASS/FAIL, does not gate.
- **D3 — intervention (valid iff G2)** — all three readings pre-registered:
  - (i) |E₃_B(XXY)| < 0.05 AND |E₃_B(YYY)| < 0.05 → **MECHANISM CONFIRMED** (phase dialed away; sign convention as modeled);
  - (ii) both |E₃_B| > 1.5×|E₃_A counterparts| → **MECHANISM CONFIRMED, sign convention inverted** (the correction doubled the phase; documented outcome, not a failure);
  - (iii) both |E₃_B| within ±3σ of |E₃_A| counterparts → **CORRECTION INERT — mechanism NOT confirmed**;
  - anything else → UNDERDETERMINED (per-sector numbers published, no verdict forced).
- **D4 — M recovery (reported, pre-declared UNDERPOWERED)**: predicted M_B − M_A = 4V(1−cosφ̂) ≈ +0.023 vs se_diff = 0.0316 (0.7σ) — printed with its interval, never gated. Pre-registering the underpower is the point (no post-hoc σ-shopping).
- **Positive controls (in-code, run before submit; the gate must be able to block)**: statevector-synthesized counts through the *same decode path*: (P1) planted uniform e^{iφ} → D1 must PASS and sectors read +sinφ/−sinφ (also pins the rz sign convention: the corrected arm must read 0 in sim); (P2) planted qubit-asymmetric perturbation (Y-sector response unequal by construction) → D1 must FAIL. Selftest failure = no submission.

## Spend + hygiene

14 shallow 3q circuits × 8000 shots, one job; estimate ≲ 15 s QPU vs ALT4's 361 s (stale) balance — the submit-time fit re-read is authoritative. Submit-and-exit (no inner waits); completion via ship-computer watch. `preflight_account_check.py` + `preflight_deep_whisper_c5041.py` must pass on the flight script; `QPU_ACCOUNT_VAR=IBMQ_ALT4` with `assert_explicit_account()` + `service_for_submission()` (a write that defaults is worse than a read that defaults). DD OFF (campaign default). Publish either way, appended in place to `docs/anomalies-mechanistic-pass-whisper-c5057.md`.
