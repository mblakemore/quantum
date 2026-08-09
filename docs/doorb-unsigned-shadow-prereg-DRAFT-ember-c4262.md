# Door (b) — unsigned Pauli shadow tomography: PRE-REGISTRATION (DRAFT)

**Author**: Ember (DC15E), C4262, 2026-08-09
**Status**: DRAFT. Not frozen. Nothing sealed, nothing flown.
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

**NOT CLAIMED**: a runtime advantage, a total-work advantage, or an advantage at any n
outside the range in §4. The output is exponentially large, so **no protocol for this task —
ours or anyone's — is efficient in total work**, and this can never become a runtime claim.

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

| n | floor (copies) | ours (copies) | ratio | output 4ⁿ | output size |
|---|---|---|---|---|---|
| 12 | 45,511 | 1,481 | **31×** | 16,777,216 | 134 MB |
| 13 | 91,022 | 1,605 | **57×** | 67,108,864 | 537 MB |
| 14 | 182,044 | 1,728 | **105×** | 268,435,456 | 2.1 GB |
| 16 | 728,178 | 1,975 | 369× | 4,294,967,296 | **34 GB — excluded** |

at ε = 0.3, inside the ε < 0.5 validity window.

**REGISTERED CHOICE: n = 12, ε = 0.3.** Rationale — 31× is the smallest ratio in the table and
therefore the most conservative claim; the output is 134 MB, which is handled without special
machinery; and 24 qubits (two copies of 12) is well inside device width. n=14 is the stretch
target if n=12 grades clean.

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
