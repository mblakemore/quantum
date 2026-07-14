# Adversarial Audit — F108 "Navigator's Sextant" GHZ Heisenberg Metrology (168σ)

**Auditor**: Whisper C4716 (4th Creator-directed adversarial run: F117 → F82 → F113 → **F108**)
**Target**: F108 / Exp129 — GHZ phase probe carries R = 2.848× the executed separable-reference
Fisher information (168σ); F_GHZ = 8.293 beats *perfect* separable probes (239.5σ); k=3
super-resolution fringe (122.9×). `ibm_marrakesh`, job `d9ale3jv6alc73crvd30`.
**Verdict in one line**: **WIN is CLEAN — no evidentiary flaw. This is the first of the four runs
where the number, the grade, and the resource accounting all survive.** The distinct failure class
is of a *different kind* from runs 1–3: not a defect in the σ, but a **front-door framing
over-reach** — two textbook deployment caveats (super-resolution ambiguity; dephasing-cancellation)
that separate a correctly-measured *local* Fisher-information advantage from "the advantage the
sensing industry actually buys."

---

## Why this run is shaped differently from the first three

| Run | Target | Failure class | Bit the *number*? |
|---|---|---|---|
| C4713 | F117 randomness cert | **Wrong uncertainty** — a +0.006 pipeline bias invisible to the bootstrap | YES (σ too tight) |
| C4714 | F82 causal game 216.8σ | **Precision ≠ significance** — correct shot-noise σ answering a narrower question than the headline | YES (σ mis-read) |
| C4715 | F113 computational bridge | **Theorem-carried, strawman null** — 438σ over random guessing, not over the real NC⁰ competitor | YES (wrong benchmark) |
| **C4716** | **F108 metrology 168σ** | **Front-door framing imports a global claim** — the *local* Fisher advantage is measured correctly; two deployment bridges are under-stated | **NO** |

I checked for a number-level flaw first, because that is where runs 1–3 lived. There isn't one:

- **The arithmetic reproduces.** R = 9V₃²/3V₁² = 3(V₃/V₁)² = 3·(0.9599/0.9853)² = 3·0.9491 =
  **2.847** ✓. W2: 9V₃² = 9·0.9599² = 8.293 > 3 ✓; V₃ = 0.9599 > 1/√3 = 0.5774 ✓.
- **The resource accounting is fair.** Both arms use 3 physical qubits, one interrogation, the same
  shot budget, the same window. The GHZ arm decodes to one center readout (H·CX·CX | Rz(φ)⊗3 |
  CX·CX·H, 4 CX); the SEP arm reads all three (zero 2q gates). Per-shot Fisher info at equal
  resources — this is the correct fixed-resource comparison for N=3, not a hidden per-qubit vs
  per-register mismatch.
- **The classical arm is a genuine competitor, not a strawman.** The executed SEP arm ran at
  F_sep = 2.912 of 3.0, V₁ = 0.9853 — essentially perfect classical performance. Unlike F113's
  W1 (438σ over *random guessing*), the reference here is the *best separable strategy having its
  best day*. The F113 failure class (no real competitor benchmarked) explicitly does **not** recur.
- **The confirmation observable is real.** The free-frequency DFT peaks at k=3 (122.9× any other
  harmonic). The GHZ fringe genuinely oscillates at 3× the drive. This is not fakeable by a trivial
  mechanism.

So the honest headline: **F108's 168σ is a correctly-computed, fairly-referenced, N=3
local-Fisher-information advantage. I do not downgrade it.** (Doing so would be the inverse
over-claim the advisor caught me pre-committing to on F82 and F113 — here the symmetric trap is the
*forward* over-claim: inflating a framing critique to match a "gotcha" cadence. I am declining it.)

---

## The actual finding: the front door imports a global claim the local number doesn't carry

The **finding's own scope section is largely honest** — it says "not a sub-shot-noise interferometer
deployment," cites Bollinger 1996 as prior art, and registers the N-ladder as open with the F85
caveat. The over-reach is concentrated in the **README front-door prose**:

> "…metrology at the Heisenberg limit (168σ …)" · "**the advantage the sensing industry actually
> buys**" · "The classical player got its best possible day and **still lost**."

"Fisher-information advantage" is standard, technically-correct language — but a reader hears "this
probe **measures a phase** 2.85× better," i.e. a deployment-grade estimation contest. Two textbook
bridges stand between the measured local number and that deployment reading, and **both are exactly
where GHZ metrology is known to erode**. Neither is in the front door.

### Caveat 1 — Local Fisher ≠ global phase estimation (Higgins et al., Nature 450, 393, 2007)

The Cramér–Rao bound is a **local** statement: it lower-bounds the variance of an *unbiased*
estimator *near a known operating point*. Exp129 measures V₃ by scanning φ over a **known** 12-point
grid — which is legitimate for certifying the Fisher *ratio*, but sidesteps the problem a real
navigator has: **the GHZ fringe at 3φ is 3-fold ambiguous.** A single GHZ readout cannot distinguish
φ from φ + 2π/3. Resolving the absolute phase over [0, 2π) needs either prior knowledge that φ sits
in a 2π/3 window, or a **cascaded/adaptive protocol** (Higgins) that re-spends part of the separable
overhead.

The elegant part: **the k=3 super-resolution law the finding celebrates as "the law the ratio can't
fake" is the *same feature* that creates the 3-fold ambiguity.** The confirmation observable and the
deployment limitation are one and the same physics. This does **not** self-defeat the result —
super-resolution ambiguity is textbook and resolvable — but it is precisely why "measures a phase
2.85× better" overshoots "carries 2.85× the *local* Fisher information."

### Caveat 2 — Huelga–Plenio bites the *framing*, not the N=3 number (PRL 79, 3865, 1997)

HP is the famous result that under Markovian dephasing, the N² GHZ Fisher gain is **cancelled** by
the N-fold-faster dephasing of the GHZ state, once interrogation time is optimized — the
entanglement advantage collapses to a constant factor, not scaling.

**Scope discipline (advisor-checked): HP does _not_ bite F108's N=3 result.** HP is about
*frequency* estimation with *time-optimized interrogation*; F108 measures *phase* at *fixed*
interrogation. At fixed interrogation and N=3 the advantage genuinely survives (V₃ = 0.96 says the
dephasing over the short 4-CX prep is small). **HP bites the phrase "the advantage the sensing
industry actually buys"** — because frequency standards are the canonical sensing-industry
application, and they are run with time-optimized interrogation, which is HP's exact domain. And the
premise is not hypothetical here: **this campaign's own F111 ("cloaking device") measured IBM's
dephasing structure** (dominantly memoryless with a real ~10–15% correlated tail) — the noise HP
requires is the noise Whisper already characterized on this hardware.

---

## What the fix is

Not a re-grade — the gates stand. **Front-door surgery only:**

1. Dial back "the advantage the sensing industry actually buys" → the honest version is
   "a certified N=3 *local* Fisher-information advantage; the deployment version (frequency
   standards, unambiguous absolute phase) carries two further caveats."
2. Add the **ambiguity** line: the k=3 super-resolution that certifies the win is also a 3-fold
   phase ambiguity; absolute-phase deployment needs a cascade (Higgins 2007).
3. Add the **HP boundary** line: at fixed interrogation N=3 the advantage is real; under
   time-optimized interrogation with dephasing (the F111-measured regime) the *scaling* advantage
   is HP-limited — sharpening the finding's existing "F85 depth wall" caveat with the metrology
   theorem that actually names the mechanism.

---

## Bottom line

**F108 is a clean win.** No wrong uncertainty (unlike F117), no precision-vs-significance conflation
in the σ (unlike F82), no strawman benchmark (unlike F113). The number is right, the reference is
fair, the resource accounting is honest, and the finding's scope section mostly says so already.

The distinct-failure-class contribution of this 4th run is therefore a **null-ish** one, reported as
such: **the marquee prose is where the over-reach lives, and it is a milder, framing-level over-reach
than any of the prior three.** Two textbook caveats — super-resolution ambiguity and
HP-under-dephasing — belong in the front door beside the 168σ, because they are exactly the two
bridges the phrase "the advantage industry buys" invites a reader to walk without a toll. The WIN
stands as an N=3 local-Fisher existence result; I neither downgrade it nor inflate the critique.

*Audit method: reproduced R and W2 arithmetic; read the frozen pre-registration to confirm the
φ-grid is known (ambiguity sidestepped by design, not by claim); pinned each caveat to the framing
rather than the number; advisor consult confirmed the HP domain boundary (phase-fixed-interrogation
vs frequency-time-optimized) and flagged the forward-over-claim risk this run uniquely carries.*
