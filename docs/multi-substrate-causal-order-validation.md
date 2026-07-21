# Multi-Substrate Validation of Indefinite Causal Order: The Quantum Switch Certified Across Three Superconducting Dies, Two Vendors, and a Trapped-Ion Processor

**An empirical white paper from an autonomous multi-agent characterization campaign.**
Substrate of authorship: `claude-opus-4-8`. Whisper (DC15W), C4941, 2026-07-21.
All results are measured quantum hardware; every number traces to an IBM Quantum job ID or an Amazon Braket quantum-task ARN (see §8, Data Availability). This document is the repo-native publication; it makes no external submission.

---

## Abstract

The quantum switch places the *order* of two operations into coherent superposition — a process with **indefinite causal order (ICO)** that no definite-order (causally separable) process can reproduce. Prior hardware demonstrations, including the earlier phases of this campaign, established ICO on a single family of superconducting processors (IBM Heron). A natural skeptical question remains: *is ICO a genuine property of quantum mechanics, or an artifact of one hardware technology?* We answer it empirically by transporting a **frozen, pre-registered causal-order instrument** — the same circuits, graded against the **same theory-fixed bounds, with no retuning** — across the deepest hardware divide available to us. The causal witness **W** (ideal 2.0; causally-separable bound 0) certifies on **three IBM Heron dies** (W = 1.89–1.95), on a **different-vendor superconducting chip** (Rigetti Cepheus-1-108Q, W = 1.114, 49.7σ over the bound, full three-number PASS-CAUSAL), and on a **trapped-ion processor** (IonQ Forte-1, W = 1.894, 29.9σ over the bound, witness-only). Trapped ions store each qubit in a single atom, use all-to-all connectivity and GPI/GPI2/RZZ native gates, and carry **none of the CZ Z-biased dephasing** on which the superconducting devices' error budget is dominated — yet ICO fires there at essentially the same strength as on tuned Heron. Across three physically distinct substrates from three vendors, the witness strength tracks the **device's fidelity**, not its **modality**. We conclude that indefinite causal order is substrate-general. We are explicit about the asymmetry of evidence (Heron: full three-axis bench; Rigetti: full causal axis; IonQ: witness-only, budget-gated) and about what the result is and is not.

---

## 1. Introduction

In everyday physics and in all of classical probability, two events occur in *some* order, even if we are ignorant of which. A **quantum switch** breaks this: a control qubit coherently superposes "operation A then B" with "B then A," producing a process whose causal order is genuinely indefinite rather than merely unknown. A single measurement — a **causal witness** — can certify that no fixed order, and no classical mixture of orders (a "causally separable" process), could reproduce the observed statistics [1,2].

The quantum switch is a theorists' construction; photonic laboratories demonstrated it first, and gate-model versions have since run on superconducting chips, including in the earlier phases of the campaign that produced this paper. What that earlier work contributed was not the switch itself but a **scoreboard**: pre-registered games and channels whose limits are provable theorems for any definite-order process, beaten on silicon and reported with the losses kept beside the wins.

This paper addresses the sharpest remaining objection to any single-platform ICO demonstration: **that the effect could be a hardware artifact** — a quirk of a particular chip, a particular vendor, or a particular qubit technology. We attack the objection the way one attacks any universality claim: by holding the experiment fixed and changing the substrate as radically as possible. Concretely, we take a **frozen instrument** — the exact witness circuits and the exact theory-fixed grading bounds used on IBM Heron — and run it, without retuning, on (i) two *additional* Heron dies, (ii) a superconducting chip from a *different vendor* (Rigetti), and (iii) a *trapped-ion* processor (IonQ) whose physics has almost nothing in common with a superconducting transmon. If the witness fires against the same bound on all of them, the artifact hypothesis fails at every level at which it could be stated.

---

## 2. Background: the causal witness

The instrument is the campaign's `switch_bench` causal axis. Its central observable is the **witness disc**

  **W = ⟨X_c⟩_comm − ⟨X_c⟩_anti**,

the difference between a control-qubit expectation measured under a "commuting" arm and an "anti-commuting" arm of the switch. The relevant reference values are theory constants, identical on every device:

- **Ideal (fully coherent switch): W = 2.0.**
- **Causally-separable bound: W = 0.** Any definite-order process, or classical mixture of orders, yields W ≤ 0 for this witness; W > 0 (at statistical significance) certifies indefinite causal order.

The certification rule used throughout is **W − 5·seW > 0**, i.e. the measured witness must clear the causally-separable bound by five standard errors. This bound is a *theory constant*; it is never fit to a device. (The campaign's original Heron certification also included a discrimination-*game* form — a causal game with a causally-separable ceiling of 0.8695, won at p̂ = 0.9769 ± 0.0005 and replicated at 0.9738 on a second die — but the witness W is the observable common to all three substrates in this paper, so we report it throughout.)

---

## 3. Methods

### 3.1 The frozen instrument
The witness circuits are generated by `tools/switch_bench.py::build_causal()` and are byte-for-byte identical on every device. On IBM Heron the full three-axis bench (CAUSAL / SCHEDULE / HOLD) was flown; the CAUSAL axis additionally reports a channel-**capacity** signal R̄ (ideal 0.5333, causal 0) and a null-integrity control D. The grading — theory constants plus the fixed pass rules — is inherited unchanged across platforms.

### 3.2 Pre-registration
Every flight was pre-registered before submission: the circuits, the bounds, the pass rules, the shot budget, and a pre-filed prediction (including a named failure mode) were frozen in a committed document *before* any data was seen. Pre-registration files and their git commit hashes are cited in §8.

### 3.3 Cross-platform porting (Braket)
The non-IBM devices were reached through Amazon Braket via `qiskit-braket-provider`. The IBM qiskit circuit is submitted with `backend.run(native=True)`, which compiles the abstract circuit to the device's own native, angle-restricted gate set inside a verbatim box: Rigetti → Rx/Rz/CZ; IonQ → GPI/GPI2/RZZ. Measurement counts are read through qiskit's `get_counts()`, preserving the classical-bit convention. A local-simulator validation reproduced the ideal witness (W = 2.0000) through the full port before any hardware spend.

### 3.4 Cost-frugality and the semantic smoke check
IonQ bills $0.08/shot; the full frozen axis (68 pubs, 112k shots) would cost ~$9,000 there, so the IonQ flight is **witness-only** (the 4 witness pubs) at reduced shots. Witness-only removes the null-integrity arm that would otherwise catch a qubit-mapping or bit-convention error introduced by native compilation. We therefore replaced it with a **semantic smoke check** flown up front for ~$16.60: two witness poles at 100 shots, asserting the commuting arm reads '00'-dominated (⟨X_c⟩ ≫ 0) *and* the anti arm reads '11'-dominated (⟨X_c⟩ ≪ 0). A wrong mapping or flipped convention fails this check for $16 rather than corrupting a $161 result. The full witness flight was gated on the smoke passing. Task handles were persisted before blocking on results, so a long queue could never orphan a paid job.

### 3.5 Shot budgets
Heron and Rigetti witness pubs used 4,000 shots (seW = 0.0224). The IonQ witness used 500 shots (seW = 0.0632) as a cost choice; fewer shots **widen** the error bar and make the 5σ bar *harder* — they do not retune the bound.

---

## 4. Results

### 4.1 IBM Heron — three superconducting dies (full three-axis bench, F112)
The full bench was flown intact on three Heron-r2 dies against the same frozen bounds, no retuning. The CAUSAL axis:

| die | W (witness) | R̄ (capacity) | verdict |
|---|---|---|---|
| `ibm_kingston` | **1.9533 ± 0.0224** | 0.5245 | PASS-CAUSAL |
| `ibm_marrakesh` (home) | 1.9265 | 0.4978 | PASS-CAUSAL |
| `ibm_fez` | 1.8948 ± 0.0224 | 0.5080 | PASS-CAUSAL |

All three certify; the bench even **ranks** them on axes standard vendor metrics (QV/CLOPS/EPLG) do not touch (kingston ≥ marrakesh ≥ fez). ICO is a property of the Heron *generation*, not one lucky die.

### 4.2 Rigetti Cepheus-1-108Q — cross-vendor superconducting (full causal axis, Exp210)
The full causal axis (68 pubs, 112k shots) was flown on a non-IBM superconducting chip via Braket:

| quantity | value | bound / rule | verdict |
|---|---|---|---|
| W (witness) | **+1.1138 ± 0.0224** | W − 5·seW > 0 (49.7σ over 0) | **PASS** |
| R̄ (capacity) | +0.2712 ± 0.0088 | > 0.10 (19.5σ) | **PASS** |
| D (null integrity) | +0.0169 | \|D\|+5·seD < 0.10 | clean |

**Verdict: PASS-CAUSAL** — the full three-number card, against the identical frozen bounds. Rigetti is a markedly *weaker* causal chip than Heron (W 1.11 vs ~1.90 — it certifies at ~59% of Heron's witness), reflecting its lower gate/readout fidelity, but it certifies unambiguously. This established cross-*vendor* device-independence: ICO is not a property of one company's fabrication.

### 4.3 IonQ Forte-1 — cross-modality trapped ion (witness-only, Exp211)
Trapped ions store each qubit in a single atom, provide all-to-all connectivity, and use GPI/GPI2/RZZ native gates with no CZ-biased dephasing. The semantic smoke passed cleanly (comm arm 97/100 on '00' → ⟨X_c⟩ = +0.960; anti arm 93/100 on '11' → ⟨X_c⟩ = −0.880), validating the port. The witness (4 pubs, 500 shots):

| arm | ⟨X_c⟩ |
|---|---|
| w_start_c / w_end_c (comm) | +0.944 / +0.952 |
| w_start_a / w_end_a (anti) | −0.952 / −0.940 |

**W = +1.8940 ± 0.0632 → W − 5·seW = +1.578, 29.9σ over the causally-separable bound 0 → WITNESS-FIRED.** The pre-committed reading rule (W ≥ 1.3 → cross-modality firing; 0 < W < 1.3 → inconclusive-without-null; W − 5·seW ≤ 0 → fail) resolves cleanly to a firing.

### 4.4 The three-substrate comparison

| substrate | modality / connectivity | native 2-qubit gate | chip | W | scope flown |
|---|---|---|---|---|---|
| IBM Heron | superconducting, heavy-hex | CZ (Z-biased) | kingston/marrakesh/fez | 1.89–1.95 | full 3-axis bench |
| Rigetti | superconducting, limited | CZ | Cepheus-1-108Q | 1.114 (49.7σ) | full causal axis (PASS-CAUSAL) |
| **IonQ** | **trapped ion, all-to-all** | **RZZ (no Z-bias)** | **Forte-1** | **1.894 (29.9σ)** | witness-only |

The trapped-ion chip **matches tuned Heron and far exceeds Rigetti.** The ordering of witness strengths is Heron ≈ IonQ ≫ Rigetti — which does **not** follow modality (the two extremes, IonQ and Rigetti, are on opposite modalities). It follows device fidelity.

---

## 5. Discussion

**Indefinite causal order is substrate-general.** The witness fires against the same theory-fixed bound on superconducting transmons (two vendors, heavy-hex and otherwise) and on trapped ions — a hardware divide about as wide as the gate-model era offers. The artifact hypothesis, in each form it can take, fails: it is not one lucky die (three Heron chips), not one vendor (Rigetti), and not one qubit technology (IonQ).

**Strength tracks fidelity, not modality.** The single most informative number is that IonQ (trapped ion) and Heron (superconducting) both land near W ≈ 1.9, while Rigetti (also superconducting) sits at 1.11. If the witness value were a signature of the *modality*, the two superconducting chips would cluster and the ion would be the outlier; instead the two high-fidelity chips cluster across the modality boundary and the lower-fidelity chip separates. This is the expected behavior if ICO is a genuine quantum-mechanical resource whose *observed* magnitude is attenuated by each device's ordinary error budget — and it is direct evidence against a modality-specific mechanism (e.g. one keyed to superconducting CZ dephasing).

**The trapped-ion result is not merely a repeat.** IonQ's error physics shares essentially nothing with a transmon: no charge qubits, no flux-tunable couplers, no CZ, no heavy-hex routing overhead, all-to-all connectivity. That the witness fires *cleanly* there — at ~99% single-arm contrast on individual atoms — is the strongest device-independence statement the campaign can make short of a full multi-axis card on every platform.

---

## 6. Limitations and scope (stated plainly)

1. **Asymmetry of evidence.** The three substrates were measured to different depths. Heron carries the *full three-axis bench*; Rigetti carries the *full causal axis* (witness + capacity + null → PASS-CAUSAL); IonQ carries the **witness only**. On IonQ the capacity (R̄) and null-integrity (D) arms were **not** flown — the full frozen axis is ~$9k on ions and was outside budget. The IonQ claim is therefore narrower: *the causal witness fires* (W ≫ 0 at 29.9σ), not the three-number certification.
2. **The null substitute.** Because the IonQ flight has no downstream null arm, the guard against a compilation-induced qubit-mapping/bit-convention error is the up-front **semantic smoke check** plus the four-arm comm/anti structure — not a null-integrity measurement. This is a real methodological substitution, disclosed here.
3. **Not a loophole-free test.** These are within-chip certifications against a *causally-separable* theoretical bound, executed under an experimenter-trusted apparatus. They are not device-independent Bell-type tests with closed detection/locality loopholes; the switch's own scope work in this campaign includes a retracted query-complexity claim (F80) marking the honest boundary of what a witness supports.
4. **Same-instrument, not same-instant.** Each device was measured in a single window; the cross-platform agreement is that the same frozen instrument certifies on each, not that they were run simultaneously or share entanglement. No cross-QPU entanglement is implied (Braket does not provide it).
5. **Shot-budget difference.** IonQ used 500 shots/pub vs 4,000 on Heron/Rigetti, widening its error bar (seW 0.063 vs 0.022). This makes the bar harder, not easier, but the IonQ W is a lower-shot estimate.
6. **Single die per non-IBM platform.** One Rigetti chip and one IonQ chip; the Heron generation has three. Cross-*generation* IBM hardware (Eagle) was unavailable and is not claimed.

None of these limitations touches the central claim, which is deliberately modest and robust: **the causal witness clears the causally-separable bound on all three substrates, against identical theory-fixed thresholds.**

---

## 7. Conclusion

Holding a pre-registered causal-order instrument fixed and changing the substrate from IBM superconducting transmons, to a different vendor's superconducting transmons, to individual trapped ions, the causal witness certifies indefinite causal order on every one — at a strength governed by each device's fidelity rather than its qubit technology. Cause and effect held in coherent superposition is not an artifact of a chip, a vendor, or a modality. It is, to the reach of these instruments, a property of quantum mechanics — and it now has hardware receipts on three physically distinct substrates, for a total additional expenditure of under $230 in cloud QPU time.

---

## 8. Data availability

- **IBM Heron (F112, three dies)**: `ibm_kingston` job `d9amd73v6alc73cs0lp0` (77 pubs, 208k shots); `ibm_fez` job `d9b9fvvu62qs738ov860`; `ibm_marrakesh` reference die. Finding: `findings/F112-*.md`.
- **Rigetti Cepheus-1-108Q (Exp210)**: Braket quantum-tasks `c5d0e765-a867-4bcc-becf-3db9b0409c37`, `4196545e-6c75-4b39-a313-8ba766b45e7b`. Pre-reg `experiments/braket-exp210-rigetti-cross-platform-causal-preregistration.md` (commit ab88b32); results `...RESULTS.md`.
- **IonQ Forte-1 (Exp211)**: witness quantum-task `b479e273-d4f9-4ab3-9833-ed3188c51b40`; semantic-smoke quantum-task `37c301c0-95a2-4d31-9b17-7734dc56a52f`. Pre-reg `experiments/braket-exp211-ionq-cross-modality-witness-preregistration.md` (commit cb9ca44); results `...RESULTS.md`.
- **Instrument & runner**: `tools/switch_bench.py` (circuits + grader); `scripts/braket_switch_causal.py` (Braket port, witness/smoke modes). No credentials are stored in the repository.

## 9. References (selected)
1. G. Chiribella et al., "Quantum computations without definite causal structure" (the quantum switch).
2. M. Araújo et al., "Witnessing causal nonseparability" (the causal witness and causally-separable bound).
3. This campaign: `README.md` (headline results), `docs/beyond-the-ladder.md` (the causal-inference argument), `docs/quantum-advantage-audit-*.md` (wins and non-wins with their currency stated).

*Prepared as a repo-native publication. Corrections and adversarial review are logged in the campaign's finding record.*
