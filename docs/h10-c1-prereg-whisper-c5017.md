# H10-C1 PRE-REGISTRATION — The Winding Meter (size-winding f(S), magnitudes AND phases)

*Whisper C5017, 2026-08-01, substrate claude-fable-5. Status: **FROZEN TEXT, awaiting Elder
co-check + Ember spec-seal + Creator GO.** Parents: scout `h10-c1-bridge-size-winding-scout-
whisper-c5015.md` (GO with target, SS7-SS10) and route freeze `scripts/h10_c1_rhohalf_route_
c5017.py`. Every number below is computed in committed artifacts (`results/h10_c1_operating_
point_c5017.json`, `..._trotter_error_c5017.json`, `..._rhohalf_route_c5017.json`,
`..._prereg_bars_c5017.json`) — nothing is asserted that was not computed, and every frozen
input is reproducible from committed code (the ephemeral-code gap was repaired this cycle: the
seeded H constructor and the Trotter convention are now committed and pinned to the frozen
artifacts at machine precision).*

## 1. Claim shape (printed first)

The first gate-model measurement of the **winding size distribution f(S)** — magnitudes and
phases — of a thermal operator under a fast scrambler, with the unwinding relation tested
quantitatively. **The claim is mechanism metrology** (the diagnostic that settled the
field's wormhole dispute, flown as a certified instrument with the control arms the disputed
experiment lacked). **Not claimed**: anything about gravity, wormholes, or holography — those
words appear only in an interpretation row citing GJW/MQ; nothing here is beyond classical
reach (N=6: every curve has an exact-theory overlay — exactness is the certification).
Statistic categories per the C5014 rule: G1/G4 are SIGN/ABSENCE tests, G2/G3 are RATIO-ORDERING
tests; none is a works-claim beyond its stated observable.

## 2. Frozen design

- **H** (committed constructor, `h10_c1_rhohalf_route_c5017.py::build_H`): all-to-all random
  Heisenberg + random Z fields, N=6, seed 42 — `default_rng(42)`, J=normal(15)/sqrt(6) over
  pairs in combinations order (drawn first), h=normal(6); probe Q = X on site 0. No ML, no
  fitting: the couplings existed before any winding was computed (the scout's SS7 local-chain
  NEGATIVE with the same instrument is the no-fishing receipt).
- **Operating point**: beta=0.6, t=0.3 (SS9 selection: rms<0.15, |alpha|>0.05, min shots).
- **TFD prep (the rho^{1/2} insertion — route frozen this cycle)**: compiled variational
  purification on 12 qubits, **L=3 layers, 12 shared parameters** (values in the route
  artifact), from 6 Bell pairs; each layer = 6 inter-side two-qubit couplings + one first-order
  sweep of angle gamma per side. **The ansatz IS the hardware circuit** (parameters absorb the
  sweep's Trotter error — no prep compilation gap exists by construction). F = 0.9669 vs exact
  TFD; prep-added meter bias 0.0072 (Trotter parity). Selection objective was fidelity ONLY,
  meter evaluated after (answer-agnostic — the route artifact's L2pp row shows higher F with
  worse meter bias; optimizing prep to the known alpha would be the ML-training trap of the
  disputed Nature claim). Route A (LCU-compiled e^{-beta H/2}) rejected on numbers: postselect
  1.1% at matching fidelity.
- **Evolution**: 2nd-order symmetric Trotter, r=2 (SS10; convention pinned incl. term order —
  the o1 alphas discriminate what the 2-norm cannot). ~180 CX per side pre-routing.
- **Coupling**: V = (3N - sum_i W_i)/4 with **W_i = X_iX'_i − Y_iY'_i + Z_iZ'_i** (eigencheck
  committed: +3 untouched site, −1 any Pauli — the XX+YY+ZZ form MISgrades Y). e^{igV} = 6
  commuting two-qubit blocks + global phase; ~18 CX.
- **Insertions/readout** (paper SS IX, Eqs. 106-107 + footnote 18; finite-beta = left-side
  measurement): Re[C(g)] run inserts (1+Q)/2 (X-basis postselect on site 0; submitted shots
  x2), Im[C(g)] run inserts exp(i pi Q/4) (one native 1q rotation).
- **Backend**: any Heron, 12-qubit chain + spectator-free placement, ALT open instance.

## 3. Registered decode (frozen) and bars (flight-estimator values, like-for-like)

**Decode** (`h10_c1_prereg_bars_c5017.py`, committed): f_hat(S) = (1/16) sum_k C_hat(g_k)
e^{-i g_k S} on the 16-point grid g_k = 2 pi k/16; **alpha_hat = −slope/2 of the unweighted
lstsq on unwrapped arg f_hat(S) over the FROZEN set S ∈ {1,2,3,4}** (frozen at prereg — a
data-dependent SNR-admission rule is unstable and invites decode discretion; if any frozen-set
|f_hat(S)| < 3 sigma_f that is a loud reported QUALITY flag, and alpha from the frozen set
stands). Ratios are reconstructed from f_hat: R_unwind = C(g*)/C(0), R_wrong = C(−g*)/C(0),
g* = −0.395 frozen. **lambda_hat = C_recon(0)/0.6658** is the attenuation self-calibration.
KEY METER PROPERTY (verified in the MC, `mc_error_table_n15k`): global depolarizing
attenuation scales all |f| and cancels in phases and ratios — alpha, R_unwind, R_wrong are
lambda-robust; only shot cost rises. Level bars would pay lambda^2 and are NOT gated.

| # | Gate | Frozen prediction | Registered bar |
|---|---|---|---|
| G1 | winding exists, right sign | alpha_4pt = **−0.1881** | alpha_hat < 0 at ≥5 sigma AND within −0.1881 ± max(3 sigma_alpha, 0.05) |
| G2 | unwinding at g* | R_unwind = **1.0697** | R_unwind > 1 at ≥3 sigma |
| G3 | wrong-sign dies | R_wrong = **0.8147** | R_wrong < 1 at ≥5 sigma |
| G4 | beta=0 winding ABSENT | alpha_4pt(beta0) = **0 exactly** | |alpha_hat_beta0| ≤ 3 sigma_alpha_beta0 |

**Registered verdict = G1 ∧ G2 ∧ G3 ∧ G4** (requires stages S1+S2 complete; a stage shortfall
= verdict INCOMPLETE, loudly — non-completion never reads as pass or fail; the H-2 rule).

**Reported rows (published either way, not verdict-changers):** R1 lambda_hat (self-calibration
+ the honesty meter for depth); R2 full f_hat(S) table vs as-flown overlay (magnitudes AND
phases — the headline exhibit); R3 energy books: dE_R = dE_L = **+0.790** at g* (coupling
energy cost; GJW negative-energy narrative confined to this row's interpretation sentence);
R4 g* vs 2 alpha: −0.395 vs −0.376 (2 x alpha_4pt) — the large-beta identity g*=2 alpha is
approximate at this OP and said so; R5 scrambled-coupling arm (per-shot random g' from a
frozen seeded list, Re leg): prediction **exactly 0** (= f(0), which vanishes by Z-parity of
H); R6 direct-circuit C(g) at {0, g*} vs reconstruction (consistency ≤3 sigma). The commuting
twin flies as EXACT-THEORY CONTRAST ONLY in v1 (alpha=−0.044, rms 0.474 = no clean winding;
flying a second Hamiltonian's full pipeline adds compile risk without touching the mechanism
claim — scope stated plainly, per the SS9 demotion).

## 4. Budget (staged; pool re-read at every submission)

| Stage | What | Submitted shots | Est. QPU-s |
|---|---|---|---|
| S0 | pilot: C(0) point (Re+Im), gives lambda_hat | 18k | ~6 |
| S1 | 16-pt DFT grid (Re 30k submitted + Im 15k per point) | 720k | ~200 |
| S2 | beta=0 arm, same grid (prep params = 0, shallow) | 288k | ~45 |
| S3 | books (2 variants x 3 bases x 6k) + scrambled (30k) + verify (90k) | 156k | ~45 |

Totals ≈ 1.18M shots ≈ **~300 QPU-s (estimate)** vs ~283 s remaining at drafting (600 s
trailing-28d pool; it ages out continuously — re-read at submit is mandatory and printed).
**Stage priority is the degradation order**: S3 drops first (reported rows become not-run,
stated), then S2 (verdict INCOMPLETE). MC error table at n=15k/component: lambda=1.0 → G1
20.9 sigma / G2 10.8 / G3 31.7; lambda=0.5 → 9.7 / 5.0 / 14.5; **lambda=0.3 → 5.6 / 3.0 /
8.6 (the registered minimums)**; lambda=0.15 → dies.

## 5. Kill / no-fly conditions

1. **Flight-script KA gate (mandatory)**: exact simulation of the ACTUAL pubs must reproduce
   every SS3 number to 1e-6, INCLUDING the circuit-level grading identity C(g) = sum_S f(S)
   e^{igS} through the compiled e^{igV} and both insertion variants. Any non-completion is a
   FAIL (unknown-is-not-a-value). Fail → no submission.
2. **Pilot gate**: lambda_hat < 0.3 → hold; 0.15 ≤ lambda_hat < 0.3 → fly only with shots
   rescaled by (0.3/lambda_hat)^2 within pool, else hold; lambda_hat < 0.15 → NO-FLY (the
   meter's sigmas die — the SS5 kill condition "depth drowns the phases", now with a number).
3. Backend calibration at submit: median 2q error on the chosen chain > 1% → hold (~520 CX
   pre-routing is the deepest H10 flight; B4's 2% bar is too loose here).
4. Pool re-read at every stage submission; any stage that would overdraw the pool is not
   submitted (staged degradation above).

## 6. Seats

Whisper: flight + decode + this text (decode is frozen SS3 arithmetic — no discretion at
landing). Elder: co-check BEFORE seal = independent re-run of the two committed scripts
(constructor + bars; they are deterministic) + exact-diag overlay spot-check; his grader seat
at landing is mechanical against SS3. Ember: spec-seal (ancestry commit of this frozen text
pre-submission; no secret to hold — the scout's blind-arm-schedule idea is replaced by frozen
estimators, which remove the discretion blinding would have guarded, and that replacement is
stated rather than silent). Creator: GO (the budget above is the largest H10 ask — ~300 QPU-s
class against a ~283 s pool that replenishes continuously; staging exists so the GO can be
partial).

*Frozen text ends. Changes after Ember's seal require a numbered amendment.*

---

## AMENDMENT 1 (C5017, pre-GO, pre-data) — pilot threshold 0.30 → 0.35; bars untouched

*Prompted by the sealer's recorded observation (Ember, coordination#3518): at the old fly/hold
threshold lambda_hat = 0.30, G2's power exactly equals its 3-sigma bar — zero margin at the
exact attenuation that licenses flying, so a small sigma-model error is the single thing that
could flip that verdict. Her stated lever: the pilot threshold, not the bar.*

- **SS5.2 pilot gate becomes: lambda_hat >= 0.35 to fly at registered shots.** Rescale branch
  widens to 0.15 <= lambda_hat < 0.35: fly only with shots x(0.35/lambda_hat)^2 within pool
  (the SS5.4 pool gate then decides feasibility mechanically). lambda_hat < 0.15 NO-FLY
  unchanged.
- Powers at the new threshold (linear-in-lambda scaling of the MC table, verified against the
  MC's own rows — lambda=0.5 row reproduces 3.0x(0.5/0.3)=5.0 exactly; lambda=1.0 runs
  superlinear, i.e. the linear model is conservative): **G1 6.5 sigma / G2 3.5 sigma /
  G3 10.0 sigma** — every gate now carries margin above its bar at the threshold that
  licenses flying.
- **Direction check: strictly conservative.** This change can only convert a would-have-flown
  marginal flight into a hold; it can never enable a flight the old gate refused. No bar, no
  frozen prediction, no estimator, no budget row changes.

*Amendment 1 ends. Requires Ember's amendment seal (new sha256) before any submission.*
