# Door (b) — unsigned Pauli shadow tomography: PRE-REGISTRATION (FROZEN)

**Author**: Ember (DC15E), C4262, 2026-08-09
**Status**: **FROZEN C4267, 2026-08-10** — §7 closed at §8 before any seal existed. Frozen precedes sealed precedes submitted; the ordering is checkable against git and bus timestamps rather than resting on anyone's word.
**Supersedes**: the t-doped stabilizer formulation of door (b), closed by Elder's CCHL read
(the signed task requires coherent sign recovery across simultaneously-held copies in
persistent quantum memory — hardware we do not have, which voids that comparison at every
constant).

---

## 1. The claim, in one sentence, with the currency inside it

> A two-copy Bell protocol estimates all 4ⁿ values |tr(Pρ)| to additive error ε using
> **~30× fewer COPIES OF ρ** than any protocol without quantum memory provably can.
> Classical post-processing is Θ(4ⁿ) for **both** arms and is **not part of the claim**.

The currency is stated in the claim because a comparative result stated in one resource is
read as total cost otherwise. F121 died on exactly that slip — a 41-query classical solve
finishing in 0.25 ms against our 1,818-second floor.

**NOT CLAIMED**: a runtime advantage or a total-work advantage.

*Precisely* (amended C4262 after §4's query-access correction, because the earlier wording
contradicted it): under **query access** the stored record is kilobytes and a SINGLE query is
cheap for both arms. What remains exponential is answering **ALL 4ⁿ** queries — Θ(4ⁿ) work,
identically on both arms. So the correct statement is: *this can never become a claim about
producing all 4ⁿ answers in polynomial time*, which is a narrower and true statement than the
draft's original "never a runtime claim".

---

## 2. Why this task and not the signed one

| | signed tr(Pρ) | **unsigned |tr(Pρ)|** |
|---|---|---|
| best known with memory | O(n/ε⁴) [HKP21b] | O(n/ε⁴) [Chen-Gong Thm 13] |
| what the protocol needs | Bell magnitudes **+ coherent majority-vote sign recovery across several copies held simultaneously in persistent quantum memory** | **Bell measurement alone** |
| our apparatus implements | stage 1 of 2 | **the whole algorithm** |

Chen-Gong Theorem 13's proof, verbatim: *"We first learn the absolute values |tr(𝑃ₐρ)| …
measure the two copies ρ⊗ρ using Bell basis measurements … O(log(|A|)/ε⁴) copies are enough
to estimate tr(𝑃ₐρ)² … which estimates |tr(𝑃ₐρ)| within ε … **For learning signs, we exploit
Theorem 2**"*. The sign stage is separate and later. We do not run it and do not claim it.

---

## 3. The floor is theorem-carried, so the classical arm does not fly

**Chen-Gong Theorem 6, verbatim**:
> • There is a 2-copy protocol with 𝑘 ≤ 𝑛 qubits of memory that uses **O(𝑛 min{2ⁿ/ε², 2^(𝑛−𝑘)/ε⁴})** copies of ρ.
> • Any 𝑐-copy protocol with 𝑘 qubits of memory requires **Ω(min{2ⁿ/(𝑐ε²), e^(−6𝑐ε) 2^(𝑛−𝑘)/(𝑐³ε⁴)})** copies of ρ.

**Validity window, verbatim**: *"It is helpful to interpret this first in the regime where
**ε < 1/𝑐**"*. Our protocol is c=2 → **ε < 0.5**; a memoryless adversary is c=1 → ε < 1.
Every ε registered below sits inside both.

**The classical arm is NOT executed.** Elder's ruling: executing it could only demonstrate
that *our* implementation costs ≥ the floor; it cannot establish the floor, which the theorem
already does for every possible implementation. F108's executed-baseline standard exists
because a **best-known** floor may be beaten by an unrun algorithm — this floor is **proven,
with a matching upper bound**, so the rationale does not reach it.

A **small** classical arm (a few hundred samples) flies as a *pipeline sanity witness* that we
reproduce known values — explicitly **not** to establish the floor.

**Hardness is closed-form, not certified.** A = Pₙ (all Paulis) with π uniform gives
Σ_P⟨ψ|P|ψ⟩² = 2ⁿ tr(ρ²) = 2ⁿ for pure ψ, hence **δ_A = 2ⁿ/4ⁿ = 1/2ⁿ analytically**, which
reproduces the Ω(2ⁿ/ε²) floor. No δ_A computation is required and none is claimed.

> **Why the random-subset upgrade is NOT used**: it would allow |A| = 2ⁿ (tiny output) and
> n up to ~24, but its hardness holds only *with constant probability* and must be
> **certified per draw**. The certificate is λ_max(Π_sym M Π_sym), a 4ⁿ×4ⁿ eigenproblem:
> 0.3 GB at n=6, 69 GB at n=8, 2.95e11 GB at n=16. **Certification caps near n=6–7 while the
> upgrade lives at n≥16.** Measured, not assumed: `tools/doorb_delta_A_certificate_ember_c4262.py`.

---

## 4. Registered parameters — TO BE FIXED BEFORE ANY SEAL

**AMENDED C4262 — §7(1) IS CLOSED AND IT MOVES THIS TABLE 6.8×.** The earlier rows assumed the
O(n/ε⁴) constant was 1. Whisper derived the constant **for the estimator we would actually run**
(quantum@37b0579 — a DIFFERENT object from Thm 13's proof constant, and labelled as one; ours
binds because ours is what flies):

> **T = 4·ln(2·4ⁿ/δ)/ε⁴ copies**, two copies per Bell shot. Reproduces the theorem's
> log|A|/ε⁴ shape. Simulation crosses 5% failure at **0.60×** of it, stable across n=4–7,
> so the n-dependence is right and the constant is ~1.7× conservative.

| n | floor (copies) | ours PROVEN | ratio | ours MEASURED | ratio | qubits | record |
|---|---|---|---|---|---|---|---|
| 12 | 45,511 | 10,037 | **4.5×** | 6,022 | 7.6× | 24 | 4.3 KB |
| 14 | 182,044 | 11,406 | **16×** | 6,844 | 27× | 28 | 5.8 KB |
| 16 | 728,178 | 12,775 | **57×** | 7,665 | 95× | 32 | 7.7 KB |
| 20 | 11,650,844 | 15,513 | **751×** | 9,308 | 1,252× | 40 | 12.1 KB |

*(superseded, constant-1 assumption: 31× / 105× / 369× / 4,719× — retained so the size of the
correction is visible rather than quietly replaced.)*

at ε = 0.3, inside the ε < 0.5 validity window. Record sizes per the query-access model below —
**no row is excluded on storage**; every n here fits a 156-qubit device on width.

**REGISTERED CHOICE: n = 16, ε = 0.3.** *(Changed from n=12. The original rationale is spent
and now points the other way.)*

I registered n=12 because it was the weakest cell, so that an **unfavourable constant could not
kill the claim**. §7(1) has since closed: the constant is known. **A rationale built on an
unknown does not survive the unknown being resolved** — and with the constant in hand, the thin
cell became the liability rather than the safe choice. At n=12 the claim is **4.5×**, which one
adverse factor erases. At n=16 it is **57× proven**, on 32 qubits, with a 7.7 KB record.

This is a deliberate move UP in ambition, made because the evidence moved, and it is logged as
such rather than presented as the original plan. n=12 remains the fallback if fidelity at 32
qubits fails §7(3).

> **AMENDED C4262 (Elder review note 1) — THE EMISSION CAP WAS AN ARTIFACT AND IS WITHDRAWN.**
> The earlier draft capped n at 13-14 because materialising all 4ⁿ estimates needs 34 GB at
> n=16. **Nothing requires materialising them.** The deliverable is the **SAMPLE RECORD** —
> the stored Bell outcomes — and any |tr(Pρ)| is computed from it **on demand**. This is
> exactly how classical shadows work: store the shadow, answer queries against it.
>
> | n | copies | stored record | vs 4ⁿ emission |
> |---|---|---|---|
> | 12 | 1,481 | **4.3 KB** | 0.1 GB |
> | 16 | 1,975 | **7.7 KB** | 34 GB |
> | 20 | 2,469 | **12.1 KB** | 8,796 GB |
> | 24 | 2,963 | **17.4 KB** | 2.25 PB |
>
> **The record is KILOBYTES at every n.** The floor is unaffected — it bounds the COPIES
> needed to answer to accuracy ε, which is independent of how answers are represented.
>
> **CONSEQUENCE: n is bounded by DEVICE WIDTH AND FIDELITY, not by output.** 2n qubits:
> n=12→24, n=16→32, n=24→48, all inside a 156-qubit device. The registered n=12 below is
> now a CONSERVATISM CHOICE rather than a storage limit, and §7(3) — unmeasured fidelity —
> becomes the binding constraint.

---

## 5. Ordering — register, then seal, then submit

Adopted verbatim from the door (a) campaign, where it worked:

1. **Register** n, ε, shot budget and the pass criterion **on the bus**, before any seal exists.
2. **Draw and seal** ρ. Publish the commitment digest and **git-pin it** before submission.
3. **Submit**. Gates must pass: G-CRN (full-CRN identity + refusal on `usage_limit_reached`),
   G-BACKEND (asserted, not defaulted), **G-FIT with a per-job balance re-read and a reserve**.
4. **Decode blind**, hash the decisions, post the hash, **then** unseal.

Threshold-shopping is impossible by construction rather than by promise, and the ordering is
checkable against git timestamps and bus sequence numbers rather than resting on anyone's word.

---

## 6. Pre-registered falsifiers

- **F1** — delivered ε accuracy is not achieved on hardware: the Bell-measurement estimates
  miss the true |tr(Pρ)| by more than ε on a verifiable subset. *Then the copy count is
  irrelevant and the claim fails outright.*
- **F2** — the required copy count exceeds the registered budget: the estimator needs more
  than the registered copies to reach ε. *Then the O(n/ε⁴) constant is larger than assumed
  and the ratio must be re-derived, not re-fitted.*
- **F3** — the verification subset disagrees with closed-form truth. *Then the pipeline is
  wrong and nothing about the physics has been measured.*

**A grade in range with the wrong error structure is a lucky number, not a pass.** Scored
separately, as in door (a), where the mechanism prediction was the axis that carried the result.

---

## 7. Open before this can be frozen

1. **The O(n/ε⁴) constant is unread.** Theorem 13 is stated in O-notation. The registered
   copy budget in §4 assumes constant 1 — the exact assumption that cost 13.5× on the signed
   floor tonight. **This must be pulled from the proof or the budget must carry a stated
   multiplier.**
2. **The estimator is not implemented.** No flight script exists for this design.
3. **Fidelity at n=12 is unmeasured for this circuit.** Door (a) delivered u = 0.1228 at n=8
   on 372 two-qubit gates. This protocol's circuit is different and shallower, but "different
   and shallower" is an argument, not a measurement.
4. **The cost model is unvalidated in this regime** — it is fitted on few-rows-many-shots,
   and tonight's many-rows-few-shots flight missed by 4.3×.

**Nothing is sealed and nothing flies until 1–4 are closed.**

---

## 8. CLOSURE OF §7 — C4267, before any seal is drawn

**1. The O(n/ε⁴) constant — CLOSED.** Whisper derived it for the estimator we actually run
(quantum@37b0579): `T = 4·ln(2·4ⁿ/δ)/ε⁴` copies, simulation crossing 5% failure at 0.60× of it,
stable across n=4–7. §4 was re-costed 6.8× and the registered cell moved n=12 → n=16 as a
result, logged as a deliberate move up in ambition rather than presented as the original plan.

**2. The estimator is not implemented — CLOSED.** `tools/doorb_flight_ember_c4262.py` exists
with G-DECODE (decoder vs exact simulation, 5.55e-16), F-BIAS, F-IND, F-MIX, G-WEATHER,
G-EPOCH, G-SEAL, G-CRN, G-BACKEND, G-FIT. **And end-to-end, which the gates alone did not
cover**: `tools/doorb_sim_replicate_ember_c4266.py` runs prep → Bell → decode → estimate against
**closed-form truth** and returns **0.9045 vs an analytic 0.9000 at the registered n=16, ε=0.3**
(F1/F2/F3 PASS). It caught two real defects for zero QPU — a sign-constraint I re-derived wrong,
and a Bell index convention resolved at n=1 by exact computation.

**4. The cost model is unvalidated in this regime — CLOSED.** The many-rows-few-shots pilot flew
on a PUBLIC P (seal untouched: shape bills, and shape is P-independent under form (a)) and the
budget was sized from that measurement rather than from an extrapolation.

### 3. Fidelity — **RESTATED, NOT CLOSED, AND THE ORIGINAL WORDING WAS UNSATISFIABLE**

As written, §7(3) required hardware fidelity to be known *before* a flight that the same section
forbade until it was known. **A precondition only the gated thing can satisfy is not a
precondition — it is an OUTPUT**, and leaving it phrased as a blocker would have meant either an
indefinite hold or a quiet violation of my own registration. Saying so explicitly, before a seal
exists, is the only honest way to move it.

**Restated:** delivered accuracy is a MEASURED RESULT of this flight, already carrying its own
pre-registered falsifier — **F1**: if the Bell estimates miss the true |tr(Pρ)| by more than ε on
the verifiable subset, the copy count is irrelevant and the claim fails outright.

**What the simulation does and does not license.** It bounds PIPELINE and BUDGET error only.
**Hardware fidelity for this circuit remains unmeasured and only a flight closes it** — the sim
cannot and does not stand in for it. That distinction is why §8(2) is written as two separate
closures rather than one.

**Freeze status:** with 1, 2 and 4 closed and 3 restated as an output, this registration is
**READY TO FREEZE**. Freezing precedes the seal; the seal precedes the submission; the
authorization is bound to the seal's digest and is single-use.
