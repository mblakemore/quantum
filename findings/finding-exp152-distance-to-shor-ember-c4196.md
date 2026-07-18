# Exp152 — The distance from the Shor kernel to Shor, priced in gates (Ember, C4196)

**Question (frontier-doc Q5):** Exp150 (C4195) flew the Shor *back-end* — QPE + inverse QFT +
continued fractions — on `ibm_kingston` to t=5 / depth-230, recovering hidden periods including
the non-divisor (real-Shor) regime. **How far is that from the full algorithm?** This finding
prices the whole staircase in CZ gates and states the gap against the measured ~800–1000-CZ wall.

**Tier:** resource ESTIMATE (transparent gate accounting), not a hardware flight. 0 QPU. The
value is the order-of-magnitude gap, which is robust to the coefficient choice.

## Method

A bottom-up count where every coefficient is a stated feature of a named construction (Cuccaro
ripple-carry adder + Beauregard-style controlled modular multiply-accumulate exponentiation),
reported as two columns — an aggressive lower bound and a textbook count — with two Toffoli→CZ
decompositions (relative-phase 3 CZ / standard 6 CZ). Modular exponentiation on an n-bit modulus
costs ≈ `coeff·n³` Toffoli (coeff 8 aggressive / 16 textbook); the terminal inverse QFT over the
2n-qubit counting register costs ≈ `(2n choose 2)` CZ. Tool + data:
`experiments/exp152_distance_to_shor_pricer_ember.py` · `results/exp152_distance_to_shor.json`.

## Result

| N | n | Aggressive-LB total CZ | Textbook total CZ | × the wall | QFT back-end share | Predictor at that depth |
|---|---|---|---|---|---|---|
| **15** | 4 | **1,564** | **6,172** | **1.6× – 7.7×** | 0.5–1.8 % | p_true = 0.5, reps → ∞ (drowned) |
| 21 | 5 | 3,045 | 12,045 | 3.0× – 15.1× | 0.4–1.5 % | p_true = 0.5, drowned |
| 35 | 6 | 5,250 | 20,802 | 5.2× – 26× | 0.3–1.3 % | p_true = 0.5, drowned |

## The headline number

**The smallest textbook Shor (N = 15) costs 1,564–6,172 CZ — between 1.6× (optimistic) and 7.7×
(textbook) past the ~1000-CZ wall.** The QFT back-end that Exp150 actually flew is only ~0.5–1.8 %
of the circuit; the missing ~98 %+ is the **modular-exponentiation front-end**, and that is the
entire distance. Run through the campaign's own survival predictor (generic-decay depolarizing
model, `E_CX = 0.0106`), the period signal's bias margin collapses to zero far below the modexp
depth: `p_true` pins at 0.5, `reps_needed → ∞`. No rep budget recovers a signal that has decayed
into the noise floor.

## Interpretation

Exp150 was not "almost Shor." It flew the cheap ~1–2 % tail of the algorithm — the part that was
always going to be easy on NISQ because it is shallow. The 98 % that makes Shor *Shor* — reversibly
computing `aˣ mod N` under superposition — is one to two orders of magnitude of CZ beyond where
this hardware generation preserves any signal at all. **The gap is not a tuning problem; it is the
~1000-CZ wall (F05/Exp33) standing bodily between the kernel and the algorithm.** This is the same
lesson the campaign keeps measuring from new angles: the walls are where the interesting boundary
is, and they are made of depth, not cleverness.

## Fence

Prices the gate-distance to factoring **toy N**. This does **not** factor RSA (needs n≈2048, ~10⁸+
CZ fault-tolerant), it is **not** fault-tolerant, and a "compiled Shor" that hard-codes the known
factors into a handful of gates (Vandersypen-style) is **excluded by construction** — that is the
cloning-cheat pattern (F110): it beats the count only by already knowing the answer it claims to
compute. The predictor arm is generic-decay-scoped (G1): it certifies the signal *drowns*, which is
sufficient here — a coherent inversion could only make recovery worse, never rescue it.

**Numbering note:** the analysis is docs/estimate-tier; per the C4154 defer-to-silicon rule it does
**not** earn an F-number. It is the Q5 deliverable of the frontier doc and the pricing companion to
Exp150's F-track flight.
