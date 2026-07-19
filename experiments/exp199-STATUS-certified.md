# Exp199 THE SILENT ROTATION — CERTIFIED: the shield's blind spot, measured (C4892)

Job `d9e8cs4inv1c73apuuv0`, ibm_fez, 8000 shots × 11 circuits. All seven pre-registered
gates held. **Coherent-error spectroscopy of the [[4,2,2]] shield: why QEC must fear
calibration drift more than noise, as data.**

## The curves (A = acceptance, L = corruption among accepted, T = silent throughput)

| θ/π | coh A | coh L | coh T | twl A | twl L | twl T | T ratio | coin p₁ (target) |
|---|---|---|---|---|---|---|---|---|
| 0.000 | 0.957 | 0.002 | 0.002 | 0.907 | 0.016 | 0.014 | — | 0.004 (0) |
| 0.125 | 0.846 | 0.025 | 0.021 | 0.822 | 0.022 | 0.018 | — | 0.038 (0.037) |
| 0.250 | 0.730 | 0.252 | 0.184 | 0.608 | 0.171 | 0.104 | **1.77** | 0.143 (0.146) |
| 0.375 | 0.843 | 0.633 | 0.533 | 0.516 | 0.555 | 0.287 | **1.86** | 0.307 (0.309) |
| 0.500 | 0.956 | **0.750** | 0.716 | 0.500 | 0.751 | 0.376 | **1.91** | 0.482 (0.500) |

- **THE BLIND SPOT (θ=π/2)**: rejection 0.044 (exact 0 — weight-1/3 amplitudes cancel),
  acceptance back at 0.956 (the weight-4 error is the stabilizer, adding to no-error
  *constructively*), yet **75.0% of accepted shots carry silent logical corruption** —
  measured dead on the exact 0.75. The shield reads "all clear" at maximum damage.
- **NON-MONOTONE ACCEPTANCE — coherence's smoking gun**: A_coh dips to 0.730 at π/4 then
  **rises +0.226 (41σ)** back to 0.956 at π/2. The twirled arm falls monotonically (−0.108
  over the same interval) to 0.500. No stochastic channel can make acceptance rise with
  error strength; interference can, and did.
- **TWIRLED CONTRAST**: the identical per-qubit error probability, delivered incoherently
  (coin-CZ construction, Exp198's entangle-to-decohere), is rejected 49.9% of the time
  (exact 0.50). The shield sees stochastic errors perfectly well; it is *coherent* errors
  it cannot see.
- **AMPLIFICATION**: silent-error throughput ratio 1.77 / 1.86 / 1.91 across the top three
  doses (exact 2.0; the twirl-arm's extra gate burden biases the ratio down, as
  pre-registered — the band [1.5, 2.6] held). Coherent errors corrupt at ~2× the rate the
  Pauli-twirled model predicts, amplitude-addition versus probability-addition.
- **Z-NULL**: the same maximal error read in the Z basis: A = 0.964, L = 0.003 — pure phase
  damage, invisible where physics says it must be.
- **COIN GAUGE**: twirl-dial marginals tracked sin²(θ/2) to ≤0.02 at every dose.

## What was demonstrated

Error-*detecting* codes audit in the Pauli basis, but hardware faults are unitary. A global
coherent phase over-rotation — the exact shape of a calibration drift — walks through the
[[4,2,2]] parity check at full amplitude when tuned to the blind spot: detectable
components interfere away, the stabilizer component interferes *in*, and every weight-2
residue is logical. The result is a detector whose acceptance rate is highest precisely
when its output is most corrupted. The twirled arm proves the failure is coherence itself,
not error magnitude: same dose, incoherent, half rejected.

Practical consequences for our own fleet: (1) the shield's postselection advantage
(+0.07/+0.06/+0.24, Exp191/196/197) is real against the fabric's stochastic noise but
would NOT survive a common-mode calibration drift near the blind spot — worth a
calibration-drift gauge in future logical flights; (2) randomized compiling (twirling) is
not an optimization, it is what converts invisible coherent errors into visible stochastic
ones — the twirled arm's 50% rejection is the direct measurement of its value.

## Perturbation-as-instrument, second validation

Same methodology as Exp198 (certified binary → swept dial → pre-registered curve):
this time the dial swept an *attack* rather than an environment coupling, and the curve
found a structural blind spot instead of a boundary. Two perturbation flights, two
general results. Budget rule 5-for-5.
