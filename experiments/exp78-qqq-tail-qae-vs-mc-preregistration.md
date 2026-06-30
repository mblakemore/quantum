# Exp78 Pre-Registration — Quantum tail-prob of QQQ vs classical Monte Carlo: measuring the gap

**Author:** Elder (DC15) | **Cycle:** C6269 | **Date:** 2026-06-30
**Status:** PRE-REGISTERED (committed before hardware submission)
**Script:** `scripts/qae_qqq_tail_demo.py` | **Backend:** ibm_marrakesh (Heron-r2) | **Sim gate:** FakeMarrakesh
**Creator ask:** "ELI5, can we do more than noise mapping?" → build a real P(QQQ>K) demo, benchmark vs MC,
measure the gap. **This is a proof-of-concept measuring the gap; it is NOT an edge.**

---

## 0. What this is (and is NOT the Finding-10 toy)

Finding 10 encoded a **precomputed** scalar a*=0.56 as one `Ry(2θ)` gate and re-estimated it — the
distribution-loading was classical. **Exp78's A operator genuinely loads a lognormal QQQ terminal-price
distribution into a 3-qubit register; the tail prob a* = P(S_T > K) is COMPUTED by the circuit** (= P(top
bit = 1)). That is the honest "P(QQQ>K) on hardware."

## 1. Design (advisor-gated C6269)

- Lognormal QQQ terminal: S0=724 (6/29 close), σ=20%/yr, T=21/252 (~1mo), driftless (r=0, E[S_T]=S0).
- 8-bucket (3-qubit) linear price grid; **MSB bucket boundary == strike K=725 (ATM-ish)** → the
  in-the-money set {S_T>K} ≡ {index≥4} ≡ {MSB=1}. **The objective qubit is just the register's top bit
  — no comparator** (isolates the distribution LOADER as the real depth driver; zero comparator bug-surface).
- **Gate 1 (discretization):** validate against a*_DISCRETE = Σ bucket-probs above K, not continuous Φ(−d2).
  Report |a*_discrete − a*_continuous| separately.
- **Gate 2 (sim go/no-go, F53 discipline):** noiseless P(MSB=1) must match a*_discrete within shot noise
  before any hardware spend.
- Grover Q = A·S0·A†·S_χ + IAE-MLE kept **NOISELESS-SIM ONLY** (bonus; do NOT run a Q^k ladder on hardware).

## 2. Recorded sim results (pre-submit, C6269)

- a*_continuous = **0.4790**; a*_discrete = **0.4790**; discretization err **0.0000** (boundary aligned to strike).
- **Gate 2 PASS:** noiseless P(MSB=1) = 0.4866 vs 0.4790 (|d|=0.0076 ≤ 4·shot_se=0.0312). Loader correct.
- FakeMarrakesh preview: P(MSB=1) = 0.4739 (bias only **−0.0051**); loader transpiled depth 32, 7 two-qubit gates.
- Classical MC: ε=1e-3 needs ~250k samples, **~ms on a laptop** (all N up to 1e6 in 13 ms).
- Bonus noiseless Grover/IAE on the REAL A: a_mle=0.4802 vs 0.4790 (err 0.0012) — quadratic engine works noiselessly.
- **Hardware-basis depth ladder (FakeMarrakesh transpile):**
  | circuit | Grover power | hw depth | 2-qubit gates |
  |---|---|---|---|
  | A (loader) | 1× | 32 | 7 |
  | A·Q¹ | 3× | 112 | 28 |
  | A·Q² | 5× | 201 | 52 |
  | A·Q³ | 7× | 283 | 76 |
  | A·Q⁵ | 11× | 451 | 124 |
  | A·Q¹⁰ | 21× | 873 | 244 |

## 3. Pre-registered predictions (corrected by the sim evidence above — committed before hardware)

- **P1 (loader on hardware):** the loader is SHALLOW (7 two-qubit gates) → it will NOT fully decohere; predict
  a*_hardware **close** to a*_discrete, |bias| ≲ ~0.05 (NOT the "collapse to 0.5" I first assumed — that was
  for a deep circuit; corrected here on sim evidence, honestly, before the run).
- **P2 (the real gap):** quantum *sampling* of the loaded distribution has **NO speedup** over classical MC
  (both ε∼1/√shots). The quadratic speedup lives ONLY in Grover amplitude estimation, whose depth =
  (2k+1)·depth(A) blows past the ~800–1000 CZ wall: signal half-gone by ~k=5 (124 CZ ≈ 54% fidelity at
  ~0.5% CZ error), buried by k≈10. To beat MC's ε=1e-3 needs cumulative Grover power ∼10³ → ∼10⁴ two-qubit
  gates → **50–100× past sustainable depth.**
- **Headline (pre-committed): quantum LOSES today.** MC reaches ε=1e-3 in ms on a laptop, arbitrary precision,
  arbitrary #buckets. Hardware QAE floors at ε∼0.05 and is capped at 8 buckets at this depth. The honest
  deliverable is the **gap in practical units**, not a quantum win.

## 4. Honesty bounds

- N=1 instance (one strike, one horizon, one backend), 3-qubit toy. "Loader works on hardware" is a WEAK
  positive; the gap synthesis is the real content.
- The depth ladder is FakeMarrakesh-transpiled (hardware basis, opt-level 1); real depth varies with routing
  and daily calibration. The 50–100× gap is order-of-magnitude, not a precise constant.
- Reversibility: pure-additive (one script + this pre-reg + result JSONs). No existing file modified. Elder
  finance-QAE line; does not touch the IIT/Φ thread (Whisper/Ember).
