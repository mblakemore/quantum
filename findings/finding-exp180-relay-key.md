# Finding — Exp180: THE RELAY KEY — certified keys through one AND two relays; the Werner mapping falls

**Cycle**: C4867 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e15q1htsac739dm7i0`
(20 circuits: 4 arms × [4 CHSH + 1 key setting], 8000 shots). The capstone: the full network
stack (swap 162 + frame 177 + echo 178 + merged window 179) carrying its real payload — an
E91 key certified by physics through relay infrastructure nobody trusts.

## Result

| arm | S (CHSH) | σ over classical 2 | QBER | verdict |
|-----|----------|--------------------|------|---------|
| direct | 2.607 ± 0.017 | +35.8 | 1.4% | ceiling |
| **key1relay** (1 swap + stack) | **2.307 ± 0.018** | **+16.8** | **8.2%** | **CERTIFIED KEY THROUGH A RELAY** |
| **key2relay** (2 swaps, merged window + stack) | **2.235 ± 0.019** | **+12.7** | **10.6%** | **CERTIFIED — through TWO relays** |
| nomeas (falsifier) | −0.010 ± 0.022 | — | 49.9% | flat, as physics requires |

**PRIMARY HELD.** Alice and Bob's qubits never met; their entanglement was forged by relay
stations whose only role is a published Bell measurement — and the CHSH certificate (the bound
an eavesdropper cannot beat, by physics not by assumption) passes at 16.8σ with a working key
basis at 8.2% error. Ordering held; falsifier textbook (S = −0.01, key bits pure coin-flips).

**Method contribution — frame-steered sifting**: CHSH angles are non-Clifford, so relay
corrections cannot be XORed (the Exp177 fence, met head-on). Conjugation gives the exact
operational rule: pending frame (x,z) ⇒ flip the outcome by (−1)ˣ and steer Bob's effective
angle between ±π/4 by x⊕z. Every shot lands in a valid CHSH term — this IS how
entanglement-swapping QKD folds relay outcomes into sifting, derived and selftest-proven exact
(noiseless S = 2√2 recovered through both architectures).

## The out-of-band result — and the model correction it forces

key2relay was pre-registered as the model's falsification point: Werner mapping S = 2√2·p on
the plateau (F ≈ 0.77) predicted **1.97 — no violation**. Measured: **2.235, certified at 12.7σ.
The plateau pricing was too pessimistic, and the miss decomposes cleanly:**

1. **The Werner assumption is wrong for this hardware's noise** (the structural error). Our
   chains die by dephasing: ZZ ≫ XX ≈ −YY. For such states, with A ∈ {Z, X} and B at ±π/4:
   **S = √2·(⟨ZZ⟩ + ⟨XX⟩)** — not 2√2·p. Plugging Exp179's own mergedecho correlations
   (ZZ 0.787, XX 0.663) gives S = 2.05: *a violation was already predicted by our own data*,
   hidden by the Werner reduction. The ZZ surplus that dephasing leaves intact actively buys
   CHSH margin — and it is also why QBER stays low (key bits live in the Z basis, the protected
   one). **Dephasing-structured links are better QKD carriers than Werner-equivalent fidelity
   suggests.** (Exp165's lesson — witness-F understates structured states — recurring at the
   protocol layer.)
2. Conditions swung favorable (2.05 → 2.235) — the day's volatility record, this time in our
   favor; same-job ordering and falsifier keep the claims clean.

Corrected rule going forward: price CHSH from the measured correlation pair (ZZ, XX), never
from scalar F. The scalar-collapse of a structured state is the same class of error as
multiplicative layer pricing was (C4863) — the night's recurring lesson at a new level.

## Ledger (honest accounting)

- Primary HELD (16.8σ, QBER 8.2% < 11%). Ordering HELD. Falsifier HELD.
- key1relay S 2.307 ∈ band [2.10–2.40] ✓; direct 2.607 in band ✓ ; nomeas flat ✓; QBER bands
  all held (key2 10.6% ∈ [8–13%]).
- **key2relay OUT OF BAND high** — pre-registered as informative-either-way; decomposed above
  into Werner-assumption error + condition swing. Ledger prediction (logged pre-submit)
  correspondingly graded: primary right, model-point wrong for a now-understood structural
  reason.

## Fence

Raw sifted bits + CHSH certificate (Ekert security layer) — no error correction, privacy
amplification, or authenticated channel. Relay outcomes published (standard; the relay holds no
correlated qubit afterward — the witness is the proof). One die; patches, not stations. The
2.235 includes a favorable condition swing; the *certified-through-two-relays* claim rests on
the 12.7σ margin, not on the point value repeating.

## The night (seven flights)

175 tax → 176 dose → 177 decomposition → 178 cure → 179 architecture+plateau → **180: the stack
delivers its payload — certified secret bits through two untrusted relays** — plus one corrected
model (structured-noise CHSH) and one method (frame-steered sifting) banked for everything that
comes next.
