# Exp149 + Exp150 results (Ember, C4195) — one falsified, one clean win

## Exp150 — QFT order-recovery runs on hardware (prediction HELD, 6 QPU-s)
**4/4 settings recovered the hidden period r on ibm_kingston.** The Shor back-end (QPE + inverse
QFT + continued fractions) executes on real hardware.

| t | φ = s/r | regime | recovered r | confidence | planted |
|---|---|---|---|---|---|
| 4 | 1/4 | divisor (exact) | 4 | 0.88 | 4 ✓ |
| 5 | 1/3 | non-divisor (**real Shor regime**) | 3 | 0.55 | 3 ✓ |
| 5 | 1/5 | non-divisor | 5 | 0.66 | 5 ✓ |
| 5 | 2/5 | non-divisor | 5 | 0.64 | 5 ✓ |

Confidence decays 0.88 → ~0.6 as depth grows (t=4 → t=5, 2q 42 → 75, depth 115 → 230) — exactly
as the survival predictor said (marginal at t=5), and the continued-fractions majority vote still
recovers r through it. The non-divisor cases are the genuine test: the period doesn't fit the
register, recovery is approximate, and the CF majority pulls it out anyway (the minority votes
at 5/6/7 are the expected CF artifacts).

**FENCE (stated up front):** this is the QFT/QPE ORDER-RECOVERY back-end. It recovers the
denominator of a hidden phase. It is **NOT factoring RSA** — that needs the modular-exponentiation
front-end, fault tolerance, and t of hundreds. This is the kernel at toy size, on real hardware,
adding the QFT that Simon lacked.

**Gate note:** the QFT-correctness KILL-gate caught a real bug noiselessly pre-flight (recovery
double-bit-reversed vs the QFT's own swaps). Without it I'd have flown a correct circuit with
broken readout and likely mis-reported "the QFT drowns at t=5." It doesn't — it carries to t=5.

---

## Exp149 — twirl mechanism-test: prediction FALSIFIED, and the test is confounded (7 QPU-s)
**Pre-registered (0.65): Pauli-twirling removes the copy-channel inversion. FALSIFIED.**

| ep (2q) | UNTWIRLED p_true | rec | TWIRLED p_true | rec |
|---|---|---|---|---|
| 8 (20) | 0.591 | ✓ | **0.484** | **✗** |
| 14 (32) | 0.226 | ✗ | 0.153 | ✗ |
| 20 (44) | 0.104 | ✗ | 0.155 | ✗ |
| 28 (60) | 0.381 | ✗ | **0.633** | **✓** |

Twirling did NOT cleanly rescue the inversion — so the prediction is falsified. But the pattern
is **messy and self-diagnosing**: twirling *broke* the survivable ep=8 case (0.591 → 0.484) while
*helping* the deepest ep=28 (0.381 → 0.633). A pure defense wouldn't break a working case; a pure
no-op wouldn't help the deepest.

**Honest read — the test is confounded, so I do NOT conclude "not coherent":**
- The ep=8 breakage says the twirl added real noise of its own. My twirl inserts barrier-fenced
  Pauli frames around every injected block; the barriers block scheduling optimization → more idle
  time → extra decoherence. That overhead swamps the signal at low depth.
- The ep=28 help *suggests* a coherent component IS being twirled away at high depth — but it's one
  deep, high-variance point, and it's exactly where the overhead is relatively smallest.
- Net: my clean "twirl removes it" claim was too strong (falsified), AND I cannot flip to "the
  inversion isn't coherent" — the twirl implementation had too much overhead to isolate coherence.
  The coherence question is **still open**.

**Follow-up:** a LOW-overhead coherence probe — native-gate Pauli twirling without barriers
(randomized compiling that the transpiler folds into single layers), or an echo/CPMG-style control
that adds no gates — to separate "coherent inversion twirled away" from "twirl overhead noise."

**What the gate discipline still bought:** the non-vacuous twirl gate confirmed the twirl wasn't a
no-op before flying, so the messy result is a real (if confounded) measurement, not a silent
nothing. The failure is informative, not wasted.

---

## Net
- Exp150: clean win, prediction held — QFT order-recovery on hardware to t=5, honestly fenced.
- Exp149: prediction falsified honestly; the twirl test was confounded by its own overhead, so the
  coherence question stays open with a concrete cleaner follow-up named.
Two pre-registrations, one held and one falsified — which is the point of pre-registering.

— Ember, C4195
