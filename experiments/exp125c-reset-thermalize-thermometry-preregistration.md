# Exp125c — CERTIFYING THE FRONTIER: reset-thermalize thermometry of q4 (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4665. Goal: certify (or bound) the F105 erasure-accessibility frontier by
measuring q4's effective temperature p_eq with an estimator that separates thermal population from readout —
the F105 straddle's named bottleneck. **ef-transition thermometry is BOUNDARY-BLOCKED** on ibm_marrakesh
(`open_pulse: False`, basis {cz,id,rz,sx,x}; reaching |2⟩ needs an ef π-pulse) — so the standard instrument
is unavailable, and this is the gate-model substitute via `dynamic_circuits` (reset+delay+measure).
**Status**: FROZEN at commit. Advisor-audited (C4665): reset-thermalize chosen over QND-repeat (below).

## Why reset-thermalize, not QND-repeat (advisor C4665)

We must resolve p_eq ≈ 0.4%, which sits *below* both q4's readout error (0.7%) and the scale of
**measurement-induced excitation** (~0.1–1% on transmons). QND-repeat would read measurement-induced 1→1
correlations AS thermal population → biases p_eq **up** → a **false ACCESSIBLE** (the very artifact ef-Rabi
exists to dodge). Reset-thermalize is robust: in `ΔP = P(1|t→∞) − P(1|t≈0)`, the per-readout terms
(readout-0→1 *and* measurement-induced excitation) are t-independent and **cancel**; only thermal
equilibration survives. Disclosed residual: cancellation assumes measurement-induced excitation is
~state-independent to first order.

## The estimator (frozen) and its conservative direction

Reset q4 → |0⟩, idle a ladder of delays t, measure P(1|t). From a cold start the population rises to
equilibrium: `P(1|t) = a + d·[p_eq + (rst − p_eq)·e^(−t/T1)]`, a = readout-0→1 + meas-induced excitation,
d = 1−a−b, rst = reset-residual excited, T1(q4)=118 µs. Since `P(1|t≈0) = a + d·rst ≥ a` (rst ≥ 0),

  **ΔP = P(1|t_max) − P(1|t_min) = d·(p_eq − rst) ≤ d·p_eq**

is **always a conservative LOWER bound on d·p_eq**, regardless of reset temperature or whether t_max reaches
equilibrium. Under-estimation only makes the floor smaller → the ACCESSIBLE verdict harder → a PASS is robust.
p_eq_lower = ΔP / (1 − e^(−t_max/T1)) [the exp factor 0.993 at 5·T1 un-does the incomplete-rise, still
conservative in rst]; `floor_lower = ln2/ln((1−p_eq_lower)/p_eq_lower)` [E units, = Exp125 formula].

## Flight (one job; QPU 🟢)

q4 (= F104/F105 record qubit). Pubs, 40000 shots each:
- **5 thermalize pubs**: reset + delay(t) + measure, t ∈ {0.1, 40, 120, 360, 590} µs ≈ {0, ⅓, 1, 3, 5}·T1.
- **1 readout-ref pub**: X + measure (immediate) → b̂ = P(0|prep1), gives d = 1−a−b (a = P(1|t=0.1µs)).
Full ladder fits `P(1|t)=P0+A(1−e^(−t/T1))` (T1 free) to confirm the rise is thermalization (τ≈118 µs), not
an artifact; A is the readout-cancelled thermal amplitude, cross-check on ΔP.

## Grade (frozen)

- **G-therm (at-risk HEADLINE):** `ΔP − 5·SE(ΔP) > 0` → q4's thermal population RESOLVED above zero →
  certifies a positive Landauer floor lower-bound → re-grade the F105 frontier. `SE(ΔP)=√(SEmax²+SEmin²)`.
- **If G-therm PASS → re-grade F105 frontier (certification):** bonus_lower = (|S(B|A)|−5·0.020)·floor_lower,
  |S(B|A)|=0.855 (F105 banked). `bonus_lower − 0.028 − 5·SE_b > 0` → **COHERENT-ACCESSIBLE CERTIFIED**
  (the F105 straddle resolved). Report vs classical 0.092 too.
- **If G-therm FAIL (ΔP ⊄ >0 at 5σ) → THE META-FINDING (pre-registered as expected/acceptable):** a THIRD
  independent axis — after F104 (credit-SE) and F105 (tomographic-SPAM) — agrees the erasure effect lies
  **below NISQ's certification floor**. Per the frozen ceiling (advisor C4665): **this is the finding; STOP
  — no Exp125d.** Three axes converging is a stronger closing than a fourth refinement.

## Caveat on the tax (advisor C4665)

F97's tax (0.028 coherent / 0.092 classical) is a QET-feedforward *decoherence* scale used as a **proxy** for
the cost of cashing the erasure bonus, NOT a measured erasure work. A PASS means "bonus exceeds a
representative feedforward scale," not "net work extracted." Stated in any ACCESSIBLE verdict.

## Predictions (Whisper C4665)

| Pre-filed | Conf | |
|---|---|---|
| G-therm resolves ΔP>0 at 5σ (reset colder than p_eq, thermal visible) | 0.50 | genuinely at-risk: reset residual may ≈ p_eq |
| Ladder fit τ consistent with T1≈118 µs (rise IS thermalization) | 0.70 | if ΔP>0 at all |
| **If resolved: coherent-frontier CERTIFIED ACCESSIBLE** | 0.60 | bonus ~0.107 ≫ coherent tax 0.028 |
| classical-frontier stays STRADDLE/inaccessible | 0.55 | bonus ~0.107 vs 0.092, marginal |

Cost: one job, longest-idle ~590 µs × 40k shots (6 pubs). Bound graded: q4 effective temperature (frontier certification).
