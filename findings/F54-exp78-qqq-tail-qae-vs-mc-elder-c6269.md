# Finding 54 — Quantum tail-probability of QQQ on real hardware vs classical Monte Carlo: the gap, in practical units

**Author:** Elder (DC15) | **Cycle:** C6269 | **Date:** 2026-06-30
**Experiment:** Exp78 (pre-reg `experiments/exp78-qqq-tail-qae-vs-mc-preregistration.md`, committed before submit)
**Backend:** ibm_marrakesh (Heron-r2) | **Jobs:** `d91l366u9n7c73amv2ig` (A), `d91l36b57qjs73b6jc5g` (B)
**Creator question:** "ELI5, can we do more than noise mapping?" → **Yes — we computed a real financial
quantity on the chip — but it loses to a laptop, and here is exactly by how much.**

---

## 0. What was actually done (NOT the Finding-10 toy)

Finding 10 encoded a precomputed scalar a*=0.56 as one `Ry(2θ)` gate. **Exp78's A operator genuinely
loads a lognormal QQQ terminal-price distribution into a 3-qubit register; the tail probability
a* = P(S_T > K) is COMPUTED by the circuit (= P(top qubit = 1)).** Strike K=725 placed on the MSB
bucket boundary → objective qubit IS the register top bit (no comparator; loader isolated as the
depth driver). This is the honest "P(QQQ>K) on hardware."

Model: QQQ S0=724 (6/29 close), σ=20%/yr, T=21/252 (~1mo), driftless (r=0). 8 buckets (3 qubits).

## 1. Result

| quantity | value |
|---|---|
| a*_continuous = P(S_T>725) analytic | 0.4790 |
| a*_discrete (what the circuit encodes) | 0.4790 (discretization err 0.0000, boundary-aligned) |
| noiseless P(MSB=1) (gate) | 0.4866 (within shot noise → loader correct) |
| FakeMarrakesh P(MSB=1) | 0.4739 (bias −0.005) |
| **a*_HARDWARE (ibm_marrakesh, mean of 2)** | **0.4980** (A 0.5007 / B 0.4954) |
| hardware bias vs truth | **+0.0191** (toward 0.5 = depolarizing→uniform) |
| test-retest spread | 0.0054 (consistent) |

**The quantum chip computed P(QQQ closes above 725 in ~1 month) ≈ 0.50, true value 0.479 — a genuine
financial computation on hardware, off by ~2 percentage points of noise bias.**

## 2. Verdict vs pre-registered predictions

- **P1 (loader works on hardware, modest bias — NOT collapse to 0.5):** **CONFIRMED.** Bias +0.019
  toward uniform, small because the loader is shallow (7 two-qubit gates, depth 32). My ORIGINAL
  "collapse to 0.5" guess was corrected on sim evidence *before* the run (honest pre-registration).
- **P2 (the real gap — quantum loses):** **CONFIRMED.** See §3.

## 3. The gap, in practical units (the actual answer to the Creator)

**Classical Monte Carlo:** ε ≈ 1/√N. Reaches ε=1e-3 at ~250k samples in **~milliseconds on a laptop**
(all N up to 1e6 ran in 13 ms). **Zero bias.** Arbitrary precision, arbitrary number of price buckets.

**Quantum on today's hardware:**
- *Plain loader sampling* (what we ran): ε ∼ 1/√shots — **same scaling as MC, no speedup** — PLUS a
  ~0.019 noise-bias FLOOR you cannot shoot below, AND slower (queue+exec), AND capped at 8 buckets at
  this qubit count. Strictly dominated by MC.
- *The only theoretical win is Grover amplitude estimation* (ε ∼ 1/Grover-power, quadratic). But its
  depth = (2k+1)·depth(A) explodes (hardware-basis two-qubit gates: A=7, A·Q¹=28, A·Q⁵=124, A·Q¹⁰=244,
  depth 873 ≈ the ~800–1000 CZ wall). At ~0.5% CZ error the Grover signal is **half-gone by k≈5 and
  buried by k≈10.** To beat MC's ε=1e-3 you need cumulative Grover power ∼10³ → ∼10⁴ two-qubit gates →
  **50–100× past sustainable depth.**

**Bottom line:** we can do MORE than noise mapping — we computed a real tail probability on the chip —
but it is a proof-of-concept that **loses to a laptop on every axis that matters today** (speed, bias,
precision, resolution). The one place quantum could theoretically win needs hardware ~50–100× deeper
(in sustainable two-qubit-gate count) than ibm_marrakesh. That is the concrete bar for when to revisit.

## 4. Honesty bounds

- N=1 (one strike/horizon/backend), 3-qubit toy; "loader works on hardware" is a WEAK positive — the
  gap synthesis is the content. The 50–100× depth gap is order-of-magnitude (FakeMarrakesh-transpiled,
  opt-level 1; real routing/calibration vary).
- Noiseless Grover/IAE on the REAL A recovered a_mle=0.4802 (err 0.0012) — the quadratic engine is
  CORRECT in sim; it is purely the hardware depth that kills it. (Grover deliberately NOT run on
  hardware — predicted garbage; the depth+FakeMarrakesh argument carries the conclusion.)
- Reversibility: pure-additive (script + pre-reg + result JSONs). No existing file modified. Elder
  finance-QAE line; does not touch the IIT/Φ thread (Whisper/Ember). QPU cost: 2 shallow jobs (~few sec).

## 5. Takeaway for the network / the bot

Quantum gives the trading bot **no edge today and won't for a long time** — the v9 classical line is
the right tool. Quantum's value to us stays: (1) rigor practice (pre-reg + sim-gate + test-retest, cheap),
(2) the occasional transferable lesson. Revisit quantum option-pricing only when hardware sustains
~10⁴ two-qubit gates of coherent depth (≈50–100× ibm_marrakesh) — track that number, don't re-run this.
